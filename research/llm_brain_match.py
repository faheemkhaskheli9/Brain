"""LLM-brain match: shared computation or word statistics? (issue #89)

Question. GPT-2 activations predict fMRI responses to spoken stories. Is that because GPT-2 computes
something the brain also computes, or would word rate, word frequency and n-gram surprisal (cheap word
statistics) predict the same variance?

Data. Narratives (Nastase et al. 2021, OpenNeuro ds002345), AFNI-cleaned, unsmoothed data on the
fsaverage6 surface (left hemisphere), from the dataset's public S3 mirror (fcp-indi). Ten stories, two
listeners each by default (--subjects 5 for five). Each scan is cropped to the story (events.tsv) and
averaged into the 74 Destrieux parcels (FreeSurfer aparc.a2009s). Listeners are aligned to each other and
each story is shifted so that the lag from word count to auditory cortex is 3 TRs (events.tsv timing was
2-3 TRs off for three stories; see main), then averaged into one group time series per story.

Features, summed over the words in each TR (1.5 s), z-scored per story, FIR delays of 1-6 TRs (1.5-9 s):
  b  word statistics: word count, unigram surprisal (-log2 word frequency) and trigram surprisal, both from
     a Dirichlet-smoothed trigram model counted on WikiText-103 (85.9M word tokens after normalisation)
  a  GPT-2 small (trained) layer 9, last sub-word token of each word, 512-token sliding context
  c  the same network untrained (Hugging Face random init, seed 0), layer 9
  s  static GPT-2 input embeddings (no context, no position)
  g  GPT-2's own surprisal of each word (exploratory: next-word predictability as a single number)
Embedding bands are cut to their top 128 principal components, fitted on the training stories only.

Encoding. Ridge regression, leave-one-story-out (no TR of a test story is ever in training), alpha per
parcel chosen by an inner 3-fold split over the training stories. In joint models the word-statistics
columns are unpenalised and the embedding band is ridge-penalised (Frisch-Waugh). Score = held-out Pearson r
per parcel and story. Unique variance of a over b = r2(b+a) - r2(b). Statistics run across the 10 held-out
stories (exact sign-flip test, bootstrap 95% CI); parcels are corrected with Benjamini-Hochberg.
Control: GPT-2 features circularly shifted by half a story (same statistics, wrong timing).

Run:  python research/llm_brain_match.py --subjects 5 # main result (downloads ~5.2 GB once, then caches)
      python research/llm_brain_match.py              # 2 listeners per story (~2.1 GB)
      python research/llm_brain_match.py --no-align   # keep events.tsv timing (sensitivity check)
      python research/llm_brain_match.py --quick      # 3 stories x 1 listener, smoke test (~10-15 min
                                                      # fresh, for the n-gram counts; ~15 s once cached)
      python research/llm_brain_match.py --download-only
Data go to ~/.cache/brain-kb/narratives/ (override with --data-dir); only parcel averages are kept, plus
WikiText-103 (314 MB), GPT-2 features (354 MB) and Hugging Face's GPT-2 weights (548 MB, its own cache).
Needs numpy, nibabel, pyarrow, torch, transformers. Runtime on a busy 20-core CPU: 1-1.5 h the first time
(download speed decides; GPT-2 features ~10 min, n-gram counts ~5-10 min), ~20 min per later run.
Result: function/language-and-llms.md.
"""
import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")   # BLAS oversubscription made eigh 100x slower on a busy 20-core machine

import argparse
import csv
import io
import json
import re
import shutil
import threading
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

TR = 1.5
STORIES = ["pieman", "milkyway", "lucy", "bronx", "notthefallintact", "prettymouth", "black", "forgot",
           "merlin", "sherlock"]          # quick mode uses the first three (smallest files)
GENTLE = {"milkyway": "milkywayoriginal"}  # milkyway has three versions; only "original" listeners are used
S3 = "https://s3.amazonaws.com/fcp-indi/data/Projects/narratives/"
LIST = "https://s3.amazonaws.com/fcp-indi?list-type=2&prefix=data/Projects/narratives/"
OPENNEURO = "https://s3.amazonaws.com/openneuro.org/ds002345/"
EXCLUDE = "https://datasets.datalad.org/labs/hasson/narratives/code/scan_exclude.json"
WIKI = "https://huggingface.co/datasets/Salesforce/wikitext/resolve/main/wikitext-103-raw-v1/"
WIKI_TRAIN = ["train-00000-of-00002.parquet", "train-00001-of-00002.parquet"]
WIKI_VALID = "validation-00000-of-00001.parquet"
# Language parcels chosen before seeing results: Destrieux regions covering Fedorenko's left IFG, IFGorb,
# anterior/posterior temporal and angular gyrus parcels. Controls: auditory cortex and early visual cortex.
LANG = ["G_front_inf-Opercular", "G_front_inf-Triangul", "G_front_inf-Orbital", "G_temp_sup-Lateral",
        "S_temporal_sup", "G_temporal_middle", "Pole_temporal", "G_temp_sup-Plan_tempo", "G_pariet_inf-Angular"]
AUD = ["G_temp_sup-G_T_transv", "S_temporal_transverse"]
VIS = ["S_calcarine", "G_cuneus", "Pole_occipital"]
LAYER = 9           # pre-registered: best GPT-2 small layer in Antonello & Huth 2024 (held-out stories)
DELAYS = (1, 2, 3, 4, 5, 6)   # 1.5-9 s: the haemodynamic peak (~4-6 s) with a margin either side
ALPHAS = np.logspace(0, 6, 13)
REF = 3             # TRs (4.5 s): word count -> auditory cortex peak lag every listener is aligned to (the median)
LOCK = threading.Lock()


# ---------------------------------------------------------------- download and parcellate
def get(url, path=None, tries=8):
    """Bytes of url, or save it to path (atomic, resumes a partial download). Retries on network errors."""
    part = Path(f"{path}.part")
    for i in range(tries):
        try:
            have = part.stat().st_size if path is not None and part.exists() else 0
            hdr = {"User-Agent": "brain-kb research script (issue #89)"} | ({"Range": f"bytes={have}-"} if have else {})
            with urllib.request.urlopen(urllib.request.Request(url, headers=hdr), timeout=120) as r:
                if path is None:
                    return r.read()
                with open(part, "ab" if have and r.status == 206 else "wb") as f:
                    shutil.copyfileobj(r, f, 1 << 20)
                part.replace(path)
                return path
        except OSError:
            if i == tries - 1:
                raise
            time.sleep(10 * (i + 1))


def cached(data_dir, rel, url):
    p = data_dir / rel
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        get(url, p)
    return p


def pick_scans(data_dir, stories, n_sub):
    """First n_sub listeners per story (participants.tsv order) with a single scan of it that the dataset
    authors did not exclude. Cached in scans_<n>.json."""
    path = data_dir / f"scans_{n_sub}.json"
    picked = json.loads(path.read_text()) if path.exists() else {}
    rows = list(csv.DictReader(open(cached(data_dir, "participants.tsv", OPENNEURO + "participants.tsv"),
                                    encoding="utf-8"), delimiter="\t"))
    bad = json.loads(cached(data_dir, "scan_exclude.json", EXCLUDE).read_text())
    for story in stories:
        if story in picked:
            continue
        excl = {s for v in bad.get(story, {}).values() for s in v}
        picked[story] = []
        for r in rows:
            tasks, conds = r["task"].split(","), r["condition"].split(",")
            if story not in tasks or (story == "milkyway" and conds[tasks.index(story)] != "original"):
                continue
            sub = r["participant_id"]
            xml = get(f"{LIST}derivatives/afni-nosmooth/{sub}/func/{sub}_task-{story}_").decode()
            keys = sorted(k for k in re.findall(r"<Key>([^<]+)</Key>", xml) if k.endswith("hemi-L_desc-clean.func.gii"))
            keys = [k for k in keys if "_run-" not in k]   # run-1 of the two-run Pie Man listeners is not
            # time-locked to other listeners (EAC ISC -0.07 vs 0.41 for run-2, sub-002 vs sub-003): skip them
            scan = keys[0].rsplit("/", 1)[1].split("_space-")[0] if keys else None
            if scan and scan not in excl:
                picked[story].append([sub, scan, keys[0].split("narratives/", 1)[1]])
            if len(picked[story]) == n_sub:
                break
        path.write_text(json.dumps(picked, indent=1))
    return {s: picked[s] for s in stories}


def parcellate(data_dir, sub, scan, key, annot):
    """Download one scan, crop it to the story, average into parcels, delete the surface file."""
    out = data_dir / "parcels" / f"{scan}.npz"
    if out.exists():
        return out
    ev = list(csv.DictReader(io.StringIO(get(f"{OPENNEURO}{sub}/func/{scan}_events.tsv").decode()), delimiter="\t"))
    assert json.loads(get(f"{OPENNEURO}{sub}/func/{scan}_bold.json"))["RepetitionTime"] == TR
    story = next(r for r in ev if r["trial_type"] == "story")
    start, n = round(float(story["onset"]) / TR), round(float(story["duration"]) / TR)
    offset = float(ev[0]["onset"]) - start * TR   # audio starts with the first event; seconds vs first kept TR
    gii = data_dir / "tmp" / Path(key).name
    gii.parent.mkdir(exist_ok=True)
    get(S3 + key, gii)
    import nibabel as nib
    labels, onehot = annot
    with LOCK:   # one surface file in memory at a time
        x = np.stack([d.data for d in nib.load(gii).darrays]).astype(np.float32)   # (TRs, vertices)
        assert x.shape[0] >= start + n, (scan, x.shape, start, n)
        y = x[start:start + n] @ onehot / onehot.sum(0)
    out.parent.mkdir(exist_ok=True)
    np.savez(out, y=y.astype(np.float32), offset=offset)
    gii.unlink()
    print(f"  {scan}: {n} TRs, audio offset {offset:+.2f} s", flush=True)
    return out


def load_annot(data_dir):
    import nibabel as nib
    p = cached(data_dir, "lh.aparc.a2009s.annot", S3 + "derivatives/freesurfer/fsaverage6/label/lh.aparc.a2009s.annot")
    lab, _, names = nib.freesurfer.read_annot(p)
    names = [n.decode() for n in names]
    keep = [i for i, n in enumerate(names) if n not in ("Unknown", "Medial_wall") and (lab == i).any()]
    onehot = (lab[:, None] == np.array(keep)[None]).astype(np.float32)
    return [names[i] for i in keep], (lab, onehot)


def download(data_dir, stories, n_sub, workers=3):
    names, annot = load_annot(data_dir)
    scans = pick_scans(data_dir, stories, n_sub)
    for s in STORIES:   # all transcripts (small): the n-gram counts use every story's words
        cached(data_dir, f"gentle/{s}.json", f"{S3}stimuli/gentle/{GENTLE.get(s, s)}/align.json")
    jobs = [(sub, scan, key) for s in stories for sub, scan, key in scans[s]]
    print(f"{len(jobs)} scans to fetch or reuse", flush=True)
    with ThreadPoolExecutor(workers) as ex:
        list(ex.map(lambda j: parcellate(data_dir, *j, annot), jobs))
    return names, scans


# ---------------------------------------------------------------- words and word statistics
def story_words(data_dir, story):
    """Transcript (typographic quotes and dashes made ASCII, one character each so the offsets still hold)
    and per-word (start offset, end offset, onset in s within the audio file)."""
    d = json.loads((data_dir / f"gentle/{story}.json").read_text(encoding="utf-8"))
    text = d["transcript"].translate({0x2018: "'", 0x2019: "'", 0x201C: '"', 0x201D: '"', 0x2013: "-", 0x2014: "-"})
    w = d["words"]
    t = np.array([x.get("start", np.nan) for x in w], float)
    ok = ~np.isnan(t)
    t[~ok] = np.interp(np.flatnonzero(~ok), np.flatnonzero(ok), t[ok])   # the few words gentle did not align
    return text, [(x["startOffset"], x["endOffset"]) for x in w], t


def norm(text):
    """Lower-case word tokens, matching WikiText-103 to the story transcripts."""
    text = re.sub(r" @(.)@ ", r"\1", text.lower().replace(chr(0x2019), "'"))   # wikitext: "a @-@ b", "1 @,@ 000"
    text = re.sub(r"\s'(?=[a-z])", "'", text)                                # wikitext: "don 't" -> "don't"
    return re.findall(r"[a-z0-9]+(?:'[a-z]+)*", text)


def ngram_surprisal(data_dir, pieces_per_story):
    """Unigram and trigram surprisal (bits) for each word piece. Trigram -> bigram -> unigram Dirichlet
    smoothing, P(w|h) = (c(h,w) + mu P(w|h')) / (c(h) + mu), one mu per order chosen on WikiText-103
    validation. Only the n-grams the stories and validation text need are counted (cached: ngram_counts.npz)."""
    import pyarrow.parquet as pq
    valid = [t for line in pq.read_table(cached(data_dir, f"wikitext/{WIKI_VALID}", WIKI + WIKI_VALID))["text"].to_pylist()
             for t in norm(line)]
    streams = [[p for w in s for p in w] for s in pieces_per_story] + [valid]
    vocab = {w: i + 1 for i, w in enumerate(sorted({p for s in streams for p in s}))}   # 0 = any other word
    V = len(vocab) + 1
    ids = [np.array([vocab[p] for p in s], np.int64) for s in streams]
    need2 = np.unique(np.concatenate([a[:-1] * V + a[1:] for a in ids]))
    need3 = np.unique(np.concatenate([(a[:-2] * V + a[1:-1]) * V + a[2:] for a in ids]))
    path = data_dir / "ngram_counts.npz"
    if path.exists() and len(np.load(path)["c2"]) == len(need2):
        c1, c2, c3 = (np.load(path)[k] for k in ("c1", "c2", "c3"))
    else:
        c1, c2, c3 = np.zeros(V), np.zeros(len(need2)), np.zeros(len(need3))
        for f in WIKI_TRAIN:
            pf = pq.ParquetFile(cached(data_dir, f"wikitext/{f}", WIKI + f))
            for batch in pf.iter_batches(batch_size=20000, columns=["text"]):
                a = np.array([vocab.get(t, 0) for line in batch.column(0).to_pylist() for t in norm(line)], np.int64)
                c1 += np.bincount(a, minlength=V)
                for codes, need, c in ((a[:-1] * V + a[1:], need2, c2), ((a[:-2] * V + a[1:-1]) * V + a[2:], need3, c3)):
                    codes = codes[np.isin(codes, need)]
                    u, k = np.unique(codes, return_counts=True)
                    c[np.searchsorted(need, u)] += k
        np.savez(path, c1=c1, c2=c2, c3=c3)
    print(f"  WikiText-103: {int(c1.sum()):,} tokens counted", flush=True)
    p1 = (c1 + 1) / (c1.sum() + V)

    def surprisal(a, mu):
        s = -np.log2(p1[a])
        if len(a) > 1:
            b2 = np.searchsorted(need2, a[:-1] * V + a[1:])
            p2 = (c2[b2] + mu[0] * p1[a[1:]]) / (c1[a[:-1]] + mu[0])
            s[1:] = -np.log2(p2)
            if len(a) > 2:
                b3 = np.searchsorted(need3, (a[:-2] * V + a[1:-1]) * V + a[2:])
                ctx = c2[np.searchsorted(need2, a[:-2] * V + a[1:-1])]
                s[2:] = -np.log2((c3[b3] + mu[1] * p2[1:]) / (ctx + mu[1]))
        return s

    steps = 10.0 ** np.arange(0, 7.5, 0.5)
    grid = [(m2, m3) for m2 in steps for m3 in steps]
    bits = [surprisal(ids[-1], m).mean() for m in grid]
    mu = grid[int(np.argmin(bits))]
    assert steps[0] < min(mu) and max(mu) < steps[-1], f"mu {mu} on the edge of the grid"
    print(f"  bigram/trigram mu = {mu[0]:.0f}/{mu[1]:.0f}: validation {min(bits):.2f} bits/word "
          f"(perplexity {2 ** min(bits):.0f}; unigram {-np.log2(p1[ids[-1]]).mean():.2f} bits)", flush=True)
    return [(-np.log2(p1[a]), surprisal(a, mu)) for a in ids[:-1]]


# ---------------------------------------------------------------- GPT-2 features
def gpt2_words(text, spans, model, tok, want_logits):
    """Per word: hidden states of all 13 layers at its last token, mean input embedding of its tokens, and
    (trained model) its surprisal in bits. 512-token windows, stride 256: each kept token sees >= 256 tokens."""
    import torch
    enc = tok(text, return_offsets_mapping=True)
    ids_np = np.array(enc["input_ids"])
    ids = torch.from_numpy(ids_np)
    starts, ends = np.array(enc["offset_mapping"]).T
    first = np.searchsorted(ends, [s for s, _ in spans], side="right")
    last = np.searchsorted(starts, [e for _, e in spans], side="left") - 1
    n, nw = len(ids), len(spans)
    owner = np.full(n, -1)
    owner[last] = np.arange(nw)
    H = np.zeros((nw, 13, 768), np.float32)
    tok_bits = np.full(n, np.nan)
    st = 0
    while True:
        en, keep = min(st + 512, n), (0 if st == 0 else st + 256)
        with torch.no_grad():
            out = model(ids[st:en][None], output_hidden_states=True)
        hs = torch.stack(out.hidden_states)[:, 0].numpy()            # (13, L, 768)
        pos = np.arange(keep, en)
        sel = pos[owner[pos] >= 0]
        H[owner[sel]] = hs[:, sel - st].transpose(1, 0, 2)
        if want_logits:
            lp = torch.log_softmax(out.logits[0, :-1], -1)            # predicts tokens st+1 .. en-1
            p = torch.from_numpy(pos[pos > st])
            tok_bits[p.numpy()] = -lp[p - st - 1, ids[p]].numpy() / np.log(2)
        if en == n:
            break
        st += 256
    wte = model.transformer.wte.weight.detach().numpy()
    static = np.stack([wte[ids_np[f:l + 1]].mean(0) for f, l in zip(first, last)])
    bits = np.array([np.nansum(tok_bits[f:l + 1]) for f, l in zip(first, last)])
    bits[np.isnan(tok_bits[first])] = np.nanmean(bits)               # the very first word has no context
    return H, static, bits


def bin_tr(values, onsets, n_tr):
    """Sum word-level values into TRs by word onset."""
    idx = np.floor(onsets / TR).astype(int)
    ok = (idx >= 0) & (idx < n_tr)
    out = np.zeros((n_tr,) + values.shape[1:], np.float32)
    np.add.at(out, idx[ok], values[ok])
    return out


def features(data_dir, stories, offsets, n_trs):
    """TR-level features per story. GPT-2 features are cached in features/<story>.npz (checked against the
    word onsets); the word statistics are rebuilt each run from the cached n-gram counts."""
    words = {s: story_words(data_dir, s) for s in STORIES}   # all ten, so the counts never depend on --quick
    pieces = [[norm(text[a:b]) for a, b in spans] for text, spans, _ in words.values()]
    out = {}
    for s, (uni, tri), pc in zip(STORIES, ngram_surprisal(data_dir, pieces), pieces):
        if s not in stories:
            continue
        word_of = np.repeat(np.arange(len(pc)), [len(p) for p in pc])   # pieces -> word ("1,000" has two)
        t = words[s][2] + offsets[s]
        ws = np.column_stack([np.ones(len(pc))] + [np.bincount(word_of, v, len(pc)) for v in (uni, tri)])
        ws[[len(p) == 0 for p in pc]] = 0      # words with no letters (e.g. "--") count for nothing
        out[s] = {"b": bin_tr(ws, t, n_trs[s]), "onsets": t}
        lost = int(((t < 0) | (t >= n_trs[s] * TR)).sum())
        if lost:
            print(f"  {s}: {lost} of {len(t)} words fall outside the scan window (dropped)")
        f = data_dir / f"features/{s}.npz"
        if f.exists():
            old = dict(np.load(f))
            if np.allclose(old["onsets"], t) and len(old["a"]) == n_trs[s]:
                out[s].update({k: old[k] for k in "acsg"})
    todo = [s for s in stories if "a" not in out[s]]
    if todo:
        import torch
        from transformers import GPT2Config, GPT2LMHeadModel, GPT2TokenizerFast
        torch.set_num_threads(4)
        tok = GPT2TokenizerFast.from_pretrained("gpt2")
        for name in ("trained", "untrained"):
            if name == "trained":
                model = GPT2LMHeadModel.from_pretrained("gpt2")
            else:
                torch.manual_seed(0)
                model = GPT2LMHeadModel(GPT2Config())
            model.eval()
            for s in todo:
                text, spans, _ = words[s]
                H, static, bits = gpt2_words(text, spans, model, tok, name == "trained")
                t = out[s]["onsets"]
                if name == "trained":
                    out[s].update(a=bin_tr(H, t, n_trs[s]), s=bin_tr(static, t, n_trs[s]), g=bin_tr(bits[:, None], t, n_trs[s]))
                else:
                    out[s]["c"] = bin_tr(H, t, n_trs[s])
                print(f"  {name} GPT-2: {s} ({len(spans)} words)", flush=True)
            del model
        for s in todo:
            (data_dir / "features").mkdir(exist_ok=True)
            np.savez(data_dir / f"features/{s}.npz", **{k: out[s][k] for k in ("onsets", "a", "c", "s", "g")})
    return out


# ---------------------------------------------------------------- encoding models
def z(x):
    sd = x.std(0)
    return (x - x.mean(0)) / np.where(sd > 0, sd, 1)


def delay(x):
    return np.hstack([np.vstack([np.zeros((d, x.shape[1]), x.dtype), x[:-d]]) for d in DELAYS])


def corr(a, b):
    a, b = z(a), z(b)
    return (a * b).mean(0)


def peak_lag(x, y, lags):
    """Lag (TRs, y after x) at which y correlates best with x."""
    n = len(x)
    c = [np.corrcoef(x[:n - L], y[L:])[0, 1] if L >= 0 else np.corrcoef(x[-L:], y[:n + L])[0, 1] for L in lags]
    return int(lags[int(np.argmax(c))])


def shift(y, d):
    """Move y earlier by d TRs (later if d < 0); the vacated TRs are 0 (the mean)."""
    out = np.zeros_like(y)
    if d >= 0:
        out[:len(y) - d] = y[d:]
    else:
        out[-d:] = y[:d]
    return out


def fit_predict(Btr, Ptr, Ytr, Bte, Pte):
    """Test predictions (alphas, TRs, parcels). B columns unpenalised, P columns ridge (Frisch-Waugh)."""
    base = 0
    if Btr is not None:
        coef = np.linalg.lstsq(Btr, np.hstack([Ytr] + ([Ptr] if Ptr is not None else [])), rcond=None)[0]
        cy, cp = coef[:, :Ytr.shape[1]], coef[:, Ytr.shape[1]:]
        base = Bte @ cy
        if Ptr is None:
            return base[None]
        Ytr, Ptr, Pte = Ytr - Btr @ cy, Ptr - Btr @ cp, Pte - Bte @ cp
    lam, V = np.linalg.eigh(Ptr.T @ Ptr)   # ridge via the Gram matrix: 4x faster than an SVD here
    vxy = V.T @ (Ptr.T @ Ytr)
    PV = Pte @ V
    return np.stack([base + PV @ (vxy / (lam + a)[:, None]) for a in ALPHAS])


def pcs(F, train, k, shift=False):
    """Band -> per-story delayed top-k PC scores, PCA fitted on the training stories."""
    zs = [z(f) for f in F]
    X = np.vstack([zs[i] for i in train])
    w, v = np.linalg.eigh(X.T @ X)
    v = v[:, ::-1][:, :k]
    out = [z(x @ v) for x in zs]
    if shift:
        out = [np.roll(x, len(x) // 2, 0) for x in out]
    return [delay(x) for x in out]


def evaluate(spec, feats, Y, k):
    """Held-out r (stories x parcels) for one model. spec = (base bands, penalised bands)."""
    base_keys, pen_keys = spec
    n = len(Y)
    r = np.zeros((n, Y[0].shape[1]))
    for t in range(n):
        train = [i for i in range(n) if i != t]
        B = [np.hstack([delay(z(feats[key][i])) for key in base_keys]) for i in range(n)] if base_keys else None
        P = None
        if pen_keys:
            bands = []
            for key in pen_keys:
                band, shift = key.rstrip("~"), key.endswith("~")
                bands.append(pcs([feats[band][i] for i in range(n)], train, k, shift))
            P = [np.hstack([b[i] for b in bands]) for i in range(n)]
        cat = lambda L, idx: None if L is None else np.vstack([L[i] for i in idx])
        if P is not None:
            score = np.zeros((len(ALPHAS), Y[0].shape[1]))
            for g in [train[j::3] for j in range(min(3, len(train)))]:
                itr = [i for i in train if i not in g]
                pred = fit_predict(cat(B, itr), cat(P, itr), cat(Y, itr), cat(B, g), cat(P, g))
                score += np.stack([corr(p, cat(Y, g)) for p in pred])
            best = score.argmax(0)
        else:
            best = np.zeros(Y[0].shape[1], int)
        pred = fit_predict(cat(B, train), cat(P, train), cat(Y, train), cat(B, [t]), cat(P, [t]))
        pred = pred[best, :, np.arange(len(best))].T
        r[t] = corr(pred, Y[t])
    return r


def signflip(d):
    """Exact two-sided sign-flip p for mean(d) != 0 (n <= 16)."""
    n = len(d)
    signs = 1 - 2 * ((np.arange(2 ** n)[:, None] >> np.arange(n)) & 1)
    null = np.abs((signs * d).mean(1))
    return float((null >= abs(d.mean()) - 1e-12).mean())


def boot(d, rng):
    m = d[rng.integers(0, len(d), (10000, len(d)))].mean(1)
    return np.percentile(m, [2.5, 97.5])


def bh(p):
    """Benjamini-Hochberg: which p values survive at q = 0.05."""
    p = np.asarray(p)
    order = np.argsort(p)
    ok = p[order] <= 0.05 * np.arange(1, len(p) + 1) / len(p)
    cut = np.flatnonzero(ok).max() + 1 if ok.any() else 0
    out = np.zeros(len(p), bool)
    out[order[:cut]] = True
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="3 stories x 1 listener, layer 9 only")
    ap.add_argument("--subjects", type=int, default=2, help="listeners per story")
    ap.add_argument("--pcs", type=int, default=128, help="principal components per embedding band")
    ap.add_argument("--download-only", action="store_true")
    ap.add_argument("--no-align", action="store_true", help="use events.tsv timing as is (no per-listener shift)")
    ap.add_argument("--data-dir", type=Path, default=Path.home() / ".cache" / "brain-kb" / "narratives")
    a = ap.parse_args()
    t0 = time.time()
    stories, n_sub, k = (STORIES[:3], 1, 32) if a.quick else (STORIES, a.subjects, a.pcs)
    a.data_dir.mkdir(parents=True, exist_ok=True)
    names, scans = download(a.data_dir, stories, n_sub)
    print(f"download/parcellation done in {time.time() - t0:.0f} s", flush=True)
    if a.download_only:
        return

    runs, offsets = {}, {}
    for s in stories:
        runs[s] = [np.load(a.data_dir / f"parcels/{scan}.npz") for _, scan, _ in scans[s]]
        offs = [float(r["offset"]) for r in runs[s]]
        assert max(offs) - min(offs) < 0.75, (s, offs)
        offsets[s] = float(np.mean(offs))
    feats = features(a.data_dir, stories, offsets, {s: len(runs[s][0]["y"]) for s in stories})

    # Timing. With events.tsv timing the word count -> auditory cortex peak lag was 5-6 TRs for milkyway and
    # prettymouth and -2 to 1 for lucy in all five listeners (2-4 for the other stories' group means), and two
    # Pie Man listeners ran 2-3 TRs ahead of the other three. So, with 3+ listeners, each is first shifted by its auditory-cortex
    # lag behind the mean of the others; then the story's group mean is shifted so its word count -> auditory
    # peak lag is REF. Only auditory parcels and word count are used, every feature set gets the same timing,
    # and it can only help the word-statistics baseline. --no-align keeps events.tsv timing.
    aud = [names.index(p) for p in AUD]
    Y, ceil = [], []
    for s in stories:
        ys = [z(r["y"]) for r in runs[s]]
        if not a.no_align:
            loo = [0] * len(ys)
            if len(ys) >= 3:
                loo = [peak_lag(np.mean([v for j, v in enumerate(ys) if j != i], 0)[:, aud].mean(1),
                                y[:, aud].mean(1), np.arange(-4, 5)) for i, y in enumerate(ys)]
                ys = [shift(y, L) for y, L in zip(ys, loo)]
            G = peak_lag(feats[s]["b"][:, 0], z(np.mean(ys, 0))[:, aud].mean(1), np.arange(-3, 10))
            ys = [shift(y, G - REF) for y in ys]
            print(f"  {s}: listener lags {loo}, word count -> auditory peak lag {G:+d} TR, moved to {REF}")
        Y.append(z(np.mean(ys, 0)))   # z-score each listener, average, z-score again
        if len(ys) >= 2:   # split-half reliability (alternate listeners), Spearman-Brown (approximate for odd n)
            rho = corr(np.mean(ys[0::2], 0), np.mean(ys[1::2], 0))
            ceil.append(np.sqrt(np.clip(2 * rho / (1 + rho), 0, None)))
            print(f"  {s}: split-half r, auditory {rho[aud].mean():.2f}, "
                  f"language {rho[[names.index(p) for p in LANG]].mean():.2f}")
    F = {key: [feats[s][key][:, LAYER] if key in "ac" else feats[s][key] for s in stories] for key in "abcsg"}
    layers = [] if a.quick else range(13)
    for L in layers:
        F[f"a{L}"] = [feats[s]["a"][:, L] for s in stories]
        F[f"c{L}"] = [feats[s]["c"][:, L] for s in stories]

    models = {"b": (["b"], []), "a": ([], ["a"]), "c": ([], ["c"]), "s": ([], ["s"]),
              "b+a": (["b"], ["a"]), "b+c": (["b"], ["c"]), "b+s": (["b"], ["s"]), "b+s+a": (["b"], ["s", "a"]),
              "b+g": (["b", "g"], []), "b+g+a": (["b", "g"], ["a"]), "b+a~": (["b"], ["a~"])}
    models.update({f"a{L}": ([], [f"a{L}"]) for L in layers})
    models.update({f"c{L}": ([], [f"c{L}"]) for L in layers})
    R = {}
    for m, spec in models.items():
        R[m] = evaluate(spec, F, Y, k)
        print(f"  fitted {m:6s} ({time.time() - t0:.0f} s)", flush=True)

    idx = {grp: [names.index(p) for p in ps] for grp, ps in (("language", LANG), ("auditory", AUD), ("visual", VIS))}
    rng = np.random.default_rng(0)
    print(f"\n{len(stories)} stories, {n_sub} listener(s) each, {sum(len(y) for y in Y)} TRs, "
          f"{len(names)} left-hemisphere parcels, {k} PCs per band, layer {LAYER}")
    if ceil:
        c = np.median(ceil, 0)
        print("noise ceiling (median over stories, r): " + ", ".join(f"{g} {c[i].mean():.3f}" for g, i in idx.items()))
    print("\nheld-out r, mean over stories [95% CI]")
    for m in models:
        cis = {g: boot(R[m][:, i].mean(1), rng) for g, i in idx.items()}
        print(f"  {m:6s} " + "  ".join(f"{g} {R[m][:, i].mean():.3f} [{cis[g][0]:.3f}, {cis[g][1]:.3f}]"
                                       for g, i in idx.items()))
    for m in ("b", "a", "b+a"):
        print(f"  per story, {m:4s} language: " + " ".join(f"{v:.3f}" for v in R[m][:, idx["language"]].mean(1))
              + " | auditory: " + " ".join(f"{v:.3f}" for v in R[m][:, idx["auditory"]].mean(1)))
    r2 = lambda m: np.sign(R[m]) * R[m] ** 2
    print("\nunique variance (r2 joint - r2 reduced), per-story mean over parcels; sign-flip p over stories")
    out = {"stories": stories, "n_sub": n_sub, "parcels": names, "r": {m: R[m].tolist() for m in R}}
    for full, red in (("b+a", "b"), ("b+c", "b"), ("b+s", "b"), ("b+s+a", "b+s"), ("b+g+a", "b+g"), ("b+a~", "b"),
                      ("b+g", "b")):
        d = r2(full) - r2(red)
        line = []
        for g, i in idx.items():
            di = d[:, i].mean(1)
            lo, hi = boot(di, rng)
            line.append(f"{g} {di.mean():+.4f} [{lo:+.4f}, {hi:+.4f}] p={signflip(di):.3f}")
        sig = bh([signflip(d[:, j]) for j in range(d.shape[1])])
        print(f"  {full:6s} over {red:4s}: " + "  ".join(line) + f"  | parcels FDR<0.05: {sig.sum()}/{len(sig)}"
              + (f" ({', '.join(names[j] for j in np.flatnonzero(sig))})" if 0 < sig.sum() <= 12 else ""))
    if layers:
        print("\nlayer sweep, language parcels, held-out r (trained / untrained)")
        print("  " + "  ".join(f"L{L} {R[f'a{L}'][:, idx['language']].mean():.3f}/{R[f'c{L}'][:, idx['language']].mean():.3f}"
                              for L in layers))
    tag = "quick" if a.quick else f"{n_sub}x{k}" + ("_events" if a.no_align else "")
    (a.data_dir / f"results_{tag}.json").write_text(json.dumps(out))
    print(f"\ntotal {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()

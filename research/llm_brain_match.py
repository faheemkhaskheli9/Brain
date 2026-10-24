"""LLM-brain match: does GPT-2 explain story-listening fMRI beyond word statistics? (issue #89)

Encoding models predict each voxel's response to a held-out story from features of the words heard.
The question is whether a contextual language model (GPT-2) explains variance that word statistics
(word rate, unigram and trigram surprisal) cannot, and whether that survives the controls below.

Pre-registered (written here and in the issue plan before the real-data run):
  Data       LeBel et al. 2023 (OpenNeuro ds003020): preprocessed responses of subjects UTS04-UTS08
             to the 25 stories all five heard once, plus word timings (TextGrids). The story heard
             five times ("wheretheressmoke") is used only to choose voxels and for the noise ceiling.
  Voxels     per subject, the 2,000 voxels with the highest repeat reliability on wheretheressmoke
             (mean correlation of each repeat with the mean of the other four). Chosen from repeats
             only, so no feature set is favoured.
  Features   per word, then summed within each TR (2.0045 s); delays of 1-4 TRs (FIR), z-scored per
               story. Big spaces are reduced to 128 principal components of the word vectors
               (stimulus only, no brain data).
               W  word statistics: count, unigram and trigram surprisal (Dirichlet-smoothed trigram
                  trained on the other 83 transcripts of the dataset, leaving out the scored story)
               E  static embeddings (the dataset's english1000 co-occurrence vectors, 985 dims)
               S  GPT-2 surprisal (small GPT-2, 124M, context of up to 512 tokens)
               G  GPT-2 layer 9 hidden state at each word's last token
               R  the same from an untrained GPT-2 (random weights, same tokenizer)
               H  G shifted by half a story (circularly, at the word level): keeps its statistics,
                  breaks its alignment with the response
  Model      ridge, leave-one-story-out over the 25 stories. In each fold one alpha per model (and,
             for joint models, the weight of the added block from 1/3, 1, 3) is chosen on 5 of the
             24 training stories after fitting on the other 19, then refitted on all 24.
  Score      per voxel on the held-out story, signed r^2 (r|r|). Unique variance of a block over a
             base = mean over voxels of r^2(base + block) - r^2(base).
  Statistic  per story, unique variance averaged over the five subjects; mean over 25 stories, 95% CI
             from 10,000 story bootstraps, one-sided sign-flip p over stories (100,000 flips).
             Primary: G over W. Secondary: G over W+E, G over W+S, R over W, H over W.
  Counts as  G over W at or below 0 (p > 0.05): word statistics match the brain as well as GPT-2.
  against    The controls: if R over W or H over W is as large as G over W, the gain is not GPT-2's
             learned context.
  Alignment  where row 0 of the response sits in the audio is not in the dataset files. It is picked
             (integer TR offset 0-10) by the held-out fit of W alone, before any GPT-2 model is fitted.

Deviations from the issue: it named the Narratives set (OpenNeuro ds002345). Its preprocessed
derivatives and word alignments are not on OpenNeuro's S3 bucket, and the datalad host was not
reachable from where this was first run, so the script uses LeBel et al. 2023, which ships both.
The first, unpushed run (issue comment, 2026-10-16) used Narratives and is not reproduced here.
GPT-2 runs in numpy from the original checkpoint (PyTorch did not install where this was first run).

Run: python research/llm_brain_match.py              # statistics from the saved per-story scores
     python research/llm_brain_match.py --fetch      # download (~45 GB streamed, ~1 GB kept), rebuild them
     python research/llm_brain_match.py --synthetic  # pipeline check on SYNTHETIC data (not a result)
Needs numpy; --fetch also needs h5py and regex (pip install h5py regex). About an hour with --fetch.
"""
import argparse
import collections
import csv
import json
import math
import os
import pickle
import time
import urllib.request
from pathlib import Path

import numpy as np

S3 = "https://s3.amazonaws.com/openneuro.org/ds003020/derivatives/"
GPT2 = "https://s3.amazonaws.com/models.huggingface.co/bert/gpt2-"   # the original OpenAI 124M weights
CACHE = Path(os.environ.get("BRAIN_KB_CACHE", Path.home() / ".cache" / "brain-kb")) / "lebel2023"
DATA = Path(__file__).parent / "data"
SCORES = DATA / "llm_brain_match_lebel2023.csv"
SUBJECTS = ("UTS04", "UTS05", "UTS06", "UTS07", "UTS08")
STORIES = ("adollshouse", "adventuresinsayingyes", "alternateithicatom", "avatar", "buck", "exorcism",
           "eyespy", "fromboyhoodtofatherhood", "hangtime", "haveyoumethimyet", "howtodraw", "inamoment",
           "itsabox", "legacy", "myfirstdaywiththeyankees", "naked", "odetostepfather", "sloth", "souls",
           "stagefright", "swimmingwithastronauts", "thatthingonmyarm", "theclosetthatateeverything",
           "tildeath", "undertheinfluence")
REPEAT = "wheretheressmoke"
TR, DELAYS, N_VOX, PCS, LAYER, CTX = 2.0045, (1, 2, 3, 4), 2000, 128, 9, 512
ALPHAS = np.logspace(0, 5, 11)
SCALES = (1 / 3, 1.0, 3.0)
INNER = 5                                    # training stories held out to pick alpha and block weight
BOOT, FLIPS = 10000, 100000
MODELS = {"W": "W", "G": "G", "R": "R", "W+G": "WG", "W+E": "WE", "W+E+G": "WEG", "W+S": "WS",
          "W+S+G": "WSG", "W+R": "WR", "W+H": "WH"}
CONTRASTS = (("GPT-2 over word statistics (primary)", "W+G", "W"),
             ("GPT-2 over word statistics + static embeddings", "W+E+G", "W+E"),
             ("GPT-2 over word statistics + GPT-2 surprisal", "W+S+G", "W+S"),
             ("untrained GPT-2 over word statistics", "W+R", "W"),
             ("GPT-2 shifted by half a story over word statistics", "W+H", "W"))
SKIP = {"", "sp", "sil", "ns", "lg", "br", "sl", "cg", "ls", "ig"}


# ---------------------------------------------------------------- downloads
def get(url, dest):
    """Download url to dest (skipped if present), retrying dropped connections."""
    dest = Path(dest)
    if not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        tmp = dest.with_suffix(dest.suffix + ".part")
        for attempt in range(5):
            try:
                with urllib.request.urlopen(url, timeout=600) as r, open(tmp, "wb") as f:
                    while chunk := r.read(1 << 20):
                        f.write(chunk)
                break
            except OSError:
                if attempt == 4:
                    raise
                time.sleep(2 ** attempt)
        tmp.rename(dest)
    return dest


def all_stories(cache):
    """Names of every story with a TextGrid (the trigram corpus)."""
    resp = json.loads(get(S3 + "respdict.json", cache / "respdict.json").read_text())
    return sorted(resp)


def words(path):
    """(onset seconds, lowercase word) from a Praat TextGrid's word tier (long, short or chronological format)."""
    lines = [ln.strip() for ln in Path(path).read_text(errors="replace").splitlines()]
    raw = []
    if lines[0].startswith('"Praat chronological'):
        tiers = [ln.split('"')[3] for ln in lines[:6] if ln.startswith('"IntervalTier"')]
        wt = str(tiers.index("word") + 1)
        for head, text in zip(lines[3 + len(tiers)::2], lines[4 + len(tiers)::2]):
            if head.split()[0] == wt:
                raw.append((float(head.split()[1]), text))
    elif "=" not in lines[3]:                    # short format: values only, one per line
        vals = [ln for ln in lines[3:] if ln]
        i = 4
        for _ in range(int(vals[3])):
            name, n = vals[i + 1].strip('"'), int(vals[i + 4])
            if name == "word":
                raw += [(float(vals[j]), vals[j + 2]) for j in range(i + 5, i + 5 + 3 * n, 3)]
            i += 5 + 3 * n
    else:
        tier, start = None, None
        for ln in lines:
            if ln.startswith("name ="):
                tier = ln.split('"')[1]
            elif ln.startswith("xmin =") and tier == "word":
                start = float(ln.split("=")[1])
            elif ln.startswith("text =") and tier == "word":
                raw.append((start, ln.split("=", 1)[1].strip()))
    out = []
    for start, text in raw:
        w = text.strip().strip('"').strip().lower()
        if w.startswith("{") or any(ch.isdigit() for ch in w):     # noise marks, stray phone labels
            continue
        w = w.strip("[](){}!\\")
        if w not in SKIP:
            out.append((start, w))
    return out


# ---------------------------------------------------------------- word statistics
def ngram_counts(texts):
    c1, c2, c3 = collections.Counter(), collections.Counter(), collections.Counter()
    for ws in texts:
        ws = ["<s>", "<s>"] + ws
        c1.update(ws[2:])
        c2.update(zip(ws[1:], ws[2:]))
        c3.update(zip(ws, ws[1:], ws[2:]))
    return c1, c2, c3


def surprisals(ws, counts, mu=2.0):
    """Unigram and Dirichlet-smoothed trigram surprisal (bits) of each word, counts from other stories."""
    c1, c2, c3 = counts
    n, v = sum(c1.values()), len(c1) + 1
    h2 = collections.Counter()                   # context counts c(u v) and c(v)
    for (a, b, _), k in c3.items():
        h2[(a, b)] += k
    h1 = collections.Counter()
    for (a, _), k in c2.items():
        h1[a] += k
    uni, tri = [], []
    seq = ["<s>", "<s>"] + ws
    for i, w in enumerate(ws):
        u, b = seq[i], seq[i + 1]
        p1 = (c1[w] + 1) / (n + v)
        p2 = (c2[(b, w)] + mu * p1) / (h1[b] + mu)
        p3 = (c3[(u, b, w)] + mu * p2) / (h2[(u, b)] + mu)
        uni.append(-math.log2(p1))
        tri.append(-math.log2(p3))
    return np.array(uni), np.array(tri)


# ---------------------------------------------------------------- GPT-2 in numpy
def load_torch_legacy(path):
    """State dict from a legacy (pre-zip) PyTorch checkpoint, without PyTorch. Only tensors are built."""
    dtypes = {"FloatStorage": np.float32, "LongStorage": np.int64}
    storages = {}

    class Unpickler(pickle.Unpickler):
        def find_class(self, mod, name):
            if name in ("_rebuild_tensor", "_rebuild_tensor_v2"):
                return lambda st, off, size, stride, *a: (st, off, size, stride)
            if (mod, name) == ("collections", "OrderedDict"):
                return collections.OrderedDict
            if mod == "torch" and name in dtypes:
                return name
            raise pickle.UnpicklingError(f"refusing {mod}.{name}")

        def persistent_load(self, pid):
            storages.setdefault(pid[2], [pid[1], None])
            return pid[2]

    with open(path, "rb") as f:
        for _ in range(3):                       # magic number, protocol, system info
            pickle.load(f)
        obj = Unpickler(f).load()
        for key in pickle.load(f):
            n = int(np.frombuffer(f.read(8), "<i8")[0])
            dt = np.dtype(dtypes[storages[key][0]])
            storages[key][1] = np.frombuffer(f.read(n * dt.itemsize), dt)
    out = {}
    for name, (st, off, size, stride) in obj.items():
        a = storages[st][1]
        out[name] = np.lib.stride_tricks.as_strided(a[off:], size, [s * a.itemsize for s in stride]).copy()
    return out


def random_gpt2(w, seed=0):
    """GPT-2's own initialisation: N(0, 0.02) weights, residual projections scaled by 1/sqrt(24)."""
    rng = np.random.default_rng(seed)
    out = {}
    for k, v in w.items():
        if k.endswith("ln_1.weight") or k.endswith("ln_2.weight") or k == "ln_f.weight":
            out[k] = np.ones_like(v)
        elif k.endswith(".bias") and "attn.bias" not in k:
            out[k] = np.zeros_like(v)
        elif "attn.bias" in k:
            out[k] = v
        else:
            sd = 0.02 / math.sqrt(24) if k.endswith("c_proj.weight") else 0.02
            out[k] = rng.normal(0, sd, v.shape).astype(np.float32)
    return out


class BPE:
    """GPT-2's byte-level BPE tokenizer (OpenAI's encoder.py, shortened)."""

    def __init__(self, vocab, merges):
        import regex
        bs = list(range(33, 127)) + list(range(161, 173)) + list(range(174, 256))
        cs = bs[:] + [256 + i for i in range(256) if i not in bs]
        bs += [i for i in range(256) if i not in bs]
        self.byte = dict(zip(bs, map(chr, cs)))
        self.enc = json.loads(Path(vocab).read_text())
        rows = Path(merges).read_text(encoding="utf-8").split("\n")[1:-1]
        self.rank = {tuple(r.split()): i for i, r in enumerate(rows)}
        self.pat = regex.compile(r"""'s|'t|'re|'ve|'m|'ll|'d| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+""")

    def bpe(self, tok):
        word = list(tok)
        while len(word) > 1:
            pairs = [(self.rank.get(p, 1e18), i) for i, p in enumerate(zip(word, word[1:]))]
            r, i = min(pairs)
            if r == 1e18:
                break
            word = word[:i] + [word[i] + word[i + 1]] + word[i + 2:]
        return word

    def encode(self, text):
        out = []
        for tok in self.pat.findall(text):
            out += [self.enc[t] for t in self.bpe("".join(self.byte[b] for b in tok.encode("utf-8")))]
        return out


def gelu(x):
    return 0.5 * x * (1 + np.tanh(0.7978845608 * (x + 0.044715 * x ** 3)))


def layernorm(x, g, b):
    m, v = x.mean(-1, keepdims=True), x.var(-1, keepdims=True)
    return g * (x - m) / np.sqrt(v + 1e-5) + b


def gpt2_forward(ids, w, keep, layer=LAYER, logits=True):
    """Hidden state after block `layer` and log-probabilities, for positions keep: of the window."""
    t = len(ids)
    x = w["wte.weight"][ids] + w["wpe.weight"][:t]
    mask = np.triu(np.full((t, t), -1e10, np.float32), 1)
    hid = None
    for i in range(12):
        p = f"h.{i}."
        h = layernorm(x, w[p + "ln_1.weight"], w[p + "ln_1.bias"])
        q, k, v = np.split(h @ w[p + "attn.c_attn.weight"] + w[p + "attn.c_attn.bias"], 3, -1)
        q, k, v = (a.reshape(t, 12, 64).transpose(1, 0, 2) for a in (q, k, v))
        s = q @ k.transpose(0, 2, 1) / 8.0 + mask
        s = np.exp(s - s.max(-1, keepdims=True))
        a = ((s / s.sum(-1, keepdims=True)) @ v).transpose(1, 0, 2).reshape(t, 768)
        x = x + a @ w[p + "attn.c_proj.weight"] + w[p + "attn.c_proj.bias"]
        h = layernorm(x, w[p + "ln_2.weight"], w[p + "ln_2.bias"])
        x = x + gelu(h @ w[p + "mlp.c_fc.weight"] + w[p + "mlp.c_fc.bias"]) @ w[p + "mlp.c_proj.weight"] \
            + w[p + "mlp.c_proj.bias"]
        if i + 1 == layer:
            hid = x[keep:].copy()
            if not logits:
                return hid, None
    z = layernorm(x[keep:], w["ln_f.weight"], w["ln_f.bias"]) @ w["wte.weight"].T
    z = z - z.max(-1, keepdims=True)
    return hid, z - np.log(np.exp(z).sum(-1, keepdims=True))


def gpt2_words(ws, w, bpe, logits=True):
    """Per word: layer-LAYER state at its last token, and its surprisal (bits), context <= CTX tokens."""
    toks, last = [50256], []                     # <|endoftext|> as the first context token
    for word in ws:
        toks += bpe.encode(" " + word)
        last.append(len(toks) - 1)
    ids = np.array(toks)
    hid = np.zeros((len(ids), 768), np.float32)
    lp = np.zeros(len(ids), np.float32)          # log p(token j | tokens < j)
    start, half = 0, CTX // 2
    while True:
        end = min(start + CTX, len(ids))
        keep = 0 if start == 0 else half
        h, z = gpt2_forward(ids[start:end], w, keep, logits=logits)
        hid[start + keep:end] = h
        if logits:
            nxt = ids[start + keep + 1:end + 1]
            lp[start + keep + 1:start + keep + 1 + len(nxt)] = z[np.arange(len(nxt)), nxt]
        if end == len(ids):
            break
        start += half
    first = [1] + [j + 1 for j in last[:-1]]
    sur = np.array([-lp[a:b + 1].sum() / math.log(2) for a, b in zip(first, last)])
    return hid[last], sur


# ---------------------------------------------------------------- build features and responses
def reliability(rep):
    """Leave-one-repeat-out reliability per voxel: mean corr(repeat i, mean of the others)."""
    rep = rep - rep.mean(1, keepdims=True)
    out = 0
    for i in range(len(rep)):
        a, b = rep[i], np.delete(rep, i, 0).mean(0)
        b = b - b.mean(0)
        out = out + (a * b).sum(0) / np.sqrt((a * a).sum(0) * (b * b).sum(0) + 1e-12)
    return out / len(rep)


def fetch(cache):
    import h5py
    names = all_stories(cache)
    texts = {s: words(get(S3 + f"TextGrids/{s}.TextGrid", cache / "TextGrids" / f"{s}.TextGrid"))
             for s in names}
    counts_all = ngram_counts([[w for _, w in texts[s]] for s in names])
    print(f"{len(names)} transcripts, {sum(len(t) for t in texts.values()):,} words")

    emb = h5py.File(get(S3 + "english1000sm.hf5", cache / "english1000sm.hf5"))
    vocab = {v.decode(): i for i, v in enumerate(emb["vocab"][:])}
    emat = emb["data"][:].T.astype(np.float32)
    for f in ("pytorch_model.bin", "vocab.json", "merges.txt"):
        get(GPT2 + f, cache / "gpt2" / f)
    w = load_torch_legacy(cache / "gpt2" / "pytorch_model.bin")
    wr = random_gpt2(w)
    bpe = BPE(cache / "gpt2" / "vocab.json", cache / "gpt2" / "merges.txt")

    feats = {}
    for s in STORIES:
        f = cache / "features" / f"{s}.npz"
        if not f.exists():
            t0 = time.time()
            onset = np.array([t for t, _ in texts[s]])
            ws = [x for _, x in texts[s]]
            own = ngram_counts([ws])            # leave the scored story out of the n-gram counts
            loo = tuple(a - b for a, b in zip(counts_all, own))
            uni, tri = surprisals(ws, loo)
            e = np.array([emat[vocab[x]] if x in vocab else np.zeros(emat.shape[1], np.float32) for x in ws])
            g, gs = gpt2_words(ws, w, bpe)
            r, _ = gpt2_words(ws, wr, bpe, logits=False)
            f.parent.mkdir(parents=True, exist_ok=True)
            np.savez(f, onset=onset, uni=uni, tri=tri, E=e, G=g, S=gs, R=r)
            print(f"  features {s}: {len(ws)} words, {time.time() - t0:.0f} s")
        feats[s] = dict(np.load(f))

    resp = {}
    for subj in SUBJECTS:
        f = cache / f"{subj}_resp.npz"
        if not f.exists():
            tmp = get(S3 + f"preprocessed_data/{subj}/{REPEAT}.hf5", cache / "tmp" / f"{subj}_{REPEAT}.hf5")
            rep = h5py.File(tmp)["individual_repeats"][:].astype(np.float32)
            rel = reliability(rep)
            vox = np.sort(np.argsort(-np.nan_to_num(rel, nan=-1))[:N_VOX])
            ceil = rel[vox]
            tmp.unlink()
            ys = {}
            for s in STORIES:
                tmp = get(S3 + f"preprocessed_data/{subj}/{s}.hf5", cache / "tmp" / f"{subj}_{s}.hf5")
                ys[s] = h5py.File(tmp)["data"][:, vox].astype(np.float32)
                tmp.unlink()
            np.savez(f, vox=vox, ceil=ceil, **ys)
            print(f"  {subj}: {N_VOX} voxels, repeat reliability {ceil.mean():.3f} (min {ceil.min():.3f})")
        resp[subj] = dict(np.load(f))
    return feats, resp


def pca_basis(feats, key):
    x = np.concatenate([feats[s][key] for s in STORIES])
    mu = x.mean(0)
    _, _, vt = np.linalg.svd(x - mu, full_matrices=False)
    return mu, vt[:PCS].T


def to_trs(onset, x, n, offset):
    """Sum word-level rows x into n TR bins; row r holds words with onset in [(r+offset)TR, (r+offset+1)TR)."""
    idx = np.floor(onset / TR).astype(int) - offset
    ok = (idx >= 0) & (idx < n)
    out = np.zeros((n, x.shape[1]), np.float64)
    np.add.at(out, idx[ok], x[ok])
    return out


def delayed(x):
    x = (x - x.mean(0)) / (x.std(0) + 1e-8)
    out = np.zeros((len(x), x.shape[1] * len(DELAYS)))
    for j, d in enumerate(DELAYS):
        out[d:, j * x.shape[1]:(j + 1) * x.shape[1]] = x[:len(x) - d]
    return out


def blocks(feats, n_tr, offset, pcs):
    """Per story: dict letter -> delayed TR-level feature block."""
    out = {}
    for s in STORIES:
        f, n = feats[s], n_tr[s]
        word = {"W": np.column_stack([np.ones(len(f["onset"])), f["uni"], f["tri"]]), "S": f["S"][:, None]}
        for k in ("E", "G", "R"):
            mu, basis = pcs[k]
            word[k] = (f[k] - mu) @ basis
        word["H"] = np.roll(word["G"], len(word["G"]) // 2, axis=0)
        out[s] = {k: delayed(to_trs(f["onset"], v, n, offset)) for k, v in word.items()}
    return out


# ---------------------------------------------------------------- ridge, leave-one-story-out
def corr(a, b):
    a, b = a - a.mean(0), b - b.mean(0)
    return (a * b).sum(0) / np.sqrt((a * a).sum(0) * (b * b).sum(0) + 1e-12)


def design(bl, stories, letters, scale):
    """Stack blocks; each scaled to equal total variance, the last one by `scale` more."""
    cols = []
    for i, k in enumerate(letters):
        x = np.concatenate([bl[s][k] for s in stories])
        cols.append(x * (scale if i == len(letters) - 1 and len(letters) > 1 else 1) / math.sqrt(x.shape[1]))
    return np.hstack(cols)


def ridge_paths(x, y, xt):
    """Test predictions for every alpha in ALPHAS, via one eigendecomposition of X'X."""
    s, v = np.linalg.eigh(x.T @ x)
    a, b = xt @ v, v.T @ (x.T @ y)
    return [(a / (s + al)) @ b for al in ALPHAS]


def evaluate(bl, ys, letters, rng):
    """Leave-one-story-out: per held-out story, per-voxel r. Hyperparameters picked on inner stories."""
    scales = SCALES if len(letters) > 1 else (1.0,)
    out = {}
    for test in STORIES:
        train = [s for s in STORIES if s != test]
        inner = list(rng.choice(train, INNER, replace=False))
        fit = [s for s in train if s not in inner]
        sub = rng.choice(ys[STORIES[0]].shape[1], min(500, ys[STORIES[0]].shape[1]), replace=False)
        yf = np.concatenate([ys[s][:, sub] for s in fit])
        best = (-np.inf, None, None)
        for sc in scales:
            preds = ridge_paths(design(bl, fit, letters, sc), yf, design(bl, inner, letters, sc))
            yi = np.concatenate([ys[s][:, sub] for s in inner])
            for al, p in zip(ALPHAS, preds):
                m = corr(p, yi).mean()
                if m > best[0]:
                    best = (m, sc, al)
        _, sc, al = best
        x, xt = design(bl, train, letters, sc), design(bl, [test], letters, sc)
        y = np.concatenate([ys[s] for s in train])
        beta = np.linalg.solve(x.T @ x + al * np.eye(x.shape[1]), x.T @ y)
        out[test] = corr(xt @ beta, ys[test])
    return out


def pick_offset(feats, resp, n_tr, pcs):
    """Integer TR offset of row 0 in the audio, by the held-out fit of word statistics alone."""
    rng = np.random.default_rng(0)
    fits = {}
    for off in range(0, 11):
        bl = blocks(feats, n_tr, off, pcs)
        r = [np.mean([v.mean() for v in evaluate(bl, resp[subj], "W", rng).values()]) for subj in SUBJECTS[:2]]
        fits[off] = float(np.mean(r))
        print(f"  offset {off:2d} TR: word-statistics r = {fits[off]:.3f}")
    return max(fits, key=fits.get)


def score(feats, resp):
    n_tr = {s: resp[SUBJECTS[0]][s].shape[0] for s in STORIES}
    for subj in SUBJECTS:
        assert all(resp[subj][s].shape[0] == n_tr[s] for s in STORIES), subj
    pcs = {k: pca_basis(feats, k) for k in ("E", "G", "R")}
    off = pick_offset(feats, resp, n_tr, pcs)
    print(f"alignment: row 0 = audio TR {off}")
    bl = blocks(feats, n_tr, off, pcs)
    rows = []
    for subj in SUBJECTS:
        ys = {s: resp[subj][s] for s in STORIES}
        for name, letters in MODELS.items():
            r = evaluate(bl, ys, letters, np.random.default_rng(1))
            for s in STORIES:
                rows.append({"subject": subj, "story": s, "model": name, "r": f"{r[s].mean():.5f}",
                             "r2": f"{(r[s] * np.abs(r[s])).mean():.5f}"})
            print(f"  {subj} {name:6s} r = {np.mean([r[s].mean() for s in STORIES]):.3f}")
        rows.append({"subject": subj, "story": REPEAT, "model": "ceiling",
                     "r": f"{resp[subj]['ceil'].mean():.5f}", "r2": ""})
    DATA.mkdir(exist_ok=True)
    with open(SCORES, "w", newline="") as f:
        wr = csv.DictWriter(f, ["subject", "story", "model", "r", "r2"], lineterminator="\n")
        wr.writeheader()
        wr.writerows(rows)
    print(f"wrote {SCORES} (alignment offset {off} TR)")


# ---------------------------------------------------------------- statistics
def stats(rows):
    tab = collections.defaultdict(dict)
    for r in rows:
        if r["model"] != "ceiling":
            tab[(r["model"], r["story"])][r["subject"]] = (float(r["r"]), float(r["r2"]))
    stories = sorted({s for _, s in tab})
    subjects = sorted({r["subject"] for r in rows})
    print(f"{len(subjects)} subjects x {len(stories)} held-out stories")
    ceil = [float(r["r"]) for r in rows if r["model"] == "ceiling"]
    if ceil:
        print(f"  repeat reliability of the voxels (single-presentation ceiling) r = {np.mean(ceil):.3f}")
    for m in [m for m in ("W", "G", "R", "W+G") if (m, stories[0]) in tab]:
        print(f"  {m:5s} r = {np.mean([tab[(m, s)][j][0] for s in stories for j in subjects]):.3f}")
    rng = np.random.default_rng(0)
    out = {}
    for label, joint, base in CONTRASTS:
        per = np.array([[tab[(joint, s)][j][1] - tab[(base, s)][j][1] for j in subjects] for s in stories])
        d = per.mean(1)
        boot = np.array([d[rng.integers(0, len(d), len(d))].mean() for _ in range(BOOT)])
        flips = rng.choice((-1.0, 1.0), (FLIPS, len(d))) @ d / len(d)
        p = (1 + (flips >= d.mean()).sum()) / (FLIPS + 1)
        lo, hi = np.percentile(boot, [2.5, 97.5])
        out[label] = (d.mean(), lo, hi, p)
        print(f"  {label}: unique r2 {d.mean():+.4f} [{lo:+.4f}, {hi:+.4f}], {int((d > 0).sum())}/{len(d)} stories "
              f"> 0, {int((per.mean(0) > 0).sum())}/{len(subjects)} subjects > 0, p = {p:.5f}")
    return out


# ---------------------------------------------------------------- synthetic check
def synthetic(gain, seed=0):
    """Fake stories: responses driven by word statistics, plus `gain` x a context feature block G."""
    rng = np.random.default_rng(seed)
    feats, resp = {}, {"SYN": {}}
    for s in STORIES:
        n = 300
        onset = np.sort(rng.uniform(0, n * TR, int(n * 2.5)))
        f = {"onset": onset, "uni": rng.gamma(2, 4, len(onset)), "tri": rng.gamma(2, 5, len(onset)),
             "S": rng.gamma(2, 3, len(onset))}
        for k in ("E", "G", "R"):
            f[k] = rng.normal(size=(len(onset), 16)).astype(np.float32)
        feats[s] = f
    pcs = {k: (np.zeros(16), np.eye(16)) for k in ("E", "G", "R")}
    bl = blocks(feats, {s: 300 for s in STORIES}, 0, pcs)
    wv, gv = rng.normal(size=(12, 50)), rng.normal(size=(64, 50))
    for s in STORIES:
        sig = bl[s]["W"] @ wv / 3 + gain * bl[s]["G"] @ gv / 8
        resp["SYN"][s] = (sig + rng.normal(size=sig.shape) * 2.0).astype(np.float32)
    rows = []
    for name in ("W", "W+G", "W+R", "W+H"):
        r = evaluate(bl, resp["SYN"], MODELS[name], np.random.default_rng(1))
        rows += [{"subject": "SYN", "story": s, "model": name, "r": r[s].mean(),
                  "r2": (r[s] * np.abs(r[s])).mean()} for s in STORIES]
    return rows


def main():
    global CONTRASTS
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true", help="download the data and rebuild the per-story scores")
    ap.add_argument("--synthetic", action="store_true", help="run the pipeline on SYNTHETIC data only")
    ap.add_argument("--cache", type=Path, default=CACHE, help="where downloads go (default ~/.cache/brain-kb)")
    args = ap.parse_args()
    if args.synthetic:
        print("SYNTHETIC DATA - checks the code, says nothing about the brain")
        CONTRASTS = (CONTRASTS[0], CONTRASTS[3], CONTRASTS[4])
        print("[no context signal planted]")
        null = stats(synthetic(0.0))
        print("[context signal planted]")
        plant = stats(synthetic(1.0))
        key = CONTRASTS[0][0]
        assert plant[key][3] < 0.01 and plant[key][0] > 0, "planted GPT-2-like signal not detected"
        assert null[key][3] > 0.01, "unique variance found where none was planted"
        assert all(plant[c[0]][3] > 0.01 for c in CONTRASTS[1:]), "a control picked up the planted signal"
        print("synthetic check passed: planted signal found, none found where absent, controls stay at 0")
        return
    if args.fetch:
        score(*fetch(args.cache))
    with open(SCORES) as f:
        stats(list(csv.DictReader(f)))


if __name__ == "__main__":
    main()

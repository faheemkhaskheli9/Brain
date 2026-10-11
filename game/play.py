"""Brain Lab: run it with  python game/play.py"""
import json
import tkinter as tk
import webbrowser
from pathlib import Path

from levels import (GLASS, INK, LEVELS, LILAC, MUTED, PINK, PROSE, SMALL, TICK_MS, UI, UI_BOLD,
                    VIOLET)

REPO = Path(__file__).resolve().parent.parent
SAVE = Path.home() / ".brain_lab" / "save.json"
TITLE = ("Bahnschrift SemiBold", 26)


def load_stars():
    try:
        return {int(k): v for k, v in json.loads(SAVE.read_text(encoding="utf-8")).get("stars", {}).items()}
    except (OSError, ValueError, AttributeError):
        return {}


def save_stars(stars):
    SAVE.parent.mkdir(parents=True, exist_ok=True)
    SAVE.write_text(json.dumps({"stars": stars}, indent=1), encoding="utf-8")


def star_text(n):
    return "★" * n + "☆" * (3 - n)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Brain Lab")
        self.configure(bg=GLASS)
        self.minsize(1080, 620)
        self.stars = load_stars()
        self.level = None
        self.body = tk.Frame(self, bg=GLASS)
        self.body.pack(fill="both", expand=True, padx=24, pady=16)
        self.bind_all("<KeyPress>", lambda e: self.level and self.level.key(e.keysym))
        self.menu()
        self.loop()

    def loop(self):
        if self.level:
            self.level.tick()
        self.after(TICK_MS, self.loop)

    def clear(self):
        self.level = None
        for w in self.body.winfo_children():
            w.destroy()

    def label(self, text, font=UI, fg=INK, **pack):
        lbl = tk.Label(self.body, text=text, font=font, fg=fg, bg=GLASS, justify="left",
                       anchor="w", wraplength=640)
        lbl.pack(fill="x", **pack)
        return lbl

    def button(self, parent, text, command, primary=False):
        b = tk.Button(parent, text=text, command=command, font=UI_BOLD if primary else UI,
                      fg=GLASS if primary else INK, bg=VIOLET if primary else LILAC,
                      activebackground=INK, activeforeground=GLASS, relief="flat",
                      padx=14, pady=6, cursor="hand2")
        b.pack(side="left", padx=(0, 8))
        return b

    def unlocked(self, i):
        return i == 0 or self.stars.get(i, 0) > 0   # level i+1 opens once level i is won

    def menu(self):
        self.clear()
        self.label("Brain Lab", TITLE)
        self.label("Run a working model of the brain, one mechanism at a time. "
                   "Each level is built from a page of this knowledge base.", PROSE, MUTED, pady=(0, 20))
        for i, cls in enumerate(LEVELS):
            open_ = self.unlocked(i)
            row = tk.Frame(self.body, bg=GLASS)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=f"{i + 1}", font=UI_BOLD, width=3, anchor="w", bg=GLASS,
                     fg=VIOLET if open_ else MUTED).pack(side="left")
            b = tk.Button(row, text=cls.title, font=UI_BOLD, width=18, anchor="w", relief="flat",
                          fg=INK if open_ else MUTED, bg=LILAC if open_ else GLASS,
                          activebackground=VIOLET, activeforeground=GLASS, padx=10,
                          state="normal" if open_ else "disabled", cursor="hand2" if open_ else "",
                          command=lambda i=i: self.intro(i))
            b.pack(side="left")
            tk.Label(row, text=star_text(self.stars.get(i + 1, 0)) if open_ else "locked",
                     font=UI, fg=PINK if open_ else MUTED, bg=GLASS, width=8).pack(side="left", padx=12)
            tk.Label(row, text=cls.goal, font=SMALL, fg=MUTED, bg=GLASS, anchor="w", justify="left",
                     wraplength=480).pack(side="left")

    def intro(self, i):
        self.clear()
        cls = LEVELS[i]
        self.label(f"Level {i + 1}", SMALL, MUTED)
        self.label(cls.title, TITLE)
        tag = tk.Label(self.body, text=cls.tag.capitalize(), font=SMALL, padx=8, pady=2,
                       fg=GLASS if cls.tag == "ESTABLISHED" else INK,
                       bg=VIOLET if cls.tag == "ESTABLISHED" else PINK)
        tag.pack(anchor="w", pady=(4, 0))
        if cls.tag_note:
            self.label(cls.tag_note, SMALL, MUTED)
        self.label(cls.intro, PROSE, pady=(16, 12))
        self.label("Goal: " + cls.goal, UI_BOLD, VIOLET, pady=(0, 20))
        row = tk.Frame(self.body, bg=GLASS)
        row.pack(anchor="w")
        self.button(row, "Start", lambda: self.play(i), primary=True).focus_set()
        self.button(row, "Back to levels", self.menu)

    def play(self, i):
        self.clear()
        bar = tk.Frame(self.body, bg=GLASS)
        bar.pack(fill="x")
        tk.Label(bar, text=f"{i + 1}  {LEVELS[i].title}", font=UI_BOLD, fg=INK, bg=GLASS).pack(side="left", padx=(0, 16))
        self.button(bar, "Retry", lambda: self.play(i)).config(takefocus=0)
        self.button(bar, "Back to levels", self.menu).config(takefocus=0)
        frame = tk.Frame(self.body, bg=GLASS)
        frame.pack(fill="both", expand=True, pady=(8, 0))
        self.focus_set()
        self.level = LEVELS[i](frame, lambda stars: self.after(900, lambda: self.debrief(i, stars)))

    def debrief(self, i, stars):
        self.stars[i + 1] = max(stars, self.stars.get(i + 1, 0))
        save_stars(self.stars)
        self.clear()
        cls = LEVELS[i]
        self.label(f"Level {i + 1} complete", SMALL, MUTED)
        self.label(cls.title, TITLE)
        self.label(star_text(stars), ("Bahnschrift", 28), PINK, pady=(0, 12))
        self.label(cls.debrief, PROSE, pady=(0, 16))
        link = self.label(f"Read more: {cls.kb}", UI, VIOLET, pady=(0, 20))
        link.config(cursor="hand2", font=(UI[0], UI[1], "underline"))
        link.bind("<Button-1>", lambda e: webbrowser.open((REPO / cls.kb).as_uri()))
        row = tk.Frame(self.body, bg=GLASS)
        row.pack(anchor="w")
        if i + 1 < len(LEVELS):
            self.button(row, "Next level", lambda: self.intro(i + 1), primary=True).focus_set()
        self.button(row, "Play again", lambda: self.play(i))
        self.button(row, "Back to levels", self.menu)


if __name__ == "__main__":
    try:   # sharp text on scaled Windows displays instead of a blurry bitmap stretch
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except (ImportError, AttributeError, OSError):
        pass
    App().mainloop()

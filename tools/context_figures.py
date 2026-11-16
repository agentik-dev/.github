#!/usr/bin/python3
"""The context primers' figures: every SVG under profile/context/figures/, written from the
CSVs in profile/context/data/ and the constants below. Stdlib only; no clock, locale or
environment reaches the output, so a second run changes no byte.

Run: tools/context_figures.py          write every figure
     tools/context_figures.py --check  write nothing; exit 1 naming each figure that differs
Either way it exits 1 naming any SVG in the folder that it no longer writes.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "profile" / "context" / "data"
OUT = ROOT / "profile" / "context" / "figures"

# ---- Constants, each from agentik-session at main 6ce9266 (plugin 2.0.0-alpha.128) ---------
PLUGIN = "2.0.0-alpha.128"
CEILING_OTHER = 180_000          # profiles.yaml defaults: ceilings and ceilings_1m, context
CEILING_ORCH = 400_000           # profiles.yaml orchestrator roles: ceilings_1m, context
WINDOW_SMALL = 200_000           # profiles.yaml models: a 200k window
WINDOW_LARGE = 1_000_000         # profiles.yaml models: a 1M window
COMPACT_NEAR = 967_000           # Claude Code compacts a 1M model near 967K (profiles.yaml note)
CHECKPOINT_AT = 80               # profiles.yaml checkpoint_at 0.8
ZONES = (("clear", 0), ("notice", 80), ("wind-down", 90), ("reserve", 92), ("exhausted", 100))
CHECKPOINT_EVERY = 10            # hooks.py: after the first crossing, every tenth tool call
METER_LINE_MINUTES = 30          # profiles.yaml pacing.meter_line_minutes
RESPAWN = {"cap": 20, "floor": 600, "settle": 60}   # profiles.yaml respawn
POLL_S, GRACE_S, KILL_S = 2, 10, 30                  # chain.py Chain defaults
BAND_CEILING, BAND_MARGIN = 97, 3                    # rules.py ADMISSION

# The plugin's own output, captured once in a temp HOME against made-up fixtures: the
# session line is session.ts bandLine, the usage line session.ts admissionLine (equal to
# admission.py band_line), the rest the hooks' additionalContext. Never edited by hand.
BAND = {
    "clear": "session: opus 5.5 · 1M · ctx 46% · turns 13%",
    "checkpoint": "session: opus 5.5 · 1M · ctx 80% · turns 35% · notice",
    "respawn": "session: opus 5.5 · 1M · ctx 80% · turns 35% · notice · respawn marked",
    "exit": "session: opus 5.5 · 1M · ctx 100% · turns 42% · exhausted",
    "five": "5h 62% → 84% · ceiling 97 · resets 14:05 (1h12) · 3 helpers, room for 2 · "
            "0 deferred · 7d 41%",
    "none": "no 5h window · 7d 62% · week resets Fri 13:00 · 3 helpers",
}
METER_CLEAR = "session meter: 46% of context, 13% of turns; the checkpoint comes at 80%"
METER_PAST = "session meter: 80% of context, 34% of turns; the checkpoint came at 80%"
ZONE_LINE = "Sitting budget: 'notice' zone."
CHECKPOINT_LINE = (
    "CHECKPOINT: 80.1% context (320400/400000), 34.8% turns (139/400); charter <this sitting's "
    "charter>; bring the charter current with a Next act that opens RESPAWN:, commit, then run "
    "`agentik session checkpoint --respawn --charter <this sitting's charter>` and end the turn; "
    "the launcher restarts this sitting; tell the owner you are winding down at the meter's "
    "line, at 80.1%")
EXIT_LINE = "EXIT: land the act in flight at a checkpoint, then exit; respawn, never compact"
# The made-up admission figures behind BAND["five"]: now 12:53, the reset 14:05.
ADMIT = {"now": 62, "peak": 84, "each": 5, "room": 2, "now_at": "12:53", "reset_at": "14:05"}

# ---- Drawing ----------------------------------------------------------------------------
W = 760
SANS = '-apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif'
MONO = 'ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace'
CW = 7.22                         # a 12 px monospace advance, for placing marks on a line

# class: (light, dark); a fill unless named in STROKES.
PALETTE = {
    "bg": ("#ffffff", "#0d1117"), "panel": ("#f6f8fa", "#161b22"),
    "fg": ("#1f2328", "#e6edf3"), "mu": ("#59636e", "#9198a1"),
    "orch": ("#0969da", "#4493f8"), "oth": ("#bc4c00", "#f0883e"),
    "over": ("#cf222e", "#f85149"), "ok": ("#1a7f37", "#3fb950"),
    "z-clear": ("#d1f0d9", "#1c4428"), "z-notice": ("#fff1b8", "#4b3a00"),
    "z-wind-down": ("#ffd8b5", "#5a3000"), "z-reserve": ("#ffc1c0", "#6b1a1d"),
    "z-exhausted": ("#cf222e", "#f85149"), "soft": ("#ddf4ff", "#12263f"),
    "soft2": ("#fff1e5", "#3d2410"),
}
STROKES = {
    "grid": ("#d1d9e0", "#30363d"), "axis": ("#59636e", "#9198a1"),
    "line": ("#1f2328", "#e6edf3"), "cp": ("#9a6700", "#d29922"),
    "ceil": ("#cf222e", "#f85149"), "s-orch": ("#0969da", "#4493f8"),
    "s-oth": ("#bc4c00", "#f0883e"), "edge": ("#d1d9e0", "#3d444d"),
}


def esc(s) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def n(v: float) -> str:
    """A coordinate: one decimal, no trailing zero."""
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


def style() -> str:
    def rules(i: int) -> str:
        out = [f".{k}{{fill:{v[i]}}}" for k, v in PALETTE.items()]
        out += [f".{k}{{stroke:{v[i]};fill:none}}" for k, v in STROKES.items()]
        out += [f".t{{fill:{PALETTE['fg'][i]}}}", f".m{{fill:{PALETTE['mu'][i]}}}",
                f".halo{{stroke:{PALETTE['bg'][i]};stroke-width:4px;paint-order:stroke;"
                "stroke-linejoin:round}"]
        return "".join(out)
    return ("<style>"
            f"text{{font-family:{SANS};font-size:13px}}"
            f".mono{{font-family:{MONO};font-size:12px}}.s{{font-size:12px}}"
            ".h{font-size:15px;font-weight:600}.b{font-weight:600}"
            ".term{fill:#11161d}.tt{fill:#e6edf3}.td{fill:#8b949e}.tbar{fill:#1f2630}"
            ".tedge{stroke:#3d444d;fill:none}.badge{fill:#f2cc60}.bt{fill:#1f2328}"
            ".dash{stroke-dasharray:6 4}.dot{stroke-dasharray:2 3}"
            + rules(0)
            + "@media (prefers-color-scheme: dark){" + rules(1) + "}"
            + "</style>")


class Svg:
    def __init__(self, h: int, title: str, desc: str):
        self.h, self.title, self.desc, self.parts = h, title, desc, []

    def add(self, s: str) -> None:
        self.parts.append(s)

    def text(self, x, y, s, cls="t", anchor="start", extra=""):
        a = "" if anchor == "start" else f' text-anchor="{anchor}"'
        self.add(f'<text x="{n(x)}" y="{n(y)}" class="{cls}"{a}{extra}>{esc(s)}</text>')

    def lines(self, x, y, rows, cls="t", step=16, anchor="start"):
        for i, r in enumerate(rows):
            self.text(x, y + i * step, r, cls, anchor)

    def rect(self, x, y, w, h, cls, rx=0, extra=""):
        r = f' rx="{n(rx)}"' if rx else ""
        self.add(f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" class="{cls}"{r}{extra}/>')

    def line(self, x1, y1, x2, y2, cls, width=1.0):
        self.add(f'<line x1="{n(x1)}" y1="{n(y1)}" x2="{n(x2)}" y2="{n(y2)}" class="{cls}" '
                 f'stroke-width="{n(width)}"/>')

    def path(self, d, cls, width=1.0, extra=""):
        self.add(f'<path d="{d}" class="{cls}" stroke-width="{n(width)}"{extra}/>')

    def circle(self, x, y, r, cls):
        self.add(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" class="{cls}"/>')

    def arrow(self, x1, y1, x2, y2, cls="line", width=1.4):
        """A line with a filled head at (x2, y2), horizontal or vertical only."""
        self.line(x1, y1, x2, y2, cls, width)
        k = "t" if cls == "line" else cls.replace("s-", "")
        if y1 == y2:
            d = 1 if x2 > x1 else -1
            pts = f"{n(x2)},{n(y2)} {n(x2 - 8 * d)},{n(y2 - 4)} {n(x2 - 8 * d)},{n(y2 + 4)}"
        else:
            d = 1 if y2 > y1 else -1
            pts = f"{n(x2)},{n(y2)} {n(x2 - 4)},{n(y2 - 8 * d)} {n(x2 + 4)},{n(y2 - 8 * d)}"
        self.add(f'<polygon points="{pts}" class="{k}"/>')

    def badge(self, x, y, num):
        self.circle(x, y, 9 if num < 10 else 10, "badge")
        self.text(x, y + 4, str(num), "bt s b", "middle")

    def render(self) -> bytes:
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{self.h}" '
                f'viewBox="0 0 {W} {self.h}" role="img" aria-labelledby="title desc">'
                f'<title id="title">{esc(self.title)}</title><desc id="desc">{esc(self.desc)}</desc>'
                + style() + f'<rect width="{W}" height="{self.h}" class="bg"/>')
        return ("\n".join([head] + self.parts + ["</svg>"]) + "\n").encode("utf-8")


def wrap(s: str, width: int) -> list:
    out, cur = [], ""
    for w in s.split():
        if cur and len(cur) + 1 + len(w) > width:
            out.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}" if cur else w
    return out + ([cur] if cur else [])


def read(name: str) -> list:
    with open(DATA / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def kfmt(v: float) -> str:
    return "1M" if v == 1_000_000 else (f"{v / 1000:g}k")


# ---- 1. The lifecycle -------------------------------------------------------------------
def lifecycle() -> bytes:
    s = Svg(372, "The lifecycle of a sitting",
            "A drawing, not a measurement. Three sittings in a row. Each one's context rises "
            "as it works; at 80 percent of its ceiling the meter prints CHECKPOINT, the sitting "
            "brings its charter current and closes on RESPAWN, the launcher ends it and starts a "
            "fresh session, and the new sitting reads the charter and carries on.")
    s.text(24, 26, "One sitting after another", "t h")
    s.text(24, 45, "A drawing of the rule, not a measurement.", "m s")
    x0, x1, yb = 64, 740, 214

    def y(p):
        return yb - 1.3 * p
    s.text(x0, 70, "Context used, as a share of the sitting's ceiling", "m s")
    s.line(x0, y(100), x1, y(100), "ceil", 1.5)
    s.line(x0, y(CHECKPOINT_AT), x1, y(CHECKPOINT_AT), "cp dash", 1.5)
    s.line(x0, yb, x1, yb, "axis")
    for p, lab in ((100, "100%"), (CHECKPOINT_AT, "80%"), (0, "0")):
        s.text(x0 - 6, y(p) + 4, lab, "m s", "end")
    s.text(x1, y(100) - 6, "the ceiling", "over s halo", "end")
    s.text(x1, y(CHECKPOINT_AT) - 6, "the checkpoint", "m s halo", "end")
    steps = (6, 11, 14, 22, 27, 31, 38, 45, 49, 57, 63, 68, 74, 81, 84)
    width, gap = 196, 32
    for i in range(3):
        xs = x0 + 6 + i * (width + gap)
        pts = []
        for j, p in enumerate(steps):
            xa = xs + width * j / len(steps)
            xb = xs + width * (j + 1) / len(steps)
            pts += [f"{n(xa)},{n(y(p))}", f"{n(xb)},{n(y(p))}"]
        area = f"M{n(xs)},{n(yb)} L" + " L".join(pts) + f" L{n(xs + width)},{n(yb)} Z"
        if i == 2:
            pts = pts[:18]
            area = f"M{n(xs)},{n(yb)} L" + " L".join(pts) + f" L{pts[-1].split(',')[0]},{n(yb)} Z"
        s.path(area, "soft", 0)
        s.path("M" + " L".join(pts), "s-orch", 2)
        if i < 2:
            s.line(xs + width, y(84), xs + width, yb, "s-orch dot", 1.5)
    xs = x0 + 6
    cross = xs + width * 13 / len(steps)
    s.badge(xs + 60, y(30) - 12, 1)
    s.badge(cross, y(CHECKPOINT_AT) - 14, 2)
    s.badge(xs + width - 4, y(84) - 14, 3)
    s.badge(xs + width + gap / 2, yb - 16, 4)
    s.badge(xs + width + gap + 14, y(6) - 16, 5)
    s.text(x1, yb + 18, "time", "m s", "end")
    texts = ("Work. The meter counts context and turns after every tool call.",
             "At 80% the meter prints CHECKPOINT. Bring the charter current and commit.",
             "Close. The Next act opens RESPAWN; mark it and end the turn.",
             "The launcher waits for the turn to settle, ends the sitting and starts a fresh one.",
             "The new sitting reads the charter and does its Next act.")
    bw, bg, by = 136, 8, 246
    for i, t in enumerate(texts):
        bx = 24 + i * (bw + bg)
        s.rect(bx, by, bw, 116, "panel", 6)
        s.badge(bx + 16, by + 16, i + 1)
        s.lines(bx + 10, by + 44, wrap(t, 19), "t s", 15)
    return s.render()


# ---- 2. The ceilings in their windows ---------------------------------------------------
def ceilings() -> bytes:
    s = Svg(482, "Two ceilings inside their windows, and the zones",
            "To scale: a 180k ceiling on a 200k window and on a 1M window, and a 400k ceiling on "
            "a 1M window, with Claude Code's compaction point near 967k. Below, the zones as a "
            "share of either ceiling: clear to 80, notice from 80, wind-down from 90, reserve "
            "from 92, exhausted at 100, with each zone's token figures.")
    s.text(24, 26, "Two ceilings inside their windows", "t h")
    s.text(24, 45, "Drawn to scale. The checkpoint mark sits at 80% of each ceiling.", "m s")
    x0, span = 24, 712.0

    def x(t):
        return x0 + span * t / WINDOW_LARGE
    rows = ((f"A builder, a helper or a plain session on a 200k window", WINDOW_SMALL, CEILING_OTHER, "oth"),
            ("The same roles on a 1M window: the ceiling stays 180k", WINDOW_LARGE, CEILING_OTHER, "oth"),
            ("An orchestrator on a 1M window", WINDOW_LARGE, CEILING_ORCH, "orch"))
    for i, (label, win, ceil, cls) in enumerate(rows):
        yt = 74 + i * 54
        s.text(x0, yt, label, "t s")
        s.rect(x0, yt + 8, x(win) - x0, 22, "panel", 0, ' stroke-width="1"')
        s.rect(x0, yt + 8, x(win) - x0, 22, "edge")
        s.rect(x0, yt + 8, x(ceil) - x0, 22, cls)
        s.text(x0 + 6, yt + 24, f"ceiling {kfmt(ceil)}", "bg s b", "start")
        cp = x(ceil * CHECKPOINT_AT / 100)
        s.line(cp, yt + 4, cp, yt + 34, "line", 2)
        lab = f"{kfmt(win)} window"
        s.text(x(COMPACT_NEAR) - 8 if win == WINDOW_LARGE else x(win) + 6, yt + 24, lab, "m s",
               "end" if win == WINDOW_LARGE else "start")
    xc = x(COMPACT_NEAR)
    s.line(xc, 94, xc, 222, "ceil dash", 1.5)
    s.text(xc - 6, 98, "Claude Code compacts near 967k on a 1M window", "over s", "end")
    for t in (0, 200_000, 400_000, 600_000, 800_000, 1_000_000):
        s.line(x(t), 230, x(t), 236, "axis")
        s.text(x(t), 250, "0" if t == 0 else kfmt(t), "m s",
               "start" if t == 0 else ("end" if t == WINDOW_LARGE else "middle"))
    s.line(x0, 230, x0 + span, 230, "axis")
    # The zones.
    s.text(24, 286, "The zones, as a share of either ceiling", "t h")
    zx0, zspan, zy = 24, 640.0, 318

    def zx(p):
        return zx0 + zspan * p / 100
    bounds = [z[1] for z in ZONES[1:]] + [100]
    for (name, lo), hi in zip(ZONES[:-1], bounds):
        s.rect(zx(lo), zy, zx(hi) - zx(lo), 26, f"z-{name}")
    s.rect(zx(100), zy, 56, 26, "z-exhausted")
    s.text(zx(40), zy + 18, "clear", "t s", "middle")
    s.text(zx(85), zy + 18, "notice", "t s", "middle")
    s.text(zx(96), zy + 18, "reserve", "t s", "middle")
    s.text(zx(100) + 28, zy + 18, "100%+", "bg s b", "middle")
    s.line(zx(91), zy - 2, zx(91), zy - 12, "line")
    s.text(zx(91), zy - 16, "wind-down", "t s", "middle")
    s.text(zx(100) + 28, zy - 16, "exhausted", "t s", "middle")
    for p in (0, 80, 90, 92, 100):
        s.line(zx(p), zy + 26, zx(p), zy + 32, "axis")
    s.text(zx(0), zy + 44, "0%", "m s")
    s.text(zx(80), zy + 44, "80%", "m s", "middle")
    s.text(zx(91), zy + 44, "90 · 92", "m s", "middle")
    s.text(zx(100), zy + 44, "100%", "m s", "middle")
    cols = (("", 24), ("notice, 80%", 170), ("wind-down, 90%", 310), ("reserve, 92%", 450),
            ("exhausted, 100%", 600))
    ty = 392
    for lab, cx in cols[1:]:
        s.text(cx, ty, lab, "t s b")
    for r, (lab, c) in enumerate((("180k ceiling", CEILING_OTHER), ("400k ceiling", CEILING_ORCH))):
        s.text(24, ty + 18 + r * 17, lab, "m s")
        for (z, cx), p in zip(cols[1:], (80, 90, 92, 100)):
            v = c * p / 100
            s.text(cx, ty + 18 + r * 17, f"{v / 1000:g}k", "t s")
    s.text(24, ty + 58, "what happens", "m s")
    acts = ("CHECKPOINT, then every 10th tool call", "stop starting what you cannot finish",
            "the rest is for the wrap-up", "EXIT on every tool call")
    for (z, cx), a in zip(cols[1:], acts):
        s.lines(cx, ty + 58, wrap(a, 20), "t s", 15)
    return s.render()


# ---- 3. Peak context per sitting --------------------------------------------------------
def histogram() -> bytes:
    rows = read("sittings_hist.csv")
    summary = {r["role"]: r for r in read("sittings_summary.csv")}
    groups = (("orchestrator", "The orchestrator roles, 400k ceiling", "orch"),
              ("other", "Every other role, 180k ceiling", "oth"))
    total = sum(int(summary[g]["sittings"]) for g, _, _ in groups)
    s = Svg(500, "Peak context per sitting, as a share of its ceiling",
            f"Two histograms, {total} sittings from {summary['other']['first_day_utc']} to "
            f"{summary['orchestrator']['last_day_utc']}. Bars are ten points wide; a line marks "
            "the checkpoint at 80 percent and another the ceiling at 100. Sittings that "
            "reached or passed the ceiling are drawn in red, with their count.")
    s.text(24, 26, "Peak context per sitting, as a share of its ceiling", "t h")
    s.text(24, 45, f"{total:,} sittings, {summary['other']['first_day_utc']} to "
           f"{summary['orchestrator']['last_day_utc']}. Bars are ten points wide; "
           "each panel has its own vertical scale.", "m s")
    x0, bw = 64, 42.5
    for gi, (g, title, cls) in enumerate(groups):
        data = [(int(r["bucket_low_pct_of_ceiling"]), int(r["sittings"])) for r in rows
                if r["role"] == g]
        n_s = int(summary[g]["sittings"])
        over = sum(c for b, c in data if b >= 100)
        assert over == int(summary[g]["sittings_peaking_at_or_over_100"]), g
        assert (sum(c for b, c in data if 70 <= b < 90)
                == int(summary[g]["sittings_peaking_70_to_90"])), g
        top = 74 + gi * 216
        s.text(24, top, f"{title}: {n_s:,} sittings", "t b")
        py0, ph = top + 30, 140
        vmax = max(c for _, c in data)
        scale = ph / (vmax * 1.12)
        base = py0 + ph
        step = next(k for k in (25, 50, 100, 200) if vmax / k <= 5)
        for v in range(step, int(vmax * 1.12) + 1, step):
            yy = base - v * scale
            s.line(x0, yy, x0 + bw * 16, yy, "grid")
            s.text(x0 - 6, yy + 4, f"{v}", "m s", "end")
        s.line(x0, base, x0 + bw * 16, base, "axis")
        for b, c in data:
            bx = x0 + (b // 10) * bw
            h = c * scale
            s.rect(bx + 3, base - h, bw - 6, h, "over" if b >= 100 else cls)
            s.text(bx + bw / 2, base - h - 4, str(c), "t s", "middle")
            lab = f"{b}+" if b == 150 else str(b)
            s.text(bx + bw / 2, base + 16, lab, "m s", "middle")
        xc, xl = x0 + 8 * bw, x0 + 10 * bw
        s.line(xc, py0 - 8, xc, base, "cp dash", 1.5)
        s.line(xl, py0 - 8, xl, base, "ceil", 1.5)
        s.text(xc - 4, py0 - 2, "checkpoint 80%", "m s", "end")
        s.text(xl + 4, py0 - 2, "ceiling 100%", "over s")
        s.text(x0 + bw * 16, py0 + 34,
               f"{over} reached or passed the ceiling ({100 * over / n_s:.1f}%)", "over s b", "end")
        s.text(x0 + bw * 16, py0 + 52, f"median {summary[g]['median_pct']}%, "
               f"90th percentile {summary[g]['p90_pct']}%", "m s", "end")
    s.text(x0 + bw * 8, 492, "peak context in the sitting, % of its ceiling (each bar's low edge)",
           "m s", "middle")
    return s.render()


# ---- 4. The launcher's sequence ---------------------------------------------------------
def launcher() -> bytes:
    s = Svg(0, "The launcher's sequence",
            "A sequence drawing of agentik session run. The hooks print CHECKPOINT; the sitting "
            "brings its charter current, commits, runs the respawn checkpoint and ends its "
            "turn; the launcher waits for the turn to settle, checks its guards, ends the "
            "sitting, waits a grace, writes a restart line and starts a fresh session with the "
            "same arguments, which reads the newest charter.")
    s.text(24, 26, "What agentik session run does at a RESPAWN close", "t h")
    A, B, C = 132, 380, 628
    for cx, t, sub in ((A, "The sitting", "claude, in your terminal"),
                       (B, "The plugin's hooks", "inside the sitting"),
                       (C, "The launcher", "agentik session run")):
        s.rect(cx - 112, 44, 224, 44, "panel", 6)
        s.text(cx, 63, t, "t b", "middle")
        s.text(cx, 80, sub, "m s", "middle")
    lifelines = len(s.parts)

    def note(cx, y, rows, w=236):
        h = 12 + 15 * len(rows)
        x = min(max(cx - w / 2, 10), W - 10 - w)
        s.rect(x, y, w, h, "soft", 4)
        s.lines(x + 8, y + 17, rows, "t s", 15)
        return y + h

    def label(x, y, text, cls="t s"):
        s.text(x, y, text, cls + " halo", "middle")
    y = 120
    s.arrow(B, y, A, y)
    label((A + B) / 2, y - 7, "CHECKPOINT: … at 80% of the ceiling")
    y = note(A, y + 12, ["Bring the charter current; its Next", "act opens RESPAWN:. Commit."])
    y += 46
    s.arrow(A, y, B, y)
    label((A + B) / 2, y - 23, "agentik session checkpoint", "mono t")
    label((A + B) / 2, y - 8, "--respawn --charter <file>", "mono t")
    y = note(B, y + 12, ["The verb writes the marker; the", "PostToolUse hook confirms the",
                         "call came from the main thread."])
    y += 34
    s.arrow(A, y, B, y)
    label((A + B) / 2, y - 7, "the turn ends")
    y = note(B, y + 12, ["The Stop hook stamps the turn end."])
    y = note(C, y + 18, [f"Polls every {POLL_S} s. Waits until the", "turn end has stood "
                         f"{RESPAWN['settle']} s with no", "new tool call or prompt and no",
                         "helper call open (settle)."])
    y = note(C, y + 10, ["Checks: the marker is confirmed;", "the Next act still opens RESPAWN",
                         "and this sitting touched the charter;",
                         f"no STOP file; fewer than {RESPAWN['cap']}",
                         "restarts in 24 h (cap); the sitting",
                         f"is {RESPAWN['floor']} s old or more (floor)."])
    y += 34
    s.arrow(C, y, A, y)
    label((B + C) / 2, y - 7, f"SIGTERM, then SIGKILL after {KILL_S} s")
    y = note(C, y + 12, [f"A {GRACE_S} s grace: Ctrl-C or a STOP", "file ends the chain here. Then it",
                         "writes a restart line to its ledger."])
    y += 48
    s.arrow(C, y, A, y)
    label((B + C) / 2, y - 23, "claude --session-id <new id>", "mono t")
    label((B + C) / 2, y - 8, "<the same arguments>", "mono t")
    y = note(A, y + 12, ["A fresh session reads the newest", "charter and does its Next act."])
    s.parts[lifelines:lifelines] = [
        f'<line x1="{n(cx)}" y1="88" x2="{n(cx)}" y2="{n(y + 8)}" class="axis dash" '
        'stroke-width="1"/>' for cx in (A, B, C)]
    s.h = int(y + 24)
    return s.render()


# ---- 5. Restarts a day ------------------------------------------------------------------
def _day(d: str) -> int:
    """Days since 2026-10-11, for dates in October and November 2026 only."""
    y, m, dd = (int(p) for p in d.split("-"))
    assert y == 2026 and m in (10, 11), d
    return (dd - 11) if m == 10 else (21 + dd - 1)


def restarts() -> bytes:
    rows = read("restarts.csv")
    counts = sorted(int(r["launcher_restarts"]) for r in rows)
    med = (counts[len(counts) // 2] if len(counts) % 2 else
           (counts[len(counts) // 2 - 1] + counts[len(counts) // 2]) / 2)
    total = sum(counts)
    first, last = rows[0]["day_utc"], rows[-1]["day_utc"]
    s = Svg(338, "Launcher restarts a day",
            f"A bar chart of the launcher's restarts each day, all chains together, {first} to "
            f"{last}: {total} restarts on {len(rows)} days, a median of {med:g} a day. The last "
            "day is the day of the cut, so it is partial.")
    s.text(24, 26, "Launcher restarts a day, every chain together", "t h")
    s.text(24, 45, f"{total} restarts on the {len(rows)} days that had one, {first} to {last} "
           "(UTC). The last day is the day of the cut.", "m s")
    x0, x1, top, base = 52, 740, 70, 262
    days = _day(last) + 1
    slot = (x1 - x0) / days
    vmax = 50

    def y(v):
        return base - (base - top) * v / vmax
    for v in (10, 20, 30, 40, 50):
        s.line(x0, y(v), x1, y(v), "grid")
        s.text(x0 - 6, y(v) + 4, str(v), "m s", "end")
    s.line(x0, base, x1, base, "axis")
    for r in rows:
        i = _day(r["day_utc"])
        v = int(r["launcher_restarts"])
        s.rect(x0 + i * slot + 2, y(v), slot - 4, base - y(v), "orch")
    s.line(x0, y(med), x1, y(med), "line dash", 1.2)
    s.text(x0 + 27.5 * slot, y(med) - 6, f"median {med:g} a day", "t s b halo", "middle")
    for i, lab in ((0, "Oct 11"), (7, "Oct 18"), (14, "Oct 25"), (21, "Nov 1"), (28, "Nov 8"),
                   (35, "Nov 15")):
        s.text(x0 + i * slot + slot / 2, base + 18, lab, "m s", "middle")
    over = sum(1 for c in counts if c > RESPAWN["cap"])
    s.lines(x0, 304, [f"The cap of {RESPAWN['cap']} restarts in any 24 hours applies to each chain "
                      f"and is a setting, so the {over} days with more",
                      f"than {RESPAWN['cap']} had more than one chain running, or a raised cap."],
            "m s", 17)
    return s.render()


# ---- 6. November's seven-day reading ----------------------------------------------------
def november() -> bytes:
    rows = read("usage_readings_nov.csv")
    week = [(float(r["hours_since_first_reading"]), float(r["seven_day_pct"])) for r in rows]
    (h0, p0), (h1, p1) = week[0], week[-1]
    rate = (p1 - p0) / (h1 - h0)
    s = Svg(330, "The seven-day reading over 25 hours of November 2026",
            f"A line through {len(week)} readings of the seven-day usage meter. It climbs from "
            f"{p0:g} to {p1:g} percent over {h1 - h0:.0f} hours, about {rate:.1f} points an hour. "
            f"The record ends at {p1:g} percent and does not show what came after. The vertical "
            "axis starts at 50 percent.")
    s.text(24, 26, "The seven-day reading, 25 hours of November 2026", "t h")
    s.text(24, 45, f"With the usage band, which advises and refuses nothing. {len(week)} readings; "
           "the axis starts at 50%.", "m s")
    x0, x1, top, base, hmax, lo = 52, 740, 70, 270, 26.0, 50

    def x(h):
        return x0 + (x1 - x0) * h / hmax

    def y(p):
        return base - (base - top) * (p - lo) / (100 - lo)
    for v in (60, 70, 80, 90, 100):
        s.line(x0, y(v), x1, y(v), "grid")
        s.text(x0 - 6, y(v) + 4, f"{v}%", "m s", "end")
    s.text(x0 - 6, y(lo) + 4, f"{lo}%", "m s", "end")
    s.line(x0, base, x1, base, "axis")
    d = "M" + " L".join(f"{n(x(h))},{n(y(p))}" for h, p in week)
    s.path(d, "s-orch", 2.2, ' stroke-linejoin="round"')
    for h, p in week:
        s.circle(x(h), y(p), 2.8, "orch")
    for h in (0, 6, 12, 18, 24):
        s.line(x(h), base, x(h), base + 5, "axis")
        s.text(x(h), base + 19, f"hour {h}", "m s", "middle")
    s.text(x(h1) - 8, y(p1) + 24, f"the record ends here, at {p1:g}%", "t s b halo", "end")
    s.text(x(13), y(66), f"seven-day reading: {p0:g}% to {p1:g}% over {h1 - h0:.0f} hours,",
           "orch s b", "middle")
    s.text(x(13), y(66) + 17, f"about {rate:.1f} points an hour", "orch s b", "middle")
    s.text(24, 318, "Each dot is a reading; the line between two dots is drawn, not measured.",
           "m s")
    return s.render()


# ---- 7. Admission's mechanism (a drawing) -----------------------------------------------
def admission() -> bytes:
    a = ADMIT
    s = Svg(380, "How the usage band projects a five-hour window (a drawing)",
            "A drawing, not a measurement. Now the window is at 62 percent. The burn of the "
            "running main threads and helpers carries it to a projected 84 percent at the reset. "
            "Each new helper adds its own burn; two fit under the ceiling of 97 less a margin "
            "of 3, so the band reads room for 2. A third would cross.")
    s.text(24, 26, "How the band projects the five-hour window", "t h")
    s.text(24, 45, "A drawing, not a measurement: the figures match the band on the band page.",
           "m s")
    x0, x1, top, base = 70, 470, 72, 316

    def y(p):
        return base - (base - top) * (p - 40) / 62
    for v in (40, 60, 80):
        s.line(x0, y(v), 560, y(v), "grid")
        s.text(x0 - 6, y(v) + 4, f"{v}%", "m s", "end")
    s.line(x0, y(BAND_CEILING), 560, y(BAND_CEILING), "ceil dash", 1.5)
    s.text(x0 + 4, y(BAND_CEILING) - 5, f"ceiling {BAND_CEILING}", "over s b")
    lim = BAND_CEILING - BAND_MARGIN
    s.line(x0, y(lim), 560, y(lim), "cp dash", 1.5)
    s.text(x0 + 4, y(lim) + 15, f"ceiling less the margin of {BAND_MARGIN}: {lim}", "m s")
    s.line(x0, base, 560, base, "axis")
    s.path(f"M{n(x0)},{n(y(a['now']))} L{n(x1)},{n(y(a['peak']))}", "s-orch", 2.5)
    s.circle(x0, y(a["now"]), 5, "orch")
    s.text(x0 + 10, y(a["now"]) + 18, f"now: {a['now']}% used", "t s b")
    s.text(330, 212, "the burn of running main threads and", "t s", "middle")
    s.text(330, 227, "helpers, projected to the reset", "t s", "middle")
    s.circle(x1, y(a["peak"]), 5, "orch")
    s.text(x1 - 10, y(a["peak"]) - 10, f"peak {a['peak']}% at the reset", "t s b halo", "end")
    bx = x1 + 22
    for i in range(3):
        lo = a["peak"] + i * a["each"]
        cls = "ok" if lo + a["each"] <= lim else "over"
        s.rect(bx, y(lo + a["each"]), 44, y(lo) - y(lo + a["each"]) - 1, cls, 2)
        s.text(bx + 22, y(lo + a["each"] / 2) + 4, f"+{a['each']}", "bg s b", "middle")
    s.text(x0, base + 20, f"now, {a['now_at']}", "m s", "middle")
    s.text(x1, base + 20, f"the reset, {a['reset_at']}", "m s", "middle")
    tx = 584
    s.lines(tx, 92, ["Each new helper adds", "its own burn until the", "reset."], "t s", 15)
    s.lines(tx, 160, [f"Room for {a['room']}: two more", f"fit under {lim}%. A third", "would cross."], "t s", 15)
    s.lines(tx, 228, ["The design defers it.", "Today the band only", "advises: the spawn goes",
                      "ahead. Room tells the", "orchestrator to pull", "work forward; at room",
                      "for 0 it waits for", "the reset."], "t s", 15)
    s.text(24, 368, "peak = now + the projected burn to the reset; admitted while peak + the new "
           f"helper's burn + {BAND_MARGIN} ≤ {BAND_CEILING}", "m s")
    return s.render()


# ---- 8 to 10. The band and the hook lines, as the plugin writes them --------------------
def _segments(line: str):
    """(start column, text) for each part of a band line, split on ' · '."""
    out, col = [], 0
    for part in line.split(" · "):
        out.append((col, part))
        col += len(part) + 3
    return out


def _term(s: Svg, x, y, w, h, title=None):
    s.rect(x, y, w, h, "term", 8)
    s.rect(x, y, w, h, "tedge", 8)
    s.add(f'<path d="M{n(x)},{n(y + 24)} L{n(x)},{n(y + 8)} Q{n(x)},{n(y)} {n(x + 8)},{n(y)} '
          f'L{n(x + w - 8)},{n(y)} Q{n(x + w)},{n(y)} {n(x + w)},{n(y + 8)} L{n(x + w)},{n(y + 24)} Z" '
          'class="tbar"/>')
    for i, c in enumerate(("#ff5f57", "#febc2e", "#28c840")):
        s.add(f'<circle cx="{n(x + 16 + i * 16)}" cy="{n(y + 12)}" r="5" style="fill:{c}"/>')
    if title:
        s.text(x + w / 2, y + 16, title, "td s", "middle")


def _band_line(s: Svg, tx, y, line, marks):
    """The line as tspans at fixed columns; marks: {part text: badge number}."""
    spans = []
    for i, (col, part) in enumerate(_segments(line)):
        if i:
            spans.append(f'<tspan x="{n(tx + (col - 3) * CW)}">{esc(" · ")}</tspan>')
        spans.append(f'<tspan x="{n(tx + col * CW)}">{esc(part)}</tspan>')
    s.add(f'<text y="{n(y)}" class="mono tt" xml:space="preserve">' + "".join(spans) + "</text>")
    for col, part in _segments(line):
        for key, num in marks.items():
            if part.startswith(key):
                off = len(part) - len(part.lstrip()) + (line.split(" · ")[0].find(key)
                                                        if col == 0 and key != part else 0)
                s.badge(tx + (col + off + len(key) / 2) * CW, y - 22, num)


def band() -> bytes:
    s = Svg(262, "The band above the prompt",
            "A terminal drawn from the session plugin's output: two lines above Claude Code's "
            "prompt. The first: session, opus 5.5, 1M, ctx 46%, turns 13%. The second: 5h 62% "
            "to 84%, ceiling 97, resets 14:05 in 1h12, 3 helpers, room for 2, 0 deferred, 7d "
            f"41%. Numbered marks 1 to 10 label each part. Drawn from the plugin's output at "
            f"{PLUGIN}.")
    s.text(24, 26, "The band above the prompt", "t h")
    _term(s, 16, 40, 728, 204, "claude")
    tx = 32
    s.text(tx, 88, "⏺ Read(src/example.py)", "mono td")
    first = BAND["clear"]
    s.add(f'<text x="{n(tx)}" y="132" class="mono tt" xml:space="preserve">'
          f'{esc(first)}</text>')
    head = "session: "
    for key, num in (("opus 5.5", 1), ("1M", 2), ("ctx 46%", 3), ("turns 13%", 4)):
        col = first.find(key, len(head) - 1)
        s.badge(tx + (col + len(key) / 2) * CW, 110, num)
    _band_line(s, tx, 178, BAND["five"], {"5h 62%": 5, "ceiling": 6, "resets": 7, "3 helpers": 8,
                                          "0 deferred": 9, "7d": 10})
    s.rect(28, 196, 704, 34, "tedge", 6)
    s.text(tx + 8, 218, ">", "mono tt")
    return s.render()


def states() -> bytes:
    s = Svg(338, "The band in four other states",
            "A terminal drawn from the session plugin's output, four lines: at the checkpoint "
            "the zone word notice; after the RESPAWN close, respawn marked; at the ceiling, "
            "exhausted; and a login with no five-hour window, which shows the week instead. "
            f"Numbered marks 11 to 15. Drawn from the plugin's output at {PLUGIN}.")
    s.text(24, 26, "The band in four other states", "t h")
    _term(s, 16, 40, 728, 284, "claude")
    tx = 32
    blocks = (("At the checkpoint, 80% of the ceiling", BAND["checkpoint"], (("notice", 11),), False),
              ("After the RESPAWN close", BAND["respawn"], (("respawn marked", 12),), False),
              ("At the ceiling", BAND["exit"], (("exhausted", 13),), False),
              ("A login with no five-hour window", BAND["none"],
               (("no 5h window", 14), ("week resets", 15)), True))
    for i, (lab, line, marks, right) in enumerate(blocks):
        y = 122 + i * 60
        s.text(744 - 16 if right else tx, y - 36, lab, "td s", "end" if right else "start")
        s.add(f'<text x="{n(tx)}" y="{n(y)}" class="mono tt" xml:space="preserve">'
              f'{esc(line)}</text>')
        for key, num in marks:
            col = line.find(key)
            s.badge(tx + (col + len(key) / 2) * CW, y - 22, num)
    return s.render()


def hooklines() -> bytes:
    s = Svg(472, "The lines the hooks add to the model's context",
            "Four blocks of the session plugin's hook output, wrapped for width: the meter line "
            "in the clear zone, the meter line and zone line past the checkpoint, the "
            "CHECKPOINT line under a launcher, and the EXIT line at the ceiling. Numbered marks "
            f"16 to 22. Drawn from the plugin's output at {PLUGIN}.")
    s.text(24, 26, "What the hooks add to the model's context", "t h")
    s.text(24, 45, "The model reads these lines; the band above the prompt is for you.", "m s")
    gx, tx = 38, 58
    blocks = (
        (f"On a prompt or a tool call in the clear zone, at most every {METER_LINE_MINUTES} minutes",
         [(METER_CLEAR, 16)]),
        ("On every prompt past the checkpoint", [(METER_PAST, None), (ZONE_LINE, 17)]),
        ("After a tool call at 80%, under a launcher; again every 10th call",
         [("CHECKPOINT: 80.1% context (320400/400000), 34.8% turns (139/400);", 18),
          ("charter <this sitting's charter>;", 19),
          ("bring the charter current with a Next act that opens RESPAWN:, commit,", 20),
          ("then run `agentik session checkpoint --respawn --charter <this sitting's", None),
          ("charter>` and end the turn; the launcher restarts this sitting;", None),
          ("tell the owner you are winding down at the meter's line, at 80.1%", 21)]),
        ("After every tool call at 100%, below the same CHECKPOINT line", [(EXIT_LINE, 22)]))
    assert " ".join(r for r, _ in blocks[2][1]) == CHECKPOINT_LINE, "wrapped, never edited"
    panel = len(s.parts)
    y = 86
    for lab, rows in blocks:
        s.text(gx - 10, y, lab, "m s")
        y += 20
        for text, num in rows:
            if num is not None:
                s.badge(gx, y - 4, num)
            s.text(tx, y, text, "mono t")
            y += 18
        y += 14
    s.parts[panel:panel] = [
        f'<rect x="16" y="58" width="728" height="{n(y - 58)}" class="{c}" rx="8"/>'
        for c in ("panel", "edge")]
    s.h = int(y + 16)
    return s.render()


FIGURES = {
    "lifecycle.svg": lifecycle, "ceilings.svg": ceilings, "peak-context.svg": histogram,
    "launcher-sequence.svg": launcher, "restarts-per-day.svg": restarts,
    "usage-november.svg": november,
    "admission-drawing.svg": admission, "band.svg": band, "band-states.svg": states,
    "hook-lines.svg": hooklines,
}


def main(argv) -> int:
    check = argv[1:] == ["--check"]
    if argv[1:] and not check:
        print("usage: tools/context_figures.py [--check]", file=sys.stderr)
        return 2
    stale = []
    for name, fn in FIGURES.items():
        body, path = fn(), OUT / name
        if check:
            if not path.is_file() or path.read_bytes() != body:
                stale.append(name)
        elif not path.is_file() or path.read_bytes() != body:
            OUT.mkdir(parents=True, exist_ok=True)
            path.write_bytes(body)
    for name in stale:
        print(f"context_figures: {name} differs from what the script writes", file=sys.stderr)
    # A figure the script no longer writes is a dropped figure left behind: say so in both modes.
    extra = sorted(p.name for p in OUT.glob("*.svg") if p.name not in FIGURES)
    for name in extra:
        print(f"context_figures: {name} is not written by the script; remove it", file=sys.stderr)
    return 1 if stale or extra else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

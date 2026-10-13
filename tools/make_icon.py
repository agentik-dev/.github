#!/usr/bin/python3
"""The agentik icon: a pixel-art agent drawn from a grid, written as SVG (crisp blocks) and PNG (stdlib zlib),
on a dark tile, a cream tile or transparent. Run: tools/make_icon.py [outdir]"""
import sys, zlib, struct, os

PAL = {"G": (0x88, 0xDC, 0x96), "S": (0x5F, 0xBF, 0x72), "K": (0x12, 0x29, 0x1A), "L": (0xC6, 0xF2, 0xCD)}
BG = {"cream": (0xF0, 0xEE, 0xE6), "dark": (0x1A, 0x1F, 0x1B)}

HEAD_VISOR = [
"................",
".......LL.......",
".......SS.......",
"...GGGGGGGGGG...",
"..GGGGGGGGGGGG..",
"..GKKKKKKKKKKG..",
"..GKLLKKKKLLKG..",
"..GGGGGGGGGGGG..",
"...GGGGGGGGGG...",
]
HEAD_EYES = HEAD_VISOR[:5] + ["..GGKKGGGGKKGG..", "..GGKKGGGGKKGG.."] + HEAD_VISOR[7:]
BODY = [
"................",
".GGGGGKKKKGGGGG.",
".GG.GGGKKGGG.GG.",
"....GGGKKGGG....",
"....GGGGGGGG....",
"....SSS..SSS....",
"....SSS..SSS....",
]
# The agentik agent: a visor and a tie; the alternate has two eyes.
VARIANTS = {"agentik": HEAD_VISOR + BODY, "agentik-alt": HEAD_EYES + BODY}

def render(grid, size, bg, pad_frac=0.16, radius_frac=0.18):
    n = len(grid); w = len(grid[0])
    inner = size * (1 - 2 * pad_frac)
    cell = int(inner // max(n, w))
    ox = (size - cell * w) // 2
    rows_used = [i for i, r in enumerate(grid) if r.strip(".")]
    top, bot = rows_used[0], rows_used[-1]
    oy = (size - cell * (bot - top + 1)) // 2 - top * cell
    px = [[None] * size for _ in range(size)]
    if bg:
        rad = int(size * radius_frac)
        for y in range(size):
            for x in range(size):
                dx = max(rad - x, x - (size - 1 - rad), 0); dy = max(rad - y, y - (size - 1 - rad), 0)
                if dx * dx + dy * dy <= rad * rad:
                    px[y][x] = BG[bg] + (255,)
    for r, row in enumerate(grid):
        for c, ch in enumerate(row):
            if ch in PAL:
                for y in range(oy + r * cell, oy + (r + 1) * cell):
                    for x in range(ox + c * cell, ox + (c + 1) * cell):
                        px[y][x] = PAL[ch] + (255,)
    return px

def png(px, path):
    size = len(px)
    raw = b"".join(b"\x00" + b"".join(bytes(p if p else (0, 0, 0, 0)) for p in row) for row in px)
    def chunk(t, d): return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    data = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    open(path, "wb").write(data)

def svg(grid, bg, path, view=240, pad_frac=0.16, radius_frac=0.18):
    n = len(grid); w = len(grid[0])
    cell = (view * (1 - 2 * pad_frac)) / max(n, w)
    rows_used = [i for i, r in enumerate(grid) if r.strip(".")]
    top, bot = rows_used[0], rows_used[-1]
    ox = (view - cell * w) / 2; oy = (view - cell * (bot - top + 1)) / 2 - top * cell
    hexc = lambda c: "#%02X%02X%02X" % c
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" shape-rendering="crispEdges">' % (view, view)]
    if bg:
        out.append('<rect width="%d" height="%d" rx="%g" fill="%s"/>' % (view, view, view * radius_frac, hexc(BG[bg])))
    for r, row in enumerate(grid):
        for c, ch in enumerate(row):
            if ch in PAL:
                out.append('<rect x="%g" y="%g" width="%g" height="%g" fill="%s"/>' % (ox + c * cell, oy + r * cell, cell + 0.01, cell + 0.01, hexc(PAL[ch])))
    out.append("</svg>")
    open(path, "w").write("\n".join(out) + "\n")

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "assets"
    for name, grid in VARIANTS.items():
        for bg in ("dark", "cream", None):
            tag = bg or "clear"
            png(render(grid, 1024, bg), os.path.join(out, f"{name}-{tag}-1024.png"))
            svg(grid, bg, os.path.join(out, f"{name}-{tag}.svg"))

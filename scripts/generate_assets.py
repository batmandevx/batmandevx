"""Generates the animated SVG assets for the GitHub profile README."""
import math
import random
import sys
from pathlib import Path

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "assets")
OUT.mkdir(exist_ok=True)

CY, VI, PK, GR = "#22D3EE", "#A78BFA", "#F472B6", "#4ADE80"
BG, PANEL, BORDER, TXT, MUTED = "#0D1117", "#161B22", "#30363D", "#E6EDF3", "#8B949E"
FONT = "font-family: 'Fira Code','JetBrains Mono','DejaVu Sans Mono',Menlo,Consolas,monospace;"


def write(name, body):
    (OUT / name).write_text(body)
    print("wrote", OUT / name, len(body), "bytes")


# ───────────────────────────── bat shape ─────────────────────────────
def quad(p0, c, p1, n=6):
    pts = []
    for i in range(1, n + 1):
        t = i / n
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t * t * p1[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t * t * p1[1]
        pts.append((x, y))
    return pts


def bat_polygon():
    """Classic bat emblem, ~100 wide, centred on (0,0)."""
    r = [(0, -9), (4.5, -9), (7, -20), (9.5, -7), (15, -8.5)]
    r += quad((15, -8.5), (24, -12), (30, -19))[:-1]
    r += quad((30, -19), (38, -20), (50, -17))
    r += quad((50, -17), (42, -9), (45, 2))
    # scallops along the bottom edge (concave, curving upward)
    bottom = [(45, 2), (35, 1), (30, 9), (23, 3), (16, 12), (9, 6), (0, 21)]
    for a, b in zip(bottom, bottom[1:]):
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        r += quad(a, (mx, my - 6), b, 5)
    left = [(-x, y) for x, y in reversed(r[1:-1])]
    return r + left


BAT = bat_polygon()


def bat_path(scale=1.0, cx=0.0, cy=0.0):
    pts = [(cx + x * scale, cy + y * scale) for x, y in BAT]
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + "Z"


def inside(pt, poly):
    x, y = pt
    c = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            c = not c
        j = i
    return c


def bat_ascii(cols=64, rows=14):
    """Rasterize the bat into half-block characters (2 pixel-rows per line)."""
    ys = [y for _, y in BAT]
    ymin, ymax = min(ys) - 1, max(ys) + 1
    lines = []
    for r in range(rows):
        line = ""
        for c in range(cols):
            x = -51 + (c + 0.5) * 102 / cols
            top = inside((x, ymin + (2 * r + 0.5) * (ymax - ymin) / (2 * rows)), BAT)
            bot = inside((x, ymin + (2 * r + 1.5) * (ymax - ymin) / (2 * rows)), BAT)
            line += "█" if top and bot else "▀" if top else "▄" if bot else " "
        lines.append(line)
    return lines


def flap_bat(x, y, s, dur, begin, color="#05060c"):
    up = "M0,0 Q-6,-8 -14,-7 Q-10,-2 -9,2 Q-5,0 0,3 Q5,0 9,2 Q10,-2 14,-7 Q6,-8 0,0Z"
    dn = "M0,0 Q-6,2 -14,8 Q-9,6 -8,9 Q-4,4 0,3 Q4,4 8,9 Q9,6 14,8 Q6,2 0,0Z"
    return (f'<g transform="translate({x},{y}) scale({s})"><path fill="{color}" d="{up}">'
            f'<animate attributeName="d" values="{up};{dn};{up}" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/></path></g>')


# ───────────────────────────── 1. gotham hero ─────────────────────────────
def gotham():
    random.seed(7)
    W, H = 900, 320
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f"""<defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#05060F"/><stop offset="55%" stop-color="#140F2E"/><stop offset="100%" stop-color="#2A1640"/>
  </linearGradient>
  <radialGradient id="sig" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="#FEF9C3" stop-opacity="0.95"/><stop offset="70%" stop-color="#FDE68A" stop-opacity="0.75"/><stop offset="100%" stop-color="#FACC15" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="beam" x1="0" y1="1" x2="0" y2="0">
    <stop offset="0%" stop-color="#FDE68A" stop-opacity="0.55"/><stop offset="100%" stop-color="#FDE68A" stop-opacity="0.05"/>
  </linearGradient>
  <radialGradient id="moon" cx="40%" cy="40%" r="60%"><stop offset="0%" stop-color="#F8FAFC"/><stop offset="100%" stop-color="#C4B5FD"/></radialGradient>
  <linearGradient id="haze" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="{CY}"/><stop offset="50%" stop-color="{VI}"/><stop offset="100%" stop-color="{PK}"/>
  </linearGradient>
  <filter id="blur"><feGaussianBlur stdDeviation="9"/></filter>
  <filter id="soft"><feGaussianBlur stdDeviation="2"/></filter>
  <clipPath id="frame"><rect width="{W}" height="{H}" rx="16"/></clipPath>
</defs>
<style>
  text {{ {FONT} }}
  .tw {{ animation: tw 3s ease-in-out infinite; }}
  @keyframes tw {{ 0%,100% {{ opacity: .15; }} 50% {{ opacity: 1; }} }}
  .fl {{ animation: fl 5s steps(1) infinite; }}
  @keyframes fl {{ 0%,40%,100% {{ opacity: .9; }} 41%,44% {{ opacity: .15; }} 45%,70% {{ opacity: .9; }} 71% {{ opacity: .3; }} }}
  .hum {{ animation: hum 2.4s ease-in-out infinite; }}
  @keyframes hum {{ 0%,100% {{ opacity: .85; }} 50% {{ opacity: 1; }} }}
</style>
<g clip-path="url(#frame)">
<rect width="{W}" height="{H}" fill="url(#sky)"/>"""]
    # stars
    for _ in range(90):
        x, y = random.uniform(0, W), random.uniform(0, 190)
        r = random.choice([0.6, 0.8, 1.0, 1.3, 1.7])
        col = random.choice(["#FFFFFF"] * 5 + [CY, VI, PK])
        o.append(f'<circle class="tw" style="animation-delay:{random.uniform(0,3):.2f}s;animation-duration:{random.uniform(2,5):.1f}s" '
                 f'cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{col}"/>')
    # shooting star
    o.append(f'<g opacity="0"><line x1="0" y1="0" x2="70" y2="0" stroke="url(#haze)" stroke-width="2" stroke-linecap="round"/>'
             f'<animateTransform attributeName="transform" type="translate" values="80,30;380,110" dur="7s" keyTimes="0;1" '
             f'begin="1s" repeatCount="indefinite" calcMode="spline" keySplines=".4 0 .6 1"/>'
             f'<animate attributeName="opacity" values="0;1;0;0" keyTimes="0;.06;.14;1" dur="7s" begin="1s" repeatCount="indefinite"/></g>')
    # moon
    o.append(f'<circle cx="790" cy="70" r="46" fill="{VI}" opacity=".25" filter="url(#blur)"/>'
             f'<circle cx="790" cy="70" r="30" fill="url(#moon)"/>'
             f'<circle cx="780" cy="62" r="5" fill="#A78BFA" opacity=".25"/><circle cx="799" cy="80" r="7" fill="#A78BFA" opacity=".2"/>'
             f'<circle cx="801" cy="58" r="3" fill="#A78BFA" opacity=".25"/>')
    # clouds drifting
    for cx, cy, rx, dur, d in [(140, 120, 120, 40, 0), (520, 70, 150, 55, -20), (760, 150, 110, 45, -10)]:
        o.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="16" fill="#3B2A6B" opacity=".45" filter="url(#blur)">'
                 f'<animateTransform attributeName="transform" type="translate" values="-60,0;60,0;-60,0" dur="{dur}s" begin="{d}s" repeatCount="indefinite"/></ellipse>')
    # bat signal: beam + emblem, swaying around the rooftop spotlight
    sx, sy = 640, 258
    o.append(f'<g><animateTransform attributeName="transform" type="rotate" values="-3 {sx} {sy};3 {sx} {sy};-3 {sx} {sy}" '
             f'dur="8s" repeatCount="indefinite" calcMode="spline" keyTimes="0;.5;1" keySplines=".45 0 .55 1;.45 0 .55 1"/>'
             f'<polygon class="hum" points="{sx-6},{sy} {sx+6},{sy} 545,140 335,140" fill="url(#beam)"/>'
             f'<ellipse cx="440" cy="98" rx="150" ry="74" fill="#FDE68A" opacity=".25" filter="url(#blur)"/>'
             f'<ellipse class="hum" cx="440" cy="98" rx="118" ry="56" fill="url(#sig)"/>'
             f'<path d="{bat_path(1.9, 440, 100)}" fill="#0A0A14" opacity=".92"/></g>')
    # skyline
    random.seed(11)
    x = -10
    windows = []
    blds = []
    while x < W + 10:
        w = random.choice([34, 42, 50, 58, 66])
        h = random.randint(55, 150)
        if 600 < x < 680:
            h = 62  # rooftop under the spotlight
        blds.append((x, h, w))
        x += w + random.choice([0, 2, 4])
    for x, h, w in blds:
        top = H - h
        o.append(f'<rect x="{x}" y="{top}" width="{w}" height="{h}" fill="#080A14"/>')
        o.append(f'<rect x="{x}" y="{top}" width="{w}" height="1.5" fill="{VI}" opacity=".35"/>')
        if random.random() < 0.3:
            o.append(f'<rect x="{x + w/2 - 1}" y="{top - 16}" width="2" height="16" fill="#080A14"/>'
                     f'<circle class="tw" style="animation-duration:1.4s" cx="{x + w/2}" cy="{top - 17}" r="2" fill="#F87171"/>')
        for wy in range(top + 10, H - 8, 13):
            for wx in range(x + 6, x + w - 8, 10):
                if random.random() < 0.38:
                    col = random.choice(["#FDE68A"] * 6 + [CY, VI, PK])
                    cls = ' class="fl"' if random.random() < 0.18 else ""
                    sty = f' style="animation-delay:{random.uniform(0,5):.1f}s"' if cls else ""
                    windows.append(f'<rect{cls}{sty} x="{wx}" y="{wy}" width="5" height="6" fill="{col}" opacity=".85"/>')
    o += windows
    # spotlight housing
    o.append(f'<rect x="{sx-9}" y="{sy-2}" width="18" height="10" rx="2" fill="#1F2937" stroke="#FDE68A" stroke-width="1"/>'
             f'<circle cx="{sx}" cy="{sy}" r="5" fill="#FEF9C3" filter="url(#soft)"/>')
    # flying bats
    for path, s, dur, begin in [("M-40,150 C200,80 400,200 960,110", 1.0, 13, 0),
                                ("M-40,60 C300,120 600,30 960,90", 0.7, 17, -6),
                                ("M960,180 C700,120 300,160 -40,70", 0.85, 15, -3),
                                ("M-40,200 C250,150 500,230 960,170", 0.55, 21, -12)]:
        o.append(f'<g><animateMotion dur="{dur}s" begin="{begin}s" repeatCount="indefinite" path="{path}"/>'
                 f'{flap_bat(0, 0, s, round(0.32 + s * 0.1, 2), 0, "#0B0B16")}</g>')
    # neon horizon + labels
    o.append(f'<rect x="0" y="{H-3}" width="{W}" height="3" fill="url(#haze)"/>')
    o.append(f'<text x="24" y="34" font-size="13" fill="{MUTED}">// gotham.local</text>'
             f'<text x="24" y="54" font-size="13" fill="{VI}">night-shift AI engineer</text>')
    o.append(f'<g transform="translate(724,300)"><rect x="0" y="-14" width="156" height="20" rx="10" fill="{BG}" stroke="{BORDER}"/>'
             f'<circle class="tw" style="animation-duration:1.6s" cx="14" cy="-4" r="4" fill="{GR}"/>'
             f'<text x="25" y="0" font-size="11" fill="{TXT}">signal: always on</text></g>')
    o.append("</g>")
    o.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="16" fill="none" stroke="url(#haze)" stroke-opacity=".6" stroke-width="2"/>')
    o.append("</svg>")
    write("gotham.svg", "\n".join(o))


# ───────────────────────────── pixel helpers ─────────────────────────────
def pixels(rows, palette, size, ox=0, oy=0, cls=None):
    out = []
    width = len(rows[0])
    for r, row in enumerate(rows):
        assert len(row) == width, (r, row, len(row), width)
        c = 0
        while c < len(row):
            ch = row[c]
            if ch == ".":
                c += 1
                continue
            run = 1
            while c + run < len(row) and row[c + run] == ch:
                run += 1
            out.append(f'<rect x="{ox + c*size}" y="{oy + r*size}" width="{run*size}" height="{size}" fill="{palette[ch]}"/>')
            c += run
    return "".join(out)


CAT_PAL = {"K": "#2B2340", "F": "#EDE9FE", "S": "#C4B5FD", "P": "#F9A8D4",
           "E": "#0E7490", "W": "#FFFFFF", "B": "#F9A8D4", "N": "#F472B6"}


# ───────────────────────────── 2. cat coder ─────────────────────────────
def cat_coder():
    W, H = 420, 330
    S = 9
    head = [
        "...KK..............KK...",
        "..KPPK............KPPK..",
        "..KPPFK..........KFPPK..",
        "..KFPFFKKKKKKKKKKFFPFK..",
        "..KFFFFFFFFFFFFFFFFFFK..",
        ".KFFFFFFFFFFFFFFFFFFFFK.",
        ".KFFFFFFFFFFFFFFFFFFFFK.",
        ".KFFF...FFFFFFFF...FFFK.",
        ".KFFF...FFFFFFFF...FFFK.",
        ".KFFF...FFFFFFFF...FFFK.",
        ".KFBBFFFFFFNNFFFFFFBBFK.",
        ".KFFFFFFFFKFFKFFFFFFFFK.",
        "..KFFFFFFFFKKFFFFFFFFK..",
        "...KKFFFFFFFFFFFFFFKK...",
        "...KSFFFFFFFFFFFFFFSK...",
        "..KSFFFFFFFFFFFFFFFFSK..",
        "..KSFFFFFFFFFFFFFFFFSK..",
    ]
    eye = ["EEE", "EWE", "EEE"]
    hx, hy = 102, 40  # head origin
    ears_l = head[:3]
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f"""<defs>
  <linearGradient id="lid" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#1F2433"/><stop offset="100%" stop-color="#11141C"/></linearGradient>
  <radialGradient id="glowc" cx="50%" cy="100%" r="70%"><stop offset="0%" stop-color="{CY}" stop-opacity=".35"/><stop offset="100%" stop-color="{CY}" stop-opacity="0"/></radialGradient>
  <linearGradient id="haze" x1="0" x2="1"><stop offset="0%" stop-color="{CY}"/><stop offset="50%" stop-color="{VI}"/><stop offset="100%" stop-color="{PK}"/></linearGradient>
  <filter id="g"><feGaussianBlur stdDeviation="3"/></filter>
</defs>
<style>
  text {{ {FONT} }}
  .blink {{ animation: blink 4s infinite; transform-box: fill-box; transform-origin: center; }}
  @keyframes blink {{ 0%,44%,50%,100% {{ transform: scaleY(1); }} 47% {{ transform: scaleY(.1); }} }}
  .ear {{ animation: ear 6s infinite; transform-box: fill-box; transform-origin: 50% 100%; }}
  @keyframes ear {{ 0%,80%,90%,100% {{ transform: rotate(0); }} 85% {{ transform: rotate(-12deg); }} }}
  .tail {{ animation: tail 1.8s ease-in-out infinite; transform-origin: 300px 250px; }}
  @keyframes tail {{ 0%,100% {{ transform: rotate(-8deg); }} 50% {{ transform: rotate(10deg); }} }}
  .pawl {{ animation: tap .32s steps(1) infinite; }}
  .pawr {{ animation: tap .32s steps(1) infinite; animation-delay: .16s; }}
  @keyframes tap {{ 0% {{ transform: translateY(0); }} 50% {{ transform: translateY(5px); }} }}
  .rise {{ opacity: 0; animation: rise 3.6s ease-out infinite; }}
  @keyframes rise {{ 0% {{ opacity: 0; transform: translateY(0); }} 15% {{ opacity: 1; }} 100% {{ opacity: 0; transform: translateY(-90px); }} }}
  .pulse {{ animation: pulse 2s ease-in-out infinite; }}
  @keyframes pulse {{ 0%,100% {{ opacity: .55; }} 50% {{ opacity: 1; }} }}
  .bob {{ animation: bob 3s ease-in-out infinite; }}
  @keyframes bob {{ 0%,100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-3px); }} }}
</style>
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="16" fill="{BG}" stroke="{BORDER}" stroke-width="1.5"/>
<text x="20" y="28" font-size="12" fill="{MUTED}">~/cat.exe</text>
<text x="{W-20}" y="28" font-size="12" fill="{PK}" text-anchor="end">pair programmer</text>"""]
    # tail (behind body)
    tail = ("M300,252 C330,250 345,230 340,205 C337,190 352,180 360,192")
    o.append(f'<g class="tail"><path d="{tail}" fill="none" stroke="#2B2340" stroke-width="16" stroke-linecap="round"/>'
             f'<path d="{tail}" fill="none" stroke="#EDE9FE" stroke-width="9" stroke-linecap="round"/></g>')
    o.append('<g class="bob">')
    # ears separately so they can twitch
    o.append(f'<g class="ear">{pixels([r[:12] for r in ears_l], CAT_PAL, S, hx, hy)}</g>')
    o.append(f'<g class="ear" style="animation-delay:.3s">{pixels([r[12:] for r in ears_l], CAT_PAL, S, hx + 12*S, hy)}</g>')
    o.append(pixels(head[3:], CAT_PAL, S, hx, hy + 3*S))
    # screen glow on face
    o.append(f'<ellipse cx="{hx + 12*S}" cy="{hy + 16*S}" rx="{9*S}" ry="{5*S}" fill="{CY}" opacity=".22" filter="url(#g)"/>')
    for ex in (5, 16):
        o.append(f'<g class="blink">{pixels(eye, CAT_PAL, S, hx + ex*S, hy + 7*S)}</g>')
    o.append("</g>")
    # laptop lid (back faces the viewer)
    lx, ly, lw, lh = 70, 200, 280, 104
    o.append(f'<rect x="{lx-8}" y="{ly-6}" width="{lw+16}" height="{lh+12}" rx="14" fill="{CY}" opacity=".18" filter="url(#g)"/>'
             f'<rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="10" fill="url(#lid)" stroke="#3B4256" stroke-width="2"/>')
    o.append(f'<path class="pulse" d="{bat_path(0.9, lx + lw/2, ly + lh/2)}" fill="url(#haze)"/>')
    o.append(f'<rect x="{lx-20}" y="{ly+lh}" width="{lw+40}" height="9" rx="4" fill="#3B4256"/>')
    # paws on the lid edge, tapping
    paw = [".KKKK.", "KFFFFK", "KFPFPK"]
    o.append(f'<g class="pawl">{pixels(paw, CAT_PAL, 6, 138, ly - 12)}</g>')
    o.append(f'<g class="pawr">{pixels(paw, CAT_PAL, 6, 246, ly - 12)}</g>')
    # rising code + hearts
    heart = "M0,3 C0,-1 -6,-2 -6,2 C-6,5 0,8 0,10 C0,8 6,5 6,2 C6,-2 0,-1 0,3Z"
    items = [("&lt;/&gt;", CY, 46, 190, 0), ("{ }", VI, 362, 185, 1.2), ("01", GR, 40, 120, 2.4),
             ("fn()", PK, 352, 120, 0.6), ("=&gt;", CY, 372, 250, 1.8)]
    for t, col, x, y, d in items:
        o.append(f'<text class="rise" style="animation-delay:{d}s" x="{x}" y="{y}" font-size="14" font-weight="700" fill="{col}" text-anchor="middle">{t}</text>')
    for x, y, d, s in [(75, 160, 0.9, 1.3), (345, 165, 2.1, 1.1), (60, 230, 3.0, 1.0)]:
        o.append(f'<g transform="translate({x},{y}) scale({s})"><path class="rise" style="animation-delay:{d}s" d="{heart}" fill="{PK}"/></g>')
    o.append("</svg>")
    write("cat-coder.svg", "\n".join(o))


# ───────────────────────────── 3. walking-cat divider ─────────────────────────────
def cat_divider():
    W, H, S = 900, 48, 3
    body = [
        ".............K..K.",
        "............KFKKFK",
        "K...........KFFFFK",
        "KF..........KFEFEK",
        ".KF.........KFFFPK",
        "..KKKKKKKKKKKFFFK.",
        "...KFFFFFFFFFFFFK.",
        "...KFFFFFFFFFFFK..",
    ]
    legs_a = ["...KFKKFFFFFKFK...", "...KK.KK...KK.KK.."]
    legs_b = ["...KFFKFFFFKFFK...", "....KK.KK.KK.KK..."]
    pal = CAT_PAL | {"E": "#2B2340", "P": "#F472B6"}
    sprite_h = (len(body) + 2) * S
    y0 = H - 10 - sprite_h
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f"""<defs><linearGradient id="d" x1="0" x2="1">
  <stop offset="0%" stop-color="{CY}" stop-opacity="0"/><stop offset="25%" stop-color="{CY}"/><stop offset="50%" stop-color="{VI}"/>
  <stop offset="75%" stop-color="{PK}"/><stop offset="100%" stop-color="{PK}" stop-opacity="0"/></linearGradient></defs>
<style>
  .a {{ animation: a .36s steps(1) infinite; }} .b {{ animation: b .36s steps(1) infinite; }}
  @keyframes a {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0; }} }} @keyframes b {{ 0% {{ opacity: 0; }} 50% {{ opacity: 1; }} }}
  .hop {{ animation: hop .36s ease-in-out infinite; }}
  @keyframes hop {{ 0%,100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-1.5px); }} }}
  .tw {{ animation: tw 1.8s ease-in-out infinite; }} @keyframes tw {{ 0%,100% {{ opacity: 0; }} 50% {{ opacity: 1; }} }}
</style>
<rect x="0" y="{H-9}" width="{W}" height="2" fill="url(#d)" opacity=".6"/>"""]
    for i in range(9):
        x = 60 + i * 95
        o.append(f'<circle class="tw" style="animation-delay:{i*0.37:.2f}s" cx="{x}" cy="{10 + (i%3)*6}" r="1.6" fill="{[CY,VI,PK][i%3]}"/>')
    o.append(f'<g><animateTransform attributeName="transform" type="translate" values="-70,0;{W+10},0" dur="16s" repeatCount="indefinite"/>'
             f'<g class="hop">{pixels(body, pal, S, 0, y0)}'
             f'<g class="a">{pixels(legs_a, pal, S, 0, y0 + len(body)*S)}</g>'
             f'<g class="b">{pixels(legs_b, pal, S, 0, y0 + len(body)*S)}</g></g></g>')
    o.append("</svg>")
    write("cat-divider.svg", "\n".join(o))


# ───────────────────────────── 4. RAG pipeline ─────────────────────────────
def pipeline():
    W, H = 900, 270
    nodes = [("query", "user intent", CY), ("embed", "text → vectors", CY), ("retrieve", "top-k chunks", VI),
             ("rerank", "cross-encoder", VI), ("generate", "LLM + context", PK), ("answer", "grounded + cited", GR)]
    nw, nh, y = 122, 70, 105
    xs = [20 + i * 147 for i in range(6)]
    cycle = 6.0
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f"""<defs>
  <linearGradient id="haze" x1="0" x2="1"><stop offset="0%" stop-color="{CY}"/><stop offset="50%" stop-color="{VI}"/><stop offset="100%" stop-color="{PK}"/></linearGradient>
  <filter id="gl" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="4"/></filter>
</defs>
<style>
  text {{ {FONT} }}
  .flow {{ stroke-dasharray: 4 8; animation: flow .8s linear infinite; }}
  @keyframes flow {{ to {{ stroke-dashoffset: -12; }} }}
  .card {{ opacity: 0; animation: rise .6s cubic-bezier(.2,.8,.2,1) forwards; }}
  @keyframes rise {{ from {{ opacity: 0; transform: translateY(14px); }} to {{ opacity: 1; transform: translateY(0); }} }}
</style>
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="16" fill="{BG}" stroke="{BORDER}" stroke-width="1.5"/>
<text x="24" y="38" font-size="14" fill="{MUTED}"><tspan fill="{VI}">&gt;</tspan> how a question travels through my systems</text>
<text x="{W-24}" y="38" font-size="12" fill="{MUTED}" text-anchor="end">rag.pipeline()</text>"""]
    # connectors
    for i in range(5):
        x1, x2 = xs[i] + nw, xs[i + 1]
        o.append(f'<line class="flow" x1="{x1+2}" y1="{y+nh/2}" x2="{x2-2}" y2="{y+nh/2}" stroke="{nodes[i][2]}" stroke-width="2" stroke-linecap="round"/>')
        o.append(f'<path d="M{x2-8},{y+nh/2-4} L{x2-2},{y+nh/2} L{x2-8},{y+nh/2+4}" fill="none" stroke="{nodes[i][2]}" stroke-width="2"/>')
    # feedback loop
    lp = f"M{xs[5]+nw/2},{y+nh+2} C{xs[5]+nw/2},{y+nh+70} {xs[0]+nw/2},{y+nh+70} {xs[0]+nw/2},{y+nh+2}"
    o.append(f'<path class="flow" d="{lp}" fill="none" stroke="url(#haze)" stroke-width="1.5" opacity=".55"/>')
    o.append(f'<rect x="{W/2-120}" y="{y+nh+44}" width="240" height="24" rx="12" fill="{PANEL}" stroke="{BORDER}"/>'
             f'<text x="{W/2}" y="{y+nh+60}" font-size="12" fill="{TXT}" text-anchor="middle">evals → feedback → fine-tune</text>')
    o.append(f'<circle r="4" fill="{PK}" filter="url(#gl)"><animateMotion dur="{cycle}s" begin="{cycle*0.85:.2f}s" repeatCount="indefinite" path="{lp}" keyPoints="0;1;1" keyTimes="0;.35;1" calcMode="linear"/></circle>')
    o.append(f'<circle r="2.5" fill="#fff"><animateMotion dur="{cycle}s" begin="{cycle*0.85:.2f}s" repeatCount="indefinite" path="{lp}" keyPoints="0;1;1" keyTimes="0;.35;1" calcMode="linear"/></circle>')
    # main packet
    mp = f"M{xs[0]+nw/2},{y+nh/2} L{xs[5]+nw/2},{y+nh/2}"
    for r, col, filt in [(6, CY, ' filter="url(#gl)"'), (3, "#fff", "")]:
        o.append(f'<circle r="{r}" fill="{col}"{filt}><animateMotion dur="{cycle}s" repeatCount="indefinite" path="{mp}" '
                 f'keyPoints="0;1;1" keyTimes="0;.85;1" calcMode="linear"/>'
                 f'<animate attributeName="fill" values="{CY};{VI};{PK};{GR};{GR}" keyTimes="0;.35;.6;.85;1" dur="{cycle}s" repeatCount="indefinite"/></circle>')
    # nodes
    for i, ((name, sub, col), x) in enumerate(zip(nodes, xs)):
        t = i * 0.85 / 5  # moment the packet reaches this node (fraction of cycle)
        a, b = max(t - 0.04, 0.0), min(t + 0.10, 0.999)
        o.append(f'<g class="card" style="animation-delay:{0.15 + i*0.12:.2f}s">')
        o.append(f'<rect x="{x}" y="{y}" width="{nw}" height="{nh}" rx="12" fill="{PANEL}" stroke="{BORDER}" stroke-width="1.5"/>')
        kt = f"0;{a:.3f};{t+0.001:.3f};{b:.3f};1" if a > 0 else f"0;{t+0.001:.3f};{b:.3f};{b+0.001:.3f};1"
        vals = "0;0;1;0;0" if a > 0 else "1;1;0;0;0"
        o.append(f'<rect x="{x}" y="{y}" width="{nw}" height="{nh}" rx="12" fill="none" stroke="{col}" stroke-width="2.5" filter="url(#gl)" opacity="0">'
                 f'<animate attributeName="opacity" values="{vals}" keyTimes="{kt}" dur="{cycle}s" repeatCount="indefinite"/></rect>')
        o.append(f'<rect x="{x}" y="{y}" width="{nw}" height="{nh}" rx="12" fill="none" stroke="{col}" stroke-width="1.5" opacity=".35"/>')
        o.append(f'<text x="{x+14}" y="{y+22}" font-size="10" fill="{col}">0{i+1}</text>')
        o.append(f'<text x="{x+nw/2}" y="{y+40}" font-size="15" font-weight="700" fill="{TXT}" text-anchor="middle">{name}</text>')
        o.append(f'<text x="{x+nw/2}" y="{y+58}" font-size="10.5" fill="{MUTED}" text-anchor="middle">{sub}</text>')
        o.append("</g>")
    # tiny vector bars above embed / retrieve
    for j in range(8):
        bx = xs[1] + 22 + j * 10
        h0 = 6 + (j * 7) % 14
        o.append(f'<rect x="{bx}" y="{y-6-h0}" width="6" height="{h0}" rx="1.5" fill="{CY}" opacity=".7">'
                 f'<animate attributeName="height" values="{h0};{20-h0/2:.0f};{h0}" dur="{1.2 + j*0.1:.1f}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="y" values="{y-6-h0};{y-6-(20-h0/2):.0f};{y-6-h0}" dur="{1.2 + j*0.1:.1f}s" repeatCount="indefinite"/></rect>')
    for j in range(3):
        o.append(f'<rect x="{xs[2]+20 + j*28}" y="{y-24}" width="22" height="14" rx="3" fill="none" stroke="{VI}" stroke-width="1.2">'
                 f'<animate attributeName="opacity" values=".25;1;.25" dur="1.8s" begin="{j*0.3}s" repeatCount="indefinite"/></rect>')
    o.append("</svg>")
    write("pipeline.svg", "\n".join(o))


# ───────────────────────────── 5. stack orbit ─────────────────────────────
def orbit():
    W, H = 900, 380
    cx, cy = 450, 190
    tilt = -7
    rings = [
        (170, 56, 18, CY, ["Python", "PyTorch", "TensorFlow"]),
        (290, 96, 28, VI, ["C++", "TypeScript", "Java", "Kotlin", "C"]),
        (415, 140, 40, PK, ["React", "Next.js", "Node", "FastAPI", "NestJS", "Angular", "Lua"]),
    ]
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f"""<defs>
  <radialGradient id="core" cx="40%" cy="35%" r="70%"><stop offset="0%" stop-color="#fff"/><stop offset="35%" stop-color="{VI}"/><stop offset="100%" stop-color="#4C1D95"/></radialGradient>
  <radialGradient id="halo"><stop offset="0%" stop-color="{VI}" stop-opacity=".55"/><stop offset="100%" stop-color="{VI}" stop-opacity="0"/></radialGradient>
  <filter id="gl" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3"/></filter>
</defs>
<style>
  text {{ {FONT} }}
  .ring {{ stroke-dasharray: 2 7; animation: spin 3s linear infinite; }}
  @keyframes spin {{ to {{ stroke-dashoffset: -90; }} }}
  .breathe {{ animation: br 3s ease-in-out infinite; transform-origin: {cx}px {cy}px; }}
  @keyframes br {{ 0%,100% {{ transform: scale(1); }} 50% {{ transform: scale(1.12); }} }}
  .tw {{ animation: tw 3s ease-in-out infinite; }} @keyframes tw {{ 0%,100% {{ opacity: .1; }} 50% {{ opacity: .8; }} }}
</style>
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="16" fill="{BG}" stroke="{BORDER}" stroke-width="1.5"/>"""]
    random.seed(3)
    for _ in range(50):
        o.append(f'<circle class="tw" style="animation-delay:{random.uniform(0,3):.1f}s" cx="{random.uniform(10,W-10):.0f}" '
                 f'cy="{random.uniform(10,H-10):.0f}" r="{random.choice([.7,1,1.4])}" fill="#fff"/>')
    o.append(f'<text x="24" y="34" font-size="13" fill="{MUTED}"><tspan fill="{VI}">&gt;</tspan> stack.orbit()</text>')
    legend = [(CY, "ai / ml"), (VI, "languages"), (PK, "web &amp; backend")]
    for i, (c, l) in enumerate(legend):
        o.append(f'<circle cx="{W-200 + 0}" cy="{28 + i*18}" r="4" fill="{c}"/><text x="{W-188}" y="{32 + i*18}" font-size="11" fill="{MUTED}">{l}</text>')
    th = math.radians(tilt)

    def rot(x, y):
        return cx + x * math.cos(th) - y * math.sin(th), cy + x * math.sin(th) + y * math.cos(th)

    back, front = [], []
    for rx, ry, dur, col, items in rings:
        (ax, ay), (bx, by) = rot(rx, 0), rot(-rx, 0)
        path = f"M{ax:.1f},{ay:.1f} A{rx},{ry} {tilt} 1 0 {bx:.1f},{by:.1f} A{rx},{ry} {tilt} 1 0 {ax:.1f},{ay:.1f}"
        back.append(f'<path class="ring" d="{path}" fill="none" stroke="{col}" stroke-opacity=".45" stroke-width="1.5"/>')
        for k, label in enumerate(items):
            w = len(label) * 7.4 + 22
            begin = -dur * k / len(items)
            # t=0 right, .25 top (far), .5 left, .75 bottom (near)
            front.append(
                f'<g><animateMotion dur="{dur}s" begin="{begin:.2f}s" repeatCount="indefinite" path="{path}"/>'
                f'<g><animateTransform attributeName="transform" type="scale" values="1;.72;1;1.22;1" keyTimes="0;.25;.5;.75;1" '
                f'dur="{dur}s" begin="{begin:.2f}s" repeatCount="indefinite" calcMode="spline" keySplines=".4 0 .6 1;.4 0 .6 1;.4 0 .6 1;.4 0 .6 1"/>'
                f'<animate attributeName="opacity" values=".8;.4;.8;1;.8" keyTimes="0;.25;.5;.75;1" dur="{dur}s" begin="{begin:.2f}s" repeatCount="indefinite"/>'
                f'<rect x="{-w/2:.1f}" y="-12" width="{w:.1f}" height="24" rx="12" fill="{PANEL}" stroke="{col}" stroke-width="1.5"/>'
                f'<circle cx="{-w/2 + 11:.1f}" cy="0" r="3" fill="{col}"/>'
                f'<text x="5" y="4" font-size="11.5" font-weight="700" fill="{TXT}" text-anchor="middle">{label}</text></g></g>')
    o += back
    o.append(f'<circle class="breathe" cx="{cx}" cy="{cy}" r="80" fill="url(#halo)"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="34" fill="url(#core)"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="34" fill="none" stroke="#fff" stroke-opacity=".5"/>')
    o.append(f'<text x="{cx}" y="{cy+6}" font-size="18" font-weight="700" fill="#fff" text-anchor="middle">AI</text>')
    o += front
    o.append("</svg>")
    write("orbit.svg", "\n".join(o))


# ───────────────────────────── 6. now / currently ─────────────────────────────
def now():
    W, H = 900, 200
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f"""<defs><filter id="gl"><feGaussianBlur stdDeviation="2.5"/></filter>
  <linearGradient id="haze" x1="0" x2="1"><stop offset="0%" stop-color="{CY}"/><stop offset="50%" stop-color="{VI}"/><stop offset="100%" stop-color="{PK}"/></linearGradient></defs>
<style>
  text {{ {FONT} }}
  .card {{ opacity: 0; animation: rise .7s cubic-bezier(.2,.8,.2,1) forwards; }}
  @keyframes rise {{ from {{ opacity: 0; transform: translateY(16px); }} to {{ opacity: 1; transform: translateY(0); }} }}
  .steam {{ animation: steam 2.4s ease-in-out infinite; opacity: 0; }}
  @keyframes steam {{ 0% {{ opacity: 0; transform: translateY(6px); }} 40% {{ opacity: .9; }} 100% {{ opacity: 0; transform: translateY(-16px); }} }}
  .blink {{ animation: blink 1s steps(1) infinite; }} @keyframes blink {{ 50% {{ opacity: 0; }} }}
</style>"""]
    cards = [(25, CY, "building"), (315, VI, "learning"), (605, PK, "fuel")]
    for i, (x, col, title) in enumerate(cards):
        o.append(f'<g class="card" style="animation-delay:{0.2 + i*0.2:.1f}s">'
                 f'<rect x="{x}" y="15" width="270" height="170" rx="16" fill="{BG}" stroke="{BORDER}" stroke-width="1.5"/>'
                 f'<rect x="{x}" y="15" width="270" height="4" rx="2" fill="{col}"/>'
                 f'<circle cx="{x+24}" cy="46" r="5" fill="{col}"><animate attributeName="opacity" values="1;.3;1" dur="1.6s" repeatCount="indefinite"/></circle>'
                 f'<text x="{x+38}" y="51" font-size="14" font-weight="700" fill="{col}">{title}</text>')
        if title == "building":
            o.append(f'<text x="{x+24}" y="84" font-size="15" font-weight="700" fill="{TXT}">AI agents</text>'
                     f'<text x="{x+24}" y="104" font-size="12" fill="{MUTED}">&amp; research systems</text>')
            for j, (lab, pct) in enumerate([("agents", 0.78), ("evals", 0.6)]):
                by = 128 + j * 24
                o.append(f'<text x="{x+24}" y="{by+9}" font-size="11" fill="{MUTED}">{lab}</text>'
                         f'<rect x="{x+80}" y="{by}" width="160" height="10" rx="5" fill="{PANEL}"/>'
                         f'<rect x="{x+80}" y="{by}" width="0" height="10" rx="5" fill="{col}">'
                         f'<animate attributeName="width" values="0;{160*pct:.0f};{160*pct:.0f};0" keyTimes="0;.4;.9;1" dur="5s" begin="{j*0.4}s" repeatCount="indefinite"/></rect>')
        elif title == "learning":
            o.append(f'<text x="{x+24}" y="84" font-size="15" font-weight="700" fill="{TXT}">inference tricks</text>'
                     f'<text x="{x+24}" y="104" font-size="12" fill="{MUTED}">quantization · KV-cache</text>')
            # mini loss curve that draws itself
            pts = " ".join(f"{x+24 + k*7.2:.1f},{170 - 45*math.exp(-k/7) - 4*math.sin(k):.1f}" for k in range(31))
            o.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="2" stroke-linejoin="round" '
                     f'stroke-dasharray="400" stroke-dashoffset="400"><animate attributeName="stroke-dashoffset" values="400;0;0;400" keyTimes="0;.5;.9;1" dur="5s" repeatCount="indefinite"/></polyline>'
                     f'<text x="{x+246}" y="172" font-size="10" fill="{MUTED}" text-anchor="end">loss ↓</text>')
        else:
            # coffee cup
            cx0, cy0 = x + 46, 130
            o.append(f'<path d="M{cx0-20},{cy0} h40 v22 a14,14 0 0 1 -14,14 h-12 a14,14 0 0 1 -14,-14z" fill="{PANEL}" stroke="{col}" stroke-width="2"/>'
                     f'<path d="M{cx0+20},{cy0+6} a8,8 0 0 1 0,14" fill="none" stroke="{col}" stroke-width="2"/>'
                     f'<rect x="{cx0-17}" y="{cy0+3}" width="34" height="4" rx="2" fill="#92400E"/>')
            for k in range(3):
                sx = cx0 - 10 + k * 10
                o.append(f'<path class="steam" style="animation-delay:{k*0.5}s" d="M{sx},{cy0-6} q-4,-6 0,-12 q4,-6 0,-12" fill="none" stroke="{MUTED}" stroke-width="1.8" stroke-linecap="round"/>')
            o.append(f'<text x="{x+24}" y="84" font-size="15" font-weight="700" fill="{TXT}">coffee + lo-fi</text>'
                     f'<text x="{x+24}" y="104" font-size="12" fill="{MUTED}">beats to fine-tune to</text>')
            for k in range(10):
                bx = x + 100 + k * 15
                d = 0.5 + (k * 37 % 10) / 14
                o.append(f'<rect x="{bx}" y="140" width="9" height="30" rx="3" fill="url(#haze)">'
                         f'<animate attributeName="height" values="6;34;12;26;6" dur="{d:.2f}s" repeatCount="indefinite"/>'
                         f'<animate attributeName="y" values="164;136;158;144;164" dur="{d:.2f}s" repeatCount="indefinite"/></rect>')
        o.append("</g>")
    o.append("</svg>")
    write("now.svg", "\n".join(o))


# ───────────────────────────── 7. ASCII bat sign-off ─────────────────────────────
def ascii_signoff():
    lines = bat_ascii()
    W, H = 900, 380
    fs, lh = 14, 16
    cols = len(lines[0])
    tw = cols * 8.4
    x0 = (W - tw) / 2
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f"""<defs>
  <linearGradient id="g" x1="0" x2="1">
    <stop offset="0%" stop-color="{CY}"><animate attributeName="stop-color" values="{CY};{VI};{PK};{CY}" dur="6s" repeatCount="indefinite"/></stop>
    <stop offset="50%" stop-color="{VI}"><animate attributeName="stop-color" values="{VI};{PK};{CY};{VI}" dur="6s" repeatCount="indefinite"/></stop>
    <stop offset="100%" stop-color="{PK}"><animate attributeName="stop-color" values="{PK};{CY};{VI};{PK}" dur="6s" repeatCount="indefinite"/></stop>
  </linearGradient>
  <filter id="glow" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="2" fill="#fff" opacity=".03"/></pattern>
</defs>
<style>
  text {{ {FONT} }}
  .ln {{ opacity: 0; animation: in .25s ease forwards; }}
  @keyframes in {{ to {{ opacity: 1; }} }}
  .glitch {{ animation: glitch 6s infinite steps(1); }}
  @keyframes glitch {{ 0%,92%,100% {{ transform: translate(0,0); }} 93% {{ transform: translate(-4px,1px); }} 94% {{ transform: translate(4px,-1px); }} 95% {{ transform: translate(-1px,0); }} }}
  .blink {{ animation: blink 1s steps(1) infinite; }} @keyframes blink {{ 50% {{ opacity: 0; }} }}
  .tw {{ animation: tw 2.6s ease-in-out infinite; }} @keyframes tw {{ 0%,100% {{ opacity: .1; }} 50% {{ opacity: 1; }} }}
</style>
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="16" fill="{BG}" stroke="{BORDER}" stroke-width="1.5"/>"""]
    random.seed(5)
    for _ in range(40):
        o.append(f'<circle class="tw" style="animation-delay:{random.uniform(0,2.6):.1f}s" cx="{random.uniform(15,W-15):.0f}" '
                 f'cy="{random.uniform(15,260):.0f}" r="{random.choice([.8,1.1,1.5])}" fill="{random.choice(["#fff","#fff",CY,VI,PK])}"/>')
    o.append(f'<text x="24" y="34" font-size="13" fill="{MUTED}"><tspan fill="{GR}">ayush@batmandevx</tspan>:~$ cat signal.txt</text>')
    o.append('<g class="glitch" filter="url(#glow)">')
    for i, line in enumerate(lines):
        y = 62 + i * lh + fs
        o.append(f'<text class="ln" style="animation-delay:{0.4 + i*0.08:.2f}s" x="{x0:.1f}" y="{y}" font-size="{fs}" '
                 f'textLength="{tw:.1f}" lengthAdjust="spacingAndGlyphs" xml:space="preserve" fill="url(#g)">{line}</text>')
    o.append("</g>")
    msg = "thanks for scrolling. the night is young. let's build."
    ty = 62 + len(lines) * lh + 52
    mw = len(msg) * 9.0
    mx = (W - mw) / 2
    t0 = 0.4 + len(lines) * 0.08 + 0.3
    steps = len(msg)
    kt = ";".join(f"{k/steps:.3f}" for k in range(steps + 1))
    vals = ";".join(f"{k*9.0:.1f}" for k in range(steps + 1))
    o.append(f'<clipPath id="type"><rect x="{mx:.1f}" y="{ty-16}" height="22" width="0">'
             f'<animate attributeName="width" begin="{t0:.2f}s" dur="{steps*0.045:.2f}s" fill="freeze" calcMode="discrete" keyTimes="{kt}" values="{vals}"/></rect></clipPath>')
    o.append(f'<text x="{mx:.1f}" y="{ty}" font-size="15" fill="{TXT}" clip-path="url(#type)" textLength="{mw:.1f}" xml:space="preserve">{msg.replace("&","&amp;")}</text>')
    o.append(f'<rect class="blink" x="{mx+mw+4:.1f}" y="{ty-14}" width="9" height="17" fill="{VI}" opacity="0">'
             f'<set attributeName="opacity" to="1" begin="{t0 + steps*0.045:.2f}s"/></rect>')
    o.append(f'<text x="{W/2}" y="{ty+32}" font-size="12" fill="{MUTED}" text-anchor="middle">[ create with compassion ]</text>')
    o.append(f'<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="15" fill="url(#scan)"/>')
    o.append("</svg>")
    write("ascii-bat.svg", "\n".join(o))
    (Path(__file__).parent / "ascii-bat.txt").write_text("\n".join(l.rstrip() for l in lines) + "\n")


gotham()
cat_coder()
cat_divider()
pipeline()
orbit()
now()
ascii_signoff()

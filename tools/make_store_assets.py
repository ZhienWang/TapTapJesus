"""Renders the Microsoft Store tile images into build/appx/ from baby-jesus.svg.

Run from the project root:  python tools/make_store_assets.py
Needs: pip install playwright && playwright install chromium
"""
import os
from playwright.sync_api import sync_playwright

SRC = 'baby-jesus.svg'
OUT = os.path.join('build', 'appx')

# name: (width, height, viewBox crop of the 512×512 drawing, keep night-sky background)
FACE = '150 128 212 212'      # head, halo and fists
SCENE = '96 120 320 380'      # the whole baby in his manger
TILES = {
    'StoreLogo.png':         (50, 50, FACE, True),
    'Square44x44Logo.png':   (44, 44, FACE, False),
    'SmallTile.png':         (71, 71, FACE, True),
    'Square150x150Logo.png': (150, 150, FACE, True),
    'LargeTile.png':         (310, 310, SCENE, True),
    'Wide310x150Logo.png':   (310, 150, None, True),
}

svg_src = open(SRC, encoding='utf-8').read()
os.makedirs(OUT, exist_ok=True)


def page_html(w, h, crop, with_bg):
    if crop is None:
        # Wide tile: the face on the left of a sky banner.
        crop, w_svg = FACE, h
        svg = svg_src.replace('viewBox="0 0 512 512" width="512" height="512"',
                              f'viewBox="{crop}" width="{w_svg}" height="{h}"', 1)
        bg = 'radial-gradient(ellipse at 30% 45%, #3a4a8c 0%, #1c2352 55%, #0d1030 100%)'
        return (f'<body style="margin:0;width:{w}px;height:{h}px;background:{bg};display:flex;align-items:center;'
                f'justify-content:center;gap:6px;overflow:hidden"><style>#bg{{display:none}}</style>{svg}'
                f'<div style="font:800 26px Segoe UI,sans-serif;color:#fff7d1;line-height:1.05;'
                f'text-shadow:0 2px 8px rgba(255,200,80,.5)">Tap Tap<br>Baby</div></body>')
    svg = svg_src.replace('viewBox="0 0 512 512" width="512" height="512"',
                          f'viewBox="{crop}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice"', 1)
    hide = '' if with_bg else '<style>#bg,#holyGlow{display:none}</style>'
    return f'<body style="margin:0;background:transparent;overflow:hidden">{hide}{svg}</body>'


with sync_playwright() as p:
    try:
        browser = p.chromium.launch(channel='msedge')
    except Exception:
        browser = p.chromium.launch()
    for name, (w, h, crop, with_bg) in TILES.items():
        # Render at 4× and let the browser downscale for crisp small tiles.
        pg = browser.new_page(viewport={'width': w, 'height': h}, device_scale_factor=1)
        pg.set_content(page_html(w, h, crop, with_bg))
        pg.screenshot(path=os.path.join(OUT, name), omit_background=not with_bg)
        pg.close()
        print('wrote', os.path.join(OUT, name))
    browser.close()

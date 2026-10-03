"""Renders head-and-shoulders thumbnails of every avatar into assets/avatars/<id>.png
for the companion's Unlocks tab.

Run from the project root:  python tools/make_thumbnails.py
"""
import os
from playwright.sync_api import sync_playwright

AVATARS = {
    'jesus': 'baby-jesus.svg',
    'kitten': 'avatars/kitten.svg',
    'puppy': 'avatars/puppy.svg',
    'bunny': 'avatars/bunny.svg',
    'hamster': 'avatars/hamster.svg',
    'fox': 'avatars/fox.svg',
    'panda': 'avatars/panda.svg',
}
SIZE = 96
CROP = '136 124 240 240'
CROPS = {'bunny': '116 66 280 280'}  # taller, to fit the bunny's ears
OUT = os.path.join('assets', 'avatars')

os.makedirs(OUT, exist_ok=True)
with sync_playwright() as p:
    try:
        browser = p.chromium.launch(channel='msedge')
    except Exception:
        browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': SIZE, 'height': SIZE})
    for id_, src in AVATARS.items():
        svg = open(src, encoding='utf-8').read().replace(
            'viewBox="0 0 512 512" width="512" height="512"', f'viewBox="{CROPS.get(id_, CROP)}" width="{SIZE}" height="{SIZE}"', 1)
        page.set_content('<body style="margin:0;background:transparent"><style>#bg,#holyGlow,use{display:none}</style>'
                         + svg + '</body>')
        page.screenshot(path=os.path.join(OUT, id_ + '.png'), omit_background=True)
        print('wrote', os.path.join(OUT, id_ + '.png'))
    browser.close()

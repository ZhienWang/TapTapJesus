"""Generates the unlockable anime-inspired avatars in avatars/.

Each character is an original chibi design that nods to a famous anime archetype without copying it.
They all share the structure the companion expects (see baby-jesus.svg): #handL/#handR with
.pose-up/.pose-down, .mouth-closed/.mouth-open, #bg, #holyGlow, and data-* metadata on the root.

Run from the project root:  python tools/make_characters.py
"""
import math
import os

SKIN_LINE = '#e0a284'
STYLE = '''  <style>
    .pose-down, .mouth-open { display: none; }
    .tap-left  #handL .pose-up, .tap-right #handR .pose-up { display: none; }
    .tap-left  #handL .pose-down, .tap-right #handR .pose-down { display: inline; }
    .tap-left .mouth-closed, .tap-right .mouth-closed { display: none; }
    .tap-left .mouth-open, .tap-right .mouth-open { display: inline; }
    .chroma #bg, .chroma #holyGlow { display: none; }
  </style>'''

SHIRT = 'M146,372 C146,326 186,308 226,306 L286,306 C326,308 366,326 366,372Z'
BOARD = 'M104,364 L408,364 L400,440 L112,440Z'
LEGS = [(140, 432, 112, 492), (160, 432, 188, 492), (372, 432, 400, 492), (352, 432, 324, 492)]


# ---------- shared parts ----------

def grad(id_, stops, vertical=True, radial=False):
    tag = 'radialGradient' if radial else 'linearGradient'
    attrs = ' cx="50%" cy="50%" r="50%"' if radial else (' x1="0" y1="0" x2="0" y2="1"' if vertical else ' x1="0" y1="0" x2="1" y2="0"')
    s = ''.join(f'<stop offset="{o}" stop-color="{c}"' + (f' stop-opacity="{a}"' if a is not None else '') + '/>'
                for o, c, a in stops)
    return f'<{tag} id="{id_}"{attrs}>{s}</{tag}>'


def defs(c, extra=''):
    return f'''  <defs>
    <radialGradient id="sky" cx="50%" cy="40%" r="75%"><stop offset="0%" stop-color="{c['sky'][0]}"/><stop offset="60%" stop-color="{c['sky'][1]}"/><stop offset="100%" stop-color="{c['sky'][2]}"/></radialGradient>
    {grad('glow', [('0%', c['glow'][0], 0.85), ('45%', c['glow'][1], 0.4), ('100%', c['glow'][1], 0)], radial=True)}
    <radialGradient id="skin" cx="45%" cy="40%" r="65%"><stop offset="0%" stop-color="#fff3e8"/><stop offset="75%" stop-color="#ffe2cf"/><stop offset="100%" stop-color="#f7cbb2"/></radialGradient>
    {grad('iris', [('0%', c['iris'][0], None), ('55%', c['iris'][1], None), ('100%', c['iris'][2], None)])}
    {grad('hair', [('0%', c['hair'][0], None), ('100%', c['hair'][1], None)])}
    <filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="4"/></filter>
    <g id="sparkle"><path d="M0,-12 C1.5,-3 3,-1.5 12,0 C3,1.5 1.5,3 0,12 C-1.5,3 -3,1.5 -12,0 C-3,-1.5 -1.5,-3 0,-12Z" fill="{c['sparkle']}"/></g>
    {extra}
  </defs>'''


def ears():
    return '''  <circle cx="177" cy="262" r="13" fill="#ffd9c0"/><circle cx="335" cy="262" r="13" fill="#ffd9c0"/>
  <circle cx="179" cy="263" r="6" fill="#f5bfa2"/><circle cx="333" cy="263" r="6" fill="#f5bfa2"/>'''


def face(lash='#2a1a14', brows=None):
    eyes = ''
    for cx, flip in ((222, 1), (290, -1)):
        hl = cx - 7
        lx0, lx1 = (201, 243) if flip == 1 else (269, 311)
        corner = (f'M{lx0 + 1},260 L{lx0 - 9},253 M{lx0 + 4},255 L{lx0 - 4},247' if flip == 1
                  else f'M{lx1 - 1},260 L{lx1 + 9},253 M{lx1 - 4},255 L{lx1 + 4},247')
        eyes += f'''
  <g>
    <ellipse cx="{cx}" cy="266" rx="17" ry="22" fill="#ffffff"/>
    <ellipse cx="{cx}" cy="268" rx="14.5" ry="20" fill="url(#iris)"/>
    <ellipse cx="{cx}" cy="269" rx="6.5" ry="9" fill="#120a08" opacity="0.85"/>
    <circle cx="{hl}" cy="258" r="6.5" fill="#ffffff"/>
    <circle cx="{cx + 6}" cy="277" r="2.8" fill="#ffffff"/>
    <path d="M{lx0},{260 if flip == 1 else 258} Q{(lx0 + lx1) // 2},232 {lx1},{258 if flip == 1 else 260}" fill="none" stroke="{lash}" stroke-width="5.5" stroke-linecap="round"/>
    <path d="{corner}" stroke="{lash}" stroke-width="3.5" stroke-linecap="round"/>
  </g>'''
    brow = ''
    if brows:
        brow = f'''
  <path d="M206,234 L234,240" stroke="{brows}" stroke-width="5" stroke-linecap="round"/>
  <path d="M306,234 L278,240" stroke="{brows}" stroke-width="5" stroke-linecap="round"/>'''
    return f'''  <ellipse cx="204" cy="292" rx="16" ry="9" fill="#ff8fa8" opacity="0.5" filter="url(#soft)"/>
  <ellipse cx="308" cy="292" rx="16" ry="9" fill="#ff8fa8" opacity="0.5" filter="url(#soft)"/>{eyes}{brow}
  <ellipse cx="256" cy="290" rx="2" ry="1.5" fill="#f0a88c"/>
  <g class="mouth-closed"><path d="M246,302 Q256,314 266,302 Q256,306 246,302Z" fill="#d95c78"/></g>
  <g class="mouth-open"><ellipse cx="256" cy="306" rx="8.5" ry="9.5" fill="#b8405e"/><ellipse cx="256" cy="311" rx="5.5" ry="3.5" fill="#ff8fa8"/></g>'''


def arm(sleeve, line, fold, cuff, cuff_line, imp_out, imp_in):
    impact = ('<line x1="146" y1="353" x2="155" y2="361"/><line x1="160" y1="340" x2="164" y2="351"/>'
              '<line x1="138" y1="372" x2="150" y2="372"/>')
    return f'''
    <g class="pose-up">
      <ellipse cx="190" cy="331" rx="31" ry="21" transform="rotate(40 190 331)" fill="{sleeve}" stroke="{line}" stroke-width="2.5"/>
      <path d="M197,322 Q190,331 196,342" fill="none" stroke="{fold}" stroke-width="2" stroke-linecap="round" opacity="0.8"/>
      <ellipse cx="169" cy="313" rx="8" ry="16" transform="rotate(40 169 313)" fill="{cuff}" stroke="{cuff_line}" stroke-width="2.5"/>
      <circle cx="158" cy="300" r="17" fill="url(#skin)" stroke="{SKIN_LINE}" stroke-width="2"/>
      <ellipse cx="170" cy="293" rx="6" ry="7.5" transform="rotate(-20 170 293)" fill="#ffe3cf" stroke="{SKIN_LINE}" stroke-width="2"/>
      <path d="M147,293 Q150,289 154,292 M154,292 Q157,288 161,291" fill="none" stroke="{SKIN_LINE}" stroke-width="1.8" stroke-linecap="round"/>
      <ellipse cx="153" cy="306" rx="5" ry="3" fill="#ff9fb2" opacity="0.45"/>
      <circle cx="152" cy="295" r="2.2" fill="#ffffff" opacity="0.8"/>
    </g>
    <g class="pose-down">
      <ellipse cx="196" cy="352" rx="27" ry="21" transform="rotate(-42 196 352)" fill="{sleeve}" stroke="{line}" stroke-width="2.5"/>
      <path d="M205,345 Q197,350 197,360" fill="none" stroke="{fold}" stroke-width="2" stroke-linecap="round" opacity="0.8"/>
      <ellipse cx="183" cy="365" rx="16" ry="7" transform="rotate(-10 183 365)" fill="{cuff}" stroke="{cuff_line}" stroke-width="2.5"/>
      <ellipse cx="179" cy="375" rx="20" ry="13" fill="url(#skin)" stroke="{SKIN_LINE}" stroke-width="2"/>
      <path d="M166,371 Q169,367 173,370 M173,370 Q176,366 180,369 M180,369 Q183,365 187,368" fill="none" stroke="{SKIN_LINE}" stroke-width="1.8" stroke-linecap="round"/>
      <ellipse cx="172" cy="379" rx="5" ry="2.5" fill="#ff9fb2" opacity="0.45"/>
      <g stroke="{imp_out}" stroke-width="6.5" stroke-linecap="round">{impact}</g>
      <g stroke="{imp_in}" stroke-width="3.5" stroke-linecap="round">{impact}</g>
    </g>
'''


def hands(*args):
    a = arm(*args)
    return ('  <g id="handL">' + a + '  </g>\n'
            '  <g id="handR">\n    <g transform="translate(512 0) scale(-1 1)">' + a + '    </g>\n  </g>\n')


def legs(color, width=12):
    lines = ''.join(f'<line x1="{a}" y1="{b}" x2="{c}" y2="{d}"/>' for a, b, c, d in LEGS)
    return f'  <g stroke="{color}" stroke-width="{width}" stroke-linecap="round">{lines}</g>'


def crown(spikes, r_out, r_in, cy=236, start=205, end=-25, wobble=()):
    """Spiky hair crown: alternating spike tips (r_out) and valleys (r_in) over the top of the head."""
    pts = []
    total = start - end
    step = total / (spikes * 2)
    for i in range(spikes * 2 + 1):
        a = math.radians(start - i * step)
        r = r_out + (wobble[i // 2 % len(wobble)] if wobble else 0) if i % 2 else (82 if i in (0, spikes * 2) else r_in)
        pts.append((256 + r * math.cos(a), cy - r * math.sin(a)))
    return pts


def poly(pts):
    return 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts)


def doc(c, layers):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512"
     data-name="{c['name']}" data-crop="96 120 320 380"
     data-counter-x="256" data-counter-y="{c.get('counter_y', 420)}" data-counter-fill="{c['counter'][0]}" data-counter-stroke="{c['counter'][1]}">
  <!-- {c['note']} -->
{STYLE}
{defs(c, c.get('defs', ''))}
  <g id="bg">
    <rect id="sky-rect" width="512" height="512" fill="url(#sky)"/>
{c.get('bg', '')}
  </g>
  <circle id="holyGlow" cx="256" cy="250" r="165" fill="url(#glow)"/>
{layers}
  <use href="#sparkle" transform="translate(122 150) scale(0.9)"/>
  <use href="#sparkle" transform="translate(390 230) scale(0.7)"/>
  <use href="#sparkle" transform="translate(372 146) scale(0.5)" opacity="0.8"/>
</svg>
'''


def stars(color, pts):
    return '\n'.join(f'    <circle cx="{x}" cy="{y}" r="{r}" fill="{color}" opacity="0.7"/>' for x, y, r in pts)


STAR_PTS = [(60, 70, 1.6), (120, 40, 1.2), (40, 180, 1.4), (470, 200, 1.5), (455, 40, 1.2), (330, 50, 1.3), (90, 290, 1.3), (430, 300, 1.1)]


# ---------- characters ----------

def ninja():
    c = dict(
        id='ninja', name='Ninja Kid', note='Original chibi homage to a spiky-haired orange ninja.',
        sky=('#ff9a5a', '#c2410c', '#431407'), glow=('#fff1c2', '#ff8a1f'), iris=('#0b3a7a', '#1f6fd1', '#8ec5ff'),
        hair=('#ffe066', '#f4b400'), sparkle='#fff1c2', counter=('#fff3d6', '#5a2d0c'),
        defs=grad('jacket', [('0%', '#ff9a3c', None), ('100%', '#e8700a', None)]) + grad('counterWood', [('0%', '#d9a066', None), ('100%', '#a8692f', None)]),
        bg=stars('#fff1c2', STAR_PTS),
    )
    hair_top = crown(11, 102, 84, wobble=(0, 6, -4, 8, 2, 10, 2, 8, -4, 6, 0))
    bangs = [(330, 270), (322, 236), (312, 214), (300, 240), (288, 210), (272, 238), (256, 212), (240, 238),
             (224, 210), (212, 240), (200, 214), (190, 236), (182, 270)]
    layers = f'''  <path d="{SHIRT}" fill="url(#jacket)" stroke="#b85c00" stroke-width="2"/>
  <path d="M146,372 C146,326 186,308 226,306 L234,306 C204,316 182,332 176,372Z" fill="#1d1d24"/>
  <path d="M366,372 C366,326 326,308 286,306 L278,306 C308,316 330,332 336,372Z" fill="#1d1d24"/>
{ears()}
  <circle cx="256" cy="250" r="80" fill="url(#skin)"/>
{face(lash='#2a1a14')}
  <rect x="190" y="286" width="20" height="9" rx="3" transform="rotate(-18 200 290)" fill="#ffe2bf" stroke="#d9a77a" stroke-width="1.5"/>
  <circle cx="197" cy="291" r="1" fill="#d9a77a"/><circle cx="203" cy="289" r="1" fill="#d9a77a"/>
  <path d="{poly(hair_top + bangs)}Z" fill="url(#hair)" stroke="#c98a00" stroke-width="2.5" stroke-linejoin="round"/>
  <path d="M214,178 C232,168 252,165 272,168" fill="none" stroke="#fff6c2" stroke-width="4" stroke-linecap="round" opacity="0.9"/>
  <path d="M180,220 Q256,190 332,220 L330,204 Q256,174 182,204Z" fill="#1f3a68" stroke="#0f1f3a" stroke-width="2"/>
  <rect x="224" y="186" width="64" height="22" rx="4" fill="#d5dbe1" stroke="#6b7785" stroke-width="2"/>
  <path d="M256,191 a6,6 0 1,1 -6,6 a3.5,3.5 0 1,1 3.5,-3.5" fill="none" stroke="#55606e" stroke-width="2" stroke-linecap="round"/>
  <path d="M224,320 Q256,342 288,320 L294,334 Q256,358 218,334Z" fill="url(#jacket)" stroke="#b85c00" stroke-width="2"/>
  <line x1="256" y1="342" x2="256" y2="372" stroke="#f5f5f5" stroke-width="3"/>
  <rect x="252" y="344" width="8" height="12" rx="2" fill="#f5f5f5" stroke="#9aa1ab" stroke-width="1"/>
{legs('#5a3414')}
  <rect x="100" y="352" width="312" height="14" rx="3" fill="#8b4513" stroke="#4a2408" stroke-width="2"/>
  <path d="{BOARD}" fill="url(#counterWood)" stroke="#6b3f17" stroke-width="3" stroke-linejoin="round"/>
  <rect x="112" y="374" width="288" height="9" fill="#d62828"/>
  <path d="M150,400 Q180,396 210,401 M290,425 Q320,421 350,426" fill="none" stroke="#f0c48e" stroke-width="1.5" opacity="0.7"/>
  <path d="M222,334 Q224,360 256,360 Q288,360 290,334Z" fill="#e63946" stroke="#8d1b22" stroke-width="2"/>
  <path d="M232,346 Q256,352 280,346" fill="none" stroke="#ffffff" stroke-width="2" opacity="0.8"/>
  <ellipse cx="256" cy="334" rx="34" ry="7" fill="#f6d7a7" stroke="#8d1b22" stroke-width="2"/>
  <circle cx="246" cy="333" r="4" fill="#fff" stroke="#f4a3a8" stroke-width="2"/>
  <line x1="272" y1="332" x2="300" y2="310" stroke="#c98b4b" stroke-width="3" stroke-linecap="round"/>
  <line x1="278" y1="333" x2="306" y2="314" stroke="#c98b4b" stroke-width="3" stroke-linecap="round"/>
{hands('url(#jacket)', '#b85c00', '#ffb066', '#1d1d24', '#000000', '#5a2a00', '#ffe066')}'''
    return c, layers


def pirate():
    c = dict(
        id='pirate', name='Straw Hat Captain', note='Original chibi homage to a rubbery straw-hat pirate captain.',
        sky=('#6ec6ff', '#1e6fb8', '#0b2a4f'), glow=('#fffbe0', '#ffd166'), iris=('#1a1210', '#4a2e22', '#a07050'),
        hair=('#2a2a33', '#121218'), sparkle='#fffbe0', counter=('#ffe08a', '#3a2208'),
        defs=(grad('straw', [('0%', '#f6d985', None), ('100%', '#d9ab45', None)])
              + grad('vest', [('0%', '#e63946', None), ('100%', '#b51d2a', None)])
              + grad('chest', [('0%', '#9c6233', None), ('100%', '#6a3e1c', None)])),
        bg='''    <path d="M0,420 Q64,400 128,420 T256,420 T384,420 T512,420 L512,512 L0,512Z" fill="#0e4c86" opacity="0.6"/>
    <path d="M0,450 Q64,430 128,450 T256,450 T384,450 T512,450 L512,512 L0,512Z" fill="#0a3866" opacity="0.7"/>
    <circle cx="420" cy="90" r="34" fill="#fff4c2" opacity="0.8"/>''',
    )
    back = [(176, 262), (170, 228), (186, 200), (326, 200), (342, 228), (336, 262)]
    bangs = [(336, 262), (330, 236), (318, 224), (310, 244), (298, 222), (284, 240), (270, 220), (256, 238), (242, 220),
             (228, 242), (214, 222), (202, 244), (194, 224), (182, 236), (176, 262)]
    layers = f'''  <path d="{SHIRT}" fill="url(#skin)" stroke="{SKIN_LINE}" stroke-width="2"/>
  <path d="M146,372 C146,326 186,308 226,306 L238,306 L228,372Z" fill="url(#vest)" stroke="#8d1b22" stroke-width="2"/>
  <path d="M366,372 C366,326 326,308 286,306 L274,306 L284,372Z" fill="url(#vest)" stroke="#8d1b22" stroke-width="2"/>
  <circle cx="232" cy="330" r="3" fill="#ffd166" stroke="#a37a1c"/><circle cx="231" cy="350" r="3" fill="#ffd166" stroke="#a37a1c"/>
{ears()}
  <circle cx="256" cy="250" r="80" fill="url(#skin)"/>
{face(lash='#1a1210')}
  <path d="M298,276 L304,276 M301,273 L301,279" stroke="#c97b63" stroke-width="2" stroke-linecap="round" opacity="0.9"/>
  <path d="{poly(back + bangs)}Z" fill="url(#hair)" stroke="#000000" stroke-width="2" stroke-linejoin="round"/>
  <ellipse cx="256" cy="192" rx="118" ry="26" fill="url(#straw)" stroke="#a87b22" stroke-width="2.5"/>
  <path d="M150,196 Q256,224 362,196" fill="none" stroke="#c99a3a" stroke-width="2" opacity="0.8"/>
  <path d="M196,192 C196,138 316,138 316,192Z" fill="url(#straw)" stroke="#a87b22" stroke-width="2.5"/>
  <path d="M197,180 C222,170 290,170 315,180 L316,192 C290,183 222,183 196,192Z" fill="#d62828" stroke="#8d1b22" stroke-width="1.5"/>
  <path d="M214,160 Q256,150 298,160" fill="none" stroke="#fff1b8" stroke-width="3" stroke-linecap="round" opacity="0.8"/>
  <rect x="124" y="476" width="22" height="16" rx="3" fill="#4a2c12"/><rect x="366" y="476" width="22" height="16" rx="3" fill="#4a2c12"/>
  <path d="M104,364 L408,364 L404,480 L108,480Z" fill="url(#chest)" stroke="#3b220d" stroke-width="3" stroke-linejoin="round"/>
  <rect x="98" y="350" width="316" height="16" rx="4" fill="#e9b949" stroke="#8c6512" stroke-width="2"/>
  <rect x="146" y="366" width="16" height="114" fill="#e9b949" stroke="#8c6512" stroke-width="2"/>
  <rect x="350" y="366" width="16" height="114" fill="#e9b949" stroke="#8c6512" stroke-width="2"/>
  <line x1="106" y1="446" x2="406" y2="446" stroke="#3b220d" stroke-width="2" opacity="0.6"/>
  <rect x="242" y="364" width="28" height="22" rx="4" fill="#e9b949" stroke="#8c6512" stroke-width="2"/>
  <circle cx="256" cy="372" r="3" fill="#3b220d"/><path d="M256,374 L256,381" stroke="#3b220d" stroke-width="2.5"/>
  <circle cx="226" cy="348" r="6" fill="#ffd166" stroke="#a37a1c" stroke-width="1.5"/><circle cx="290" cy="347" r="6" fill="#ffd166" stroke="#a37a1c" stroke-width="1.5"/>
{hands('url(#skin)', SKIN_LINE, '#f0b896', '#d62828', '#8d1b22', '#3a2208', '#ffe08a')}'''
    c['counter_y'] = 425
    return c, layers


def fighter():
    c = dict(
        id='fighter', name='Power Fighter', note='Original chibi homage to a spiky-haired martial-arts hero.',
        sky=('#8fd3ff', '#3b82c4', '#13355e'), glow=('#fffbd1', '#ffe45c'), iris=('#0d0d12', '#2b2b38', '#6a6a80'),
        hair=('#2a2b36', '#0e0f15'), sparkle='#fffbd1', counter=('#ffffff', '#2b2f33'),
        defs=(grad('gi', [('0%', '#ff9a2e', None), ('100%', '#e06c00', None)])
              + grad('stone', [('0%', '#b4b9bf', None), ('100%', '#7d838a', None)])),
        bg='''    <ellipse cx="110" cy="120" rx="60" ry="18" fill="#ffffff" opacity="0.5"/>
    <ellipse cx="400" cy="80" rx="70" ry="20" fill="#ffffff" opacity="0.45"/>''',
    )
    top = crown(7, 100, 78, cy=236, start=208, end=-28, wobble=(2, 8, 4, 10, 4, 8, 2))
    bangs = [(328, 270), (320, 238), (306, 206), (298, 248), (282, 204), (266, 244), (254, 206), (238, 248), (222, 206),
             (208, 246), (196, 214), (186, 240), (184, 270)]
    layers = f'''  <path d="{SHIRT}" fill="url(#gi)" stroke="#a34f00" stroke-width="2"/>
  <circle cx="306" cy="342" r="10" fill="#ffffff" stroke="#a34f00" stroke-width="1.5"/>
  <path d="M306,335 L308,340 L313,340 L309,343 L311,348 L306,345 L301,348 L303,343 L299,340 L304,340Z" fill="#1d4e89"/>
{ears()}
  <circle cx="256" cy="250" r="80" fill="url(#skin)"/>
{face(lash='#14141c', brows='#14141c')}
  <path d="{poly(top + bangs)}Z" fill="url(#hair)" stroke="#000000" stroke-width="2.5" stroke-linejoin="round"/>
  <path d="M220,170 L236,150 M276,152 L290,170" stroke="#4a4e66" stroke-width="3.5" stroke-linecap="round" opacity="0.9"/>
  <path d="M224,318 L256,352 L288,318 L296,330 L256,364 L216,330Z" fill="#1d4e89" stroke="#0d2747" stroke-width="2" stroke-linejoin="round"/>
  <path d="M216,330 L256,364 L240,372 L206,340Z" fill="url(#gi)" stroke="#a34f00" stroke-width="2"/>
  <path d="M296,330 L256,364 L272,372 L306,340Z" fill="url(#gi)" stroke="#a34f00" stroke-width="2"/>
  <path d="M104,364 L408,364 L404,486 L108,486Z" fill="url(#stone)" stroke="#4b5057" stroke-width="3" stroke-linejoin="round"/>
  <rect x="98" y="352" width="316" height="14" rx="3" fill="#c9ced3" stroke="#4b5057" stroke-width="2"/>
  <g stroke="#5d636a" stroke-width="2" opacity="0.7">
    <line x1="182" y1="366" x2="182" y2="400"/><line x1="330" y1="366" x2="330" y2="400"/>
    <line x1="106" y1="400" x2="406" y2="400"/><line x1="140" y1="400" x2="140" y2="444"/><line x1="372" y1="400" x2="372" y2="444"/>
    <line x1="107" y1="444" x2="405" y2="444"/><line x1="200" y1="444" x2="200" y2="486"/><line x1="312" y1="444" x2="312" y2="486"/>
  </g>
  <path d="M150,366 L160,380 L152,392 L164,404 M362,366 L352,380 L360,392 L348,404" fill="none" stroke="#3a3f45" stroke-width="2.5" stroke-linejoin="round"/>
{hands('url(#gi)', '#a34f00', '#ffb366', '#1d4e89', '#0d2747', '#5a3a00', '#fff3a0')}'''
    c['counter_y'] = 432
    return c, layers


def swordsman():
    c = dict(
        id='swordsman', name='Sun Swordsman', note='Original chibi homage to a kind demon-hunting swordsman.',
        sky=('#4a1c2e', '#24101d', '#0d070c'), glow=('#ffe0c2', '#ff7b54'), iris=('#4a0d0d', '#b0302a', '#ff9a76'),
        hair=('#7a2a24', '#3d0f0f'), sparkle='#ffe0c2', counter=('#ffd166', '#2b0808'),
        defs=('<pattern id="haori" width="18" height="18" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
              '<rect width="18" height="18" fill="#11151c"/><rect width="9" height="9" fill="#1f9a7a"/><rect x="9" y="9" width="9" height="9" fill="#1f9a7a"/></pattern>'
              + grad('drum', [('0%', '#93282a', None), ('100%', '#561313', None)])),
        bg=stars('#ffe0c2', STAR_PTS) + '\n    <circle cx="410" cy="92" r="30" fill="#ff9a76" opacity="0.6"/>',
    )
    top = crown(9, 104, 84, wobble=(0, 4, -2, 6, 2, 6, -2, 4, 0))
    bangs = [(332, 270), (326, 236), (316, 218), (304, 240), (292, 214), (278, 236), (266, 212), (254, 232), (240, 212),
             (228, 238), (214, 216), (202, 240), (192, 222), (184, 244), (180, 270)]
    sun = lambda x, y: (f'<line x1="{x}" y1="{y - 18}" x2="{x}" y2="{y - 9}" stroke="#c9a227" stroke-width="2"/>'
                        f'<circle cx="{x}" cy="{y}" r="8" fill="#ffd166" stroke="#a6761d" stroke-width="2"/>'
                        f'<circle cx="{x}" cy="{y}" r="3.5" fill="#e85d04"/>')
    layers = f'''  <path d="{SHIRT}" fill="url(#haori)" stroke="#0b0f14" stroke-width="2"/>
{ears()}
  {sun(177, 292)}{sun(335, 292)}
  <circle cx="256" cy="250" r="80" fill="url(#skin)"/>
{face(lash='#2b0d0b')}
  <path d="{poly(top + bangs)}Z" fill="url(#hair)" stroke="#2b0808" stroke-width="2.5" stroke-linejoin="round"/>
  <path d="M220,168 C236,160 254,158 272,160" fill="none" stroke="#c9534a" stroke-width="4" stroke-linecap="round" opacity="0.8"/>
  <path d="M224,318 L256,346 L288,318 L296,330 L256,358 L216,330Z" fill="#1b1f2a" stroke="#e9ecef" stroke-width="2" stroke-linejoin="round"/>
{legs('#3b2412')}
  <path d="{BOARD}" fill="url(#drum)" stroke="#2b0808" stroke-width="3" stroke-linejoin="round"/>
  <ellipse cx="256" cy="360" rx="152" ry="10" fill="#efe0c4" stroke="#7a5a3a" stroke-width="2"/>
  <g fill="#e9b949" stroke="#8c6512" stroke-width="1">{''.join(f'<circle cx="{x}" cy="374" r="3.2"/>' for x in range(118, 400, 14))}{''.join(f'<circle cx="{x}" cy="430" r="3.2"/>' for x in range(124, 392, 14))}</g>
  <path d="M130,388 L382,388" stroke="#2b0808" stroke-width="2" opacity="0.5"/>
{hands('url(#haori)', '#0b0f14', '#2fb592', '#1b1f2a', '#e9ecef', '#2b0808', '#ffd166')}'''
    return c, layers


def guardian():
    c = dict(
        id='guardian', name='Moon Guardian', note='Original chibi homage to a twin-bun sailor-uniform magical guardian.',
        sky=('#c77dff', '#5a189a', '#240046'), glow=('#fff0fa', '#ff8fd1'), iris=('#1e1a6b', '#4f6ff0', '#c4d0ff'),
        hair=('#ffe8a3', '#f2b134'), sparkle='#fff0fa', counter=('#ffffff', '#c9184a'),
        defs=(grad('vanity', [('0%', '#ffc2d4', None), ('100%', '#ff8fab', None)])
              + grad('blonde', [('0%', '#ffe08a', None), ('100%', '#e9a51e', None)])),
        bg=stars('#fff0fa', STAR_PTS) + '\n    <path d="M420,60 a34,34 0 1,0 30,52 a26,26 0 1,1 -30,-52Z" fill="#fff3c4" opacity="0.85"/>',
    )
    layers = f'''  <path d="M190,182 C140,190 108,262 110,342 C111,400 120,440 134,474 C150,432 160,384 164,334 C168,276 178,222 198,198Z" fill="url(#blonde)" stroke="#c98a1a" stroke-width="2"/>
  <path d="M322,182 C372,190 404,262 402,342 C401,400 392,440 378,474 C362,432 352,384 348,334 C344,276 334,222 314,198Z" fill="url(#blonde)" stroke="#c98a1a" stroke-width="2"/>
  <path d="M152,226 C132,290 132,380 140,440 M360,226 C380,290 380,380 372,440" fill="none" stroke="#d99a2b" stroke-width="2.5" opacity="0.7"/>
  <path d="M166,252 C160,176 206,146 256,146 C306,146 352,176 346,252 L340,316 L172,316Z" fill="#f0b23a"/>
  <circle cx="184" cy="170" r="27" fill="url(#hair)" stroke="#c98a1a" stroke-width="2.5"/>
  <circle cx="328" cy="170" r="27" fill="url(#hair)" stroke="#c98a1a" stroke-width="2.5"/>
  <path d="M172,160 Q184,150 196,158 M316,158 Q328,150 340,160" fill="none" stroke="#fff6d5" stroke-width="3" stroke-linecap="round"/>
  <path d="{SHIRT}" fill="#f8f9fa" stroke="#b8c0cc" stroke-width="2"/>
  <circle cx="256" cy="250" r="80" fill="url(#skin)"/>
{face(lash='#2d2240')}
  <path d="M170,252 C162,180 204,152 256,152 C308,152 350,180 342,252
           C334,236 326,226 314,222 C310,238 296,244 286,236 C280,224 268,218 256,224
           C244,218 232,224 226,236 C216,244 202,238 198,222 C186,226 178,236 170,252Z"
        fill="url(#hair)" stroke="#c98a1a" stroke-width="2" stroke-linejoin="round"/>
  <path d="M178,212 C168,258 174,302 192,338 C194,302 196,262 202,226Z" fill="url(#hair)" stroke="#c98a1a" stroke-width="2"/>
  <path d="M334,212 C344,258 338,302 320,338 C318,302 316,262 310,226Z" fill="url(#hair)" stroke="#c98a1a" stroke-width="2"/>
  <path d="M190,214 Q256,192 322,214" fill="none" stroke="#f7c948" stroke-width="4" stroke-linecap="round"/>
  <path d="M256,196 L259,204 L267,204 L261,209 L263,217 L256,212 L249,217 L251,209 L245,204 L253,204Z" fill="#ff4d6d" stroke="#a4133c" stroke-width="1.5"/>
  <path d="M204,312 L256,356 L308,312 L334,326 C320,342 290,362 256,374 C222,362 192,342 178,326Z" fill="#2a5bd7" stroke="#173a8a" stroke-width="2" stroke-linejoin="round"/>
  <path d="M190,326 C210,342 234,356 256,364 C278,356 302,342 322,326" fill="none" stroke="#ffffff" stroke-width="2.5"/>
  <path d="M256,352 L226,336 L230,368Z M256,352 L286,336 L282,368Z" fill="#e63946" stroke="#9d1d28" stroke-width="2" stroke-linejoin="round"/>
  <path d="M256,358 C250,352 248,346 253,345 C255,345 256,347 256,348 C256,347 257,345 259,345 C264,346 262,352 256,358Z" fill="#ffd166" stroke="#c98a1a" stroke-width="1.2"/>
{legs('#ffffff', 10)}
{legs('#e0a8bd', 4)}
  <path d="{BOARD}" fill="url(#vanity)" stroke="#c9184a" stroke-width="3" stroke-linejoin="round"/>
  <rect x="100" y="352" width="312" height="14" rx="7" fill="#ffffff" stroke="#c9184a" stroke-width="2"/>
  <g fill="#ffffff" stroke="#e58fae" stroke-width="1">{''.join(f'<circle cx="{x}" cy="370" r="5"/>' for x in range(116, 400, 12))}</g>
  <path d="M146,410 C140,402 136,396 142,394 C145,393 147,396 147,398 C147,396 149,393 152,394 C158,396 154,402 146,410Z" fill="#ffffff" opacity="0.85"/>
  <path d="M366,410 C360,402 356,396 362,394 C365,393 367,396 367,398 C367,396 369,393 372,394 C378,396 374,402 366,410Z" fill="#ffffff" opacity="0.85"/>
{hands('#f8f9fa', '#b8c0cc', '#dfe4ea', '#2a5bd7', '#173a8a', '#a4133c', '#ffd1e0')}'''
    return c, layers


CHARACTERS = [ninja, pirate, fighter, swordsman, guardian]

if __name__ == '__main__':
    os.makedirs('avatars', exist_ok=True)
    for make in CHARACTERS:
        c, layers = make()
        path = os.path.join('avatars', c['id'] + '.svg')
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(doc(c, layers))
        print('wrote', path)

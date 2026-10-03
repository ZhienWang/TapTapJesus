"""Generates the unlockable cute-animal avatars in avatars/.

Each character is an original chibi pet. They all share the structure the companion expects
(see baby-jesus.svg): #handL/#handR with .pose-up/.pose-down, .mouth-closed/.mouth-open, #bg,
#holyGlow, and data-* metadata on the root.

Run from the project root:  python tools/make_characters.py
"""
import os

STYLE = '''  <style>
    .pose-down, .mouth-open { display: none; }
    .tap-left  #handL .pose-up, .tap-right #handR .pose-up { display: none; }
    .tap-left  #handL .pose-down, .tap-right #handR .pose-down { display: inline; }
    .tap-left .mouth-closed, .tap-right .mouth-closed { display: none; }
    .tap-left .mouth-open, .tap-right .mouth-open { display: inline; }
    .chroma #bg, .chroma #holyGlow { display: none; }
  </style>'''

BODY = 'M146,372 C146,326 186,308 226,306 L286,306 C326,308 366,326 366,372Z'
BOARD = 'M104,364 L408,364 L404,486 L108,486Z'
PAW_PINK = '#ff9fb6'


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
    <radialGradient id="fur" cx="45%" cy="38%" r="70%"><stop offset="0%" stop-color="{c['fur'][0]}"/><stop offset="100%" stop-color="{c['fur'][1]}"/></radialGradient>
    {grad('iris', [('0%', c['iris'][0], None), ('55%', c['iris'][1], None), ('100%', c['iris'][2], None)])}
    {grad('desk', [('0%', c['desk'][0], None), ('100%', c['desk'][1], None)])}
    <filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="4"/></filter>
    <g id="sparkle"><path d="M0,-12 C1.5,-3 3,-1.5 12,0 C3,1.5 1.5,3 0,12 C-1.5,3 -3,1.5 -12,0 C-3,-1.5 -1.5,-3 0,-12Z" fill="{c['sparkle']}"/></g>
    {extra}
  </defs>'''


def head(c):
    return f'  <circle cx="256" cy="250" r="80" fill="url(#fur)" stroke="{c["line"]}" stroke-width="2.5"/>'


def eyes(lash='#2a1a14'):
    out = ''
    for cx in (222, 290):
        out += f'''
  <ellipse cx="{cx}" cy="266" rx="15" ry="18" fill="#140c0a"/>
  <ellipse cx="{cx}" cy="270" rx="11" ry="12" fill="url(#iris)" opacity="0.9"/>
  <circle cx="{cx - 5}" cy="259" r="6" fill="#ffffff"/>
  <circle cx="{cx + 6}" cy="275" r="2.6" fill="#ffffff"/>'''
    return out


def snout(c, muzzle=None, whiskers=True, nose='#ff7d9c'):
    """Blush, optional muzzle patch, nose, whiskers and the two mouth states."""
    line = c['line']
    m = (f'\n  <ellipse cx="256" cy="300" rx="30" ry="20" fill="{muzzle}" stroke="{line}" stroke-width="1.5" opacity="0.95"/>'
         if muzzle else '')
    w = ''
    if whiskers:
        w = f'''
  <g stroke="{line}" stroke-width="2" stroke-linecap="round" opacity="0.7">
    <line x1="196" y1="292" x2="168" y2="286"/><line x1="196" y1="300" x2="166" y2="302"/>
    <line x1="316" y1="292" x2="344" y2="286"/><line x1="316" y1="300" x2="346" y2="302"/>
  </g>'''
    return f'''  <ellipse cx="200" cy="294" rx="15" ry="9" fill="#ff8fa8" opacity="0.55" filter="url(#soft)"/>
  <ellipse cx="312" cy="294" rx="15" ry="9" fill="#ff8fa8" opacity="0.55" filter="url(#soft)"/>{m}{w}
  <path d="M249,288 Q256,284 263,288 Q260,295 256,296 Q252,295 249,288Z" fill="{nose}" stroke="{line}" stroke-width="1.2"/>
  <g class="mouth-closed"><path d="M256,296 L256,301 M244,300 Q250,308 256,301 Q262,308 268,300" fill="none" stroke="{line}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></g>
  <g class="mouth-open"><path d="M256,296 L256,300" stroke="{line}" stroke-width="2.4" stroke-linecap="round"/><ellipse cx="256" cy="309" rx="9" ry="9.5" fill="#b8405e" stroke="{line}" stroke-width="1.5"/><ellipse cx="256" cy="314" rx="5.5" ry="3.5" fill="#ff8fa8"/></g>'''


def paw(arm_fill, paw_fill, line, imp_out, imp_in):
    impact = ('<line x1="146" y1="353" x2="155" y2="361"/><line x1="160" y1="340" x2="164" y2="351"/>'
              '<line x1="138" y1="372" x2="150" y2="372"/>')
    return f'''
    <g class="pose-up">
      <ellipse cx="190" cy="331" rx="31" ry="20" transform="rotate(40 190 331)" fill="{arm_fill}" stroke="{line}" stroke-width="2.5"/>
      <circle cx="160" cy="302" r="20" fill="{paw_fill}" stroke="{line}" stroke-width="2.5"/>
      <ellipse cx="160" cy="308" rx="8" ry="6" fill="{PAW_PINK}"/>
      <circle cx="148" cy="297" r="3.6" fill="{PAW_PINK}"/><circle cx="157" cy="291" r="3.6" fill="{PAW_PINK}"/>
      <circle cx="167" cy="292" r="3.6" fill="{PAW_PINK}"/><circle cx="173" cy="300" r="3.2" fill="{PAW_PINK}"/>
    </g>
    <g class="pose-down">
      <ellipse cx="196" cy="350" rx="27" ry="20" transform="rotate(-42 196 350)" fill="{arm_fill}" stroke="{line}" stroke-width="2.5"/>
      <ellipse cx="180" cy="374" rx="22" ry="14" fill="{paw_fill}" stroke="{line}" stroke-width="2.5"/>
      <path d="M168,368 L168,376 M177,366 L177,375 M186,367 L186,376" fill="none" stroke="{line}" stroke-width="2" stroke-linecap="round" opacity="0.7"/>
      <g stroke="{imp_out}" stroke-width="6.5" stroke-linecap="round">{impact}</g>
      <g stroke="{imp_in}" stroke-width="3.5" stroke-linecap="round">{impact}</g>
    </g>
'''


def paws(*args):
    a = paw(*args)
    return ('  <g id="handL">' + a + '  </g>\n'
            '  <g id="handR">\n    <g transform="translate(512 0) scale(-1 1)">' + a + '    </g>\n  </g>\n')


def body(c, belly):
    return (f'  <path d="{BODY}" fill="url(#fur)" stroke="{c["line"]}" stroke-width="2.5"/>\n'
            f'  <ellipse cx="256" cy="352" rx="44" ry="34" fill="{belly}" opacity="0.95"/>')


def mirror(path_d):
    """Mirror a left-side path made of x,y pairs across the head's centre line (x = 256)."""
    res = []
    for t in path_d.split():
        cmd = ''
        while t and t[0].isalpha():
            cmd += t[0]
            t = t[1:]
        if t and ',' in t:
            x, y = t.split(',')
            t = f'{512 - float(x):g},{y}'
        res.append(cmd + t)
    return ' '.join(res)


def both(path_d, attrs):
    return f'  <path d="{path_d}" {attrs}/>\n  <path d="{mirror(path_d)}" {attrs}/>'


def doc(c, layers):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512"
     data-name="{c['name']}" data-crop="{c.get('crop', '96 120 320 380')}"
     data-counter-x="256" data-counter-y="{c.get('counter_y', 432)}" data-counter-fill="{c['counter'][0]}" data-counter-stroke="{c['counter'][1]}">
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


def dots(color, pts, r=1.5, opacity=0.7):
    return '\n'.join(f'    <circle cx="{x}" cy="{y}" r="{r}" fill="{color}" opacity="{opacity}"/>' for x, y in pts)


STAR_PTS = [(60, 70), (120, 40), (40, 180), (470, 200), (455, 40), (330, 50), (90, 290), (430, 300)]


def paw_print(x, y, s, color, opacity=0.35):
    return (f'<g transform="translate({x} {y}) scale({s})" fill="{color}" opacity="{opacity}">'
            '<ellipse cx="0" cy="6" rx="9" ry="7"/><circle cx="-10" cy="-4" r="4"/><circle cx="-3" cy="-10" r="4"/>'
            '<circle cx="5" cy="-10" r="4"/><circle cx="11" cy="-3" r="4"/></g>')


def desk_top(rim, line):
    return f'  <rect x="98" y="352" width="316" height="16" rx="5" fill="{rim}" stroke="{line}" stroke-width="2"/>'


# ---------- characters ----------

def kitten():
    c = dict(
        id='kitten', name='Kitty', note='Original chibi kitten with a basket of yarn.',
        sky=('#ffd6e8', '#f78fb3', '#7a2c55'), glow=('#fff4fa', '#ffb3d1'), iris=('#2f6b2f', '#5fbf4a', '#d9ff9e'),
        fur=('#ffd9a8', '#f2a65a'), line='#9a5a24', sparkle='#fff4fa', counter=('#fff7e6', '#7a4510'),
        desk=('#e8c48a', '#b98a4a'),
        bg=dots('#fff4fa', STAR_PTS) + '\n    ' + paw_print(70, 400, 1.6, '#fff4fa') + paw_print(450, 380, 1.3, '#fff4fa'),
    )
    ear = 'M190,206 L182,150 L232,180Z'
    inner = 'M196,198 L191,162 L222,182Z'
    layers = f'''{body(c, '#fff3e0')}
{both(ear, f'fill="url(#fur)" stroke="{c['line']}" stroke-width="2.5" stroke-linejoin="round"')}
{both(inner, 'fill="#ffb3c6"')}
{head(c)}
  <path d="M240,176 L246,196 M256,172 L256,194 M272,176 L266,196" stroke="#e08a3c" stroke-width="5" stroke-linecap="round"/>
{eyes()}
{snout(c, muzzle='#fff3e0')}
  <path d="{BOARD}" fill="url(#desk)" stroke="#7a5326" stroke-width="3" stroke-linejoin="round"/>
  <g stroke="#9c6d33" stroke-width="2" opacity="0.6" fill="none">
    {''.join(f'<path d="M106,{y} Q160,{y - 6} 214,{y} T322,{y} T406,{y}"/>' for y in range(384, 486, 16))}
  </g>
{desk_top('#d9ab66', '#7a5326')}
  <circle cx="148" cy="348" r="18" fill="#7ec8e3" stroke="#3a7d99" stroke-width="2"/>
  <path d="M134,342 Q148,334 162,346 M132,352 Q148,344 164,356" fill="none" stroke="#3a7d99" stroke-width="2"/>
  <circle cx="364" cy="348" r="18" fill="#c39bff" stroke="#6b42b8" stroke-width="2"/>
  <path d="M350,342 Q364,334 378,346 M348,352 Q364,344 380,356" fill="none" stroke="#6b42b8" stroke-width="2"/>
  <path d="M364,366 Q380,400 360,440" fill="none" stroke="#c39bff" stroke-width="3"/>
{paws('url(#fur)', '#fff3e0', c['line'], '#7a2c55', '#ffe3ef')}'''
    return c, layers


def puppy():
    c = dict(
        id='puppy', name='Puppy', note='Original chibi puppy at its toy box.',
        sky=('#b9e6ff', '#4aa3df', '#123d63'), glow=('#ffffff', '#9ad7ff'), iris=('#2b1a0e', '#6b4226', '#c49a6c'),
        fur=('#fff8ee', '#ead6bd'), line='#8a6a4a', sparkle='#ffffff', counter=('#ffffff', '#123d63'),
        desk=('#ff7b6b', '#d64545'),
        bg='''    <ellipse cx="110" cy="120" rx="60" ry="18" fill="#ffffff" opacity="0.55"/>
    <ellipse cx="400" cy="80" rx="70" ry="20" fill="#ffffff" opacity="0.5"/>''',
    )
    ear = 'M196,184 C164,180 146,214 152,262 C156,290 176,294 184,276 C190,252 196,224 208,198Z'
    layers = f'''{body(c, '#ffffff')}
  <path d="M206,312 Q256,334 306,312 L304,326 Q256,348 208,326Z" fill="#e63946" stroke="#9d1d28" stroke-width="2"/>
  <circle cx="256" cy="340" r="8" fill="#ffd166" stroke="#b8860b" stroke-width="2"/>
{head(c)}
  <ellipse cx="292" cy="236" rx="26" ry="22" fill="#c49a6c" opacity="0.85"/>
{both(ear, 'fill="#a87a50" stroke="#6b4a2a" stroke-width="2.5" stroke-linejoin="round"')}
{eyes()}
{snout(c, muzzle='#ffffff', whiskers=False, nose='#2b1a0e')}
  <path d="{BOARD}" fill="url(#desk)" stroke="#8d1b22" stroke-width="3" stroke-linejoin="round"/>
{desk_top('#ffd166', '#b8860b')}
  <g opacity="0.9">{paw_print(150, 400, 1.2, '#ffffff', 0.5)}{paw_print(362, 400, 1.2, '#ffffff', 0.5)}</g>
  <path d="M182,350 a9,9 0 1,1 10,-8 L320,342 a9,9 0 1,1 10,8 a9,9 0 1,1 -10,8 L192,358 a9,9 0 1,1 -10,-8Z" fill="#fff8ee" stroke="#8a6a4a" stroke-width="2"/>
{paws('url(#fur)', '#fff8ee', c['line'], '#123d63', '#ffffff')}'''
    return c, layers


def bunny():
    c = dict(
        id='bunny', name='Bunny', note='Original chibi bunny at a crate of carrots.',
        sky=('#e8ffd9', '#8fd16a', '#2f5e1d'), glow=('#ffffff', '#d4ffb3'), iris=('#4a1030', '#b0306a', '#ff9ac8'),
        fur=('#ffffff', '#e6e2ee'), line='#8f86a3', sparkle='#ffffff', counter=('#fff3d6', '#5a3414'),
        desk=('#d9a066', '#a8692f'),
        bg=dots('#ffffff', STAR_PTS, 2, 0.6) + '\n    <path d="M0,440 Q128,410 256,440 T512,440 L512,512 L0,512Z" fill="#4f8f30" opacity="0.6"/>',
    )
    c['crop'] = '86 66 340 404'  # taller, to fit the ears; same shape as the others
    ear = 'M224,184 C206,130 200,88 216,76 C236,66 248,120 248,176Z'
    inner = 'M226,170 C214,126 212,98 220,90 C230,86 238,126 240,168Z'
    layers = f'''{body(c, '#ffffff')}
{both(ear, f'fill="url(#fur)" stroke="{c['line']}" stroke-width="2.5"')}
{both(inner, 'fill="#ffc2d6"')}
{head(c)}
{eyes()}
{snout(c, nose='#ff7d9c')}
  <rect x="250" y="301" width="12" height="9" rx="2" fill="#ffffff" stroke="{c['line']}" stroke-width="1.5" class="mouth-closed"/>
  <path d="{BOARD}" fill="url(#desk)" stroke="#6b3f17" stroke-width="3" stroke-linejoin="round"/>
  <g stroke="#6b3f17" stroke-width="2" opacity="0.55"><line x1="106" y1="404" x2="406" y2="404"/><line x1="107" y1="446" x2="405" y2="446"/></g>
  <g fill="none" stroke="#f0c48e" stroke-width="1.5" opacity="0.7"><path d="M150,384 Q180,380 210,385"/><path d="M300,466 Q330,462 360,467"/></g>
  {''.join(f'<path d="M{x},356 L{x + 7},318 L{x + 14},356Z" fill="#ff8c1a" stroke="#c05a00" stroke-width="2" stroke-linejoin="round"/><path d="M{x + 7},320 l-8,-14 M{x + 7},320 l0,-17 M{x + 7},320 l8,-14" stroke="#3fa34d" stroke-width="4" stroke-linecap="round"/>' for x in (116, 214, 284, 380))}
{desk_top('#c98b4b', '#6b3f17')}
{paws('url(#fur)', '#ffffff', c['line'], '#2f5e1d', '#fff3d6')}'''
    return c, layers


def hamster():
    c = dict(
        id='hamster', name='Hamster', note='Original chibi hamster with a sack of sunflower seeds.',
        sky=('#fff1c2', '#ffbf47', '#7a4a00'), glow=('#fffbe8', '#ffd97a'), iris=('#1a1210', '#4a2e22', '#a07050'),
        fur=('#ffe6b8', '#f0b465'), line='#a0682a', sparkle='#fffbe8', counter=('#ffffff', '#5a3414'),
        desk=('#c9a46a', '#97733f'),
        bg=dots('#fffbe8', STAR_PTS, 2, 0.6),
    )
    layers = f'''{body(c, '#fff8ea')}
  <circle cx="200" cy="178" r="22" fill="url(#fur)" stroke="{c['line']}" stroke-width="2.5"/>
  <circle cx="312" cy="178" r="22" fill="url(#fur)" stroke="{c['line']}" stroke-width="2.5"/>
  <circle cx="200" cy="176" r="9" fill="#ffb3c6"/><circle cx="312" cy="176" r="9" fill="#ffb3c6"/>
  <ellipse cx="256" cy="258" rx="92" ry="78" fill="url(#fur)" stroke="{c['line']}" stroke-width="2.5"/>
  <path d="M256,190 C232,212 228,250 240,268 C246,278 266,278 272,268 C284,250 280,212 256,190Z" fill="#fff8ea" opacity="0.85"/>
  <ellipse cx="190" cy="298" rx="34" ry="28" fill="#fff8ea"/><ellipse cx="322" cy="298" rx="34" ry="28" fill="#fff8ea"/>
{eyes()}
{snout(c, nose='#ff8fa8')}
  <path d="{BOARD}" fill="url(#desk)" stroke="#8a6a3a" stroke-width="3" stroke-linejoin="round"/>
  <g stroke="#a88b5a" stroke-width="1.5" opacity="0.5">{''.join(f'<line x1="{x}" y1="366" x2="{x + 4}" y2="484"/>' for x in range(118, 400, 12))}</g>
  <path d="M98,360 Q130,346 160,360 Q200,344 240,360 Q280,344 320,360 Q360,344 414,360 L412,372 L100,372Z" fill="#d9bf8c" stroke="#8a6a3a" stroke-width="2"/>
  {''.join(f'<ellipse cx="{x}" cy="{y}" rx="5" ry="9" transform="rotate({r} {x} {y})" fill="#3a3a3a" stroke="#ffffff" stroke-width="1.2"/>' for x, y, r in ((140, 352, -30), (186, 346, 20), (226, 352, -10), (300, 348, 25), (344, 352, -20), (382, 346, 10)))}
{paws('url(#fur)', '#fff8ea', c['line'], '#7a4a00', '#fffbe8')}'''
    return c, layers


def fox():
    c = dict(
        id='fox', name='Fox Cub', note='Original chibi fox cub on a forest stump.',
        sky=('#ffb07a', '#c2410c', '#2a0f05'), glow=('#fff1c2', '#ff9a3c'), iris=('#5a2d00', '#c47a00', '#ffd166'),
        fur=('#ffa45c', '#e8640a'), line='#8a3a00', sparkle='#fff1c2', counter=('#fff3d6', '#3b1f0a'),
        desk=('#8b5a2b', '#5a3414'),
        bg=dots('#fff1c2', STAR_PTS) + '\n    <path d="M0,512 L40,380 L80,512Z M432,512 L472,370 L512,512Z" fill="#3a1a08" opacity="0.6"/>',
    )
    ear = 'M184,214 L172,140 L236,178Z'
    inner = 'M190,204 L182,158 L224,182Z'
    cheek = 'M256,252 C240,264 214,262 182,272 C190,312 226,330 256,330Z'
    layers = f'''{body(c, '#fff4e6')}
{both(ear, f'fill="url(#fur)" stroke="{c['line']}" stroke-width="2.5" stroke-linejoin="round"')}
{both(inner, 'fill="#3b1f0a"')}
{head(c)}
{both(cheek, 'fill="#fff4e6"')}
{eyes()}
{snout(c, nose='#2b1208')}
  <path d="M104,364 L408,364 L414,486 L98,486Z" fill="url(#desk)" stroke="#3b1f0a" stroke-width="3" stroke-linejoin="round"/>
  <g stroke="#3b1f0a" stroke-width="2.5" opacity="0.45">{''.join(f'<path d="M{x},372 Q{x + 6},420 {x - 2},482" fill="none"/>' for x in range(124, 400, 30))}</g>
  <ellipse cx="256" cy="362" rx="156" ry="14" fill="#e8c48a" stroke="#5a3414" stroke-width="2.5"/>
  <ellipse cx="256" cy="362" rx="100" ry="9" fill="none" stroke="#c49a5a" stroke-width="1.5"/>
  <ellipse cx="256" cy="362" rx="50" ry="5" fill="none" stroke="#c49a5a" stroke-width="1.5"/>
  <path d="M370,350 q8,-18 22,-12 q-4,14 -22,12Z" fill="#4caf50" stroke="#2e7d32" stroke-width="1.5"/>
{paws('url(#fur)', '#2b1208', c['line'], '#2a0f05', '#ffd166')}'''
    return c, layers


def panda():
    c = dict(
        id='panda', name='Panda', note='Original chibi panda at a bamboo table — the final unlock.',
        sky=('#d4f7d4', '#5cbf7a', '#163d22'), glow=('#ffffff', '#b6f0c4'), iris=('#1a1a1a', '#3a3a3a', '#7a7a7a'),
        fur=('#ffffff', '#ebebeb'), line='#3a3a3a', sparkle='#ffffff', counter=('#ffffff', '#163d22'),
        desk=('#9ccc65', '#558b2f'),
        bg=dots('#ffffff', STAR_PTS, 2, 0.6)
        + ''.join(f'\n    <g stroke="#2e7d32" stroke-width="10" opacity="0.35"><line x1="{x}" y1="0" x2="{x}" y2="512"/></g>' for x in (34, 478)),
    )
    patch = 'M206,248 C192,256 190,286 204,294 C220,300 238,284 240,266 C242,250 222,240 206,248Z'
    layers = f'''  <path d="{BODY}" fill="#222222" stroke="#000000" stroke-width="2.5"/>
  <ellipse cx="256" cy="352" rx="46" ry="36" fill="#ffffff"/>
  <circle cx="192" cy="186" r="24" fill="#222222"/><circle cx="320" cy="186" r="24" fill="#222222"/>
{head(c)}
{both(patch, 'fill="#222222"')}
{eyes()}
{snout(c, muzzle='#ffffff', whiskers=False, nose='#222222')}
  <path d="{BOARD}" fill="url(#desk)" stroke="#33691e" stroke-width="3" stroke-linejoin="round"/>
  <g stroke="#33691e" stroke-width="2.5">{''.join(f'<line x1="{x}" y1="366" x2="{x}" y2="484"/>' for x in range(148, 400, 44))}</g>
  <g stroke="#7cb342" stroke-width="3" stroke-linecap="round">{''.join(f'<line x1="{x - 14}" y1="{y}" x2="{x + 14}" y2="{y}"/>' for x in range(170, 380, 44) for y in (400, 452))}</g>
{desk_top('#aed581', '#33691e')}
  <path d="M332,352 C326,330 334,318 346,314 M346,314 q14,-8 22,2 q-12,10 -22,-2Z" fill="#66bb6a" stroke="#2e7d32" stroke-width="2"/>
{paws('#222222', '#222222', '#000000', '#163d22', '#b6f0c4')}'''
    c['counter_y'] = 434
    return c, layers


CHARACTERS = [kitten, puppy, bunny, hamster, fox, panda]

if __name__ == '__main__':
    os.makedirs('avatars', exist_ok=True)
    for make in CHARACTERS:
        c, layers = make()
        path = os.path.join('avatars', c['id'] + '.svg')
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(doc(c, layers))
        print('wrote', path)

"""Generates avatars/miku.svg — a chibi Hatsune Miku fan-art avatar that follows the same
structure as baby-jesus.svg (#handL/#handR with .pose-up/.pose-down, mouth states, #bg, #holyGlow).

Run from the project root:  python tools/make_miku.py
"""

SKIN_LINE = '#e0a284'


def arm(sleeve_fill, sleeve_line, fold, cuff_fill, cuff_line, imp_out, imp_in):
    impact = ('<line x1="146" y1="353" x2="155" y2="361"/>'
              '<line x1="160" y1="340" x2="164" y2="351"/>'
              '<line x1="138" y1="372" x2="150" y2="372"/>')
    return f'''
    <g class="pose-up">
      <ellipse cx="190" cy="331" rx="31" ry="21" transform="rotate(40 190 331)" fill="{sleeve_fill}" stroke="{sleeve_line}" stroke-width="2.5"/>
      <path d="M197,322 Q190,331 196,342" fill="none" stroke="{fold}" stroke-width="2" stroke-linecap="round" opacity="0.8"/>
      <ellipse cx="169" cy="313" rx="8" ry="16" transform="rotate(40 169 313)" fill="{cuff_fill}" stroke="{cuff_line}" stroke-width="2.5"/>
      <circle cx="158" cy="300" r="17" fill="url(#skin)" stroke="{SKIN_LINE}" stroke-width="2"/>
      <ellipse cx="170" cy="293" rx="6" ry="7.5" transform="rotate(-20 170 293)" fill="#ffe3cf" stroke="{SKIN_LINE}" stroke-width="2"/>
      <path d="M147,293 Q150,289 154,292 M154,292 Q157,288 161,291" fill="none" stroke="{SKIN_LINE}" stroke-width="1.8" stroke-linecap="round"/>
      <ellipse cx="153" cy="306" rx="5" ry="3" fill="#ff9fb2" opacity="0.45"/>
      <circle cx="152" cy="295" r="2.2" fill="#ffffff" opacity="0.8"/>
    </g>
    <g class="pose-down">
      <ellipse cx="196" cy="352" rx="27" ry="21" transform="rotate(-42 196 352)" fill="{sleeve_fill}" stroke="{sleeve_line}" stroke-width="2.5"/>
      <path d="M205,345 Q197,350 197,360" fill="none" stroke="{fold}" stroke-width="2" stroke-linecap="round" opacity="0.8"/>
      <ellipse cx="183" cy="365" rx="16" ry="7" transform="rotate(-10 183 365)" fill="{cuff_fill}" stroke="{cuff_line}" stroke-width="2.5"/>
      <ellipse cx="179" cy="375" rx="20" ry="13" fill="url(#skin)" stroke="{SKIN_LINE}" stroke-width="2"/>
      <path d="M166,371 Q169,367 173,370 M173,370 Q176,366 180,369 M180,369 Q183,365 187,368" fill="none" stroke="{SKIN_LINE}" stroke-width="1.8" stroke-linecap="round"/>
      <ellipse cx="172" cy="379" rx="5" ry="2.5" fill="#ff9fb2" opacity="0.45"/>
      <g stroke="{imp_out}" stroke-width="6.5" stroke-linecap="round">{impact}</g>
      <g stroke="{imp_in}" stroke-width="3.5" stroke-linecap="round">{impact}</g>
    </g>
'''


a = arm('#2f333b', '#15171b', '#5a616c', '#39c5bb', '#1f8f87', '#0d2e2c', '#8ff7ec')
hands = ('  <g id="handL">' + a + '  </g>\n'
         '  <g id="handR">\n    <g transform="translate(512 0) scale(-1 1)">' + a + '    </g>\n  </g>\n')

# Piano keys along the top edge of the synth.
X0, X1, W = 112, 400, 12
n = (X1 - X0) // W
key_lines = ''.join(f'<line x1="{X0 + i * W}" y1="352" x2="{X0 + i * W}" y2="366"/>' for i in range(1, n))
pattern = [1, 1, 0, 1, 1, 1, 0]  # a black key follows white keys C D _ F G A _
black_keys = ''.join(f'<rect x="{X0 + (i + 1) * W - 3.5}" y="351" width="7" height="9" rx="1"/>'
                     for i in range(n - 1) if pattern[i % 7])

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512"
     data-name="Hatsune Miku" data-crop="96 120 320 380"
     data-counter-x="256" data-counter-y="420" data-counter-fill="#8ff7ec" data-counter-stroke="#0b2826">
  <!-- Chibi Hatsune Miku fan art. Hatsune Miku is a character by Crypton Future Media, INC. (piapro.net) -->
  <style>
    .pose-down, .mouth-open {{ display: none; }}
    .tap-left  #handL .pose-up, .tap-right #handR .pose-up {{ display: none; }}
    .tap-left  #handL .pose-down, .tap-right #handR .pose-down {{ display: inline; }}
    .tap-left .mouth-closed, .tap-right .mouth-closed {{ display: none; }}
    .tap-left .mouth-open, .tap-right .mouth-open {{ display: inline; }}
    .chroma #bg, .chroma #holyGlow {{ display: none; }}
  </style>
  <defs>
    <radialGradient id="sky" cx="50%" cy="40%" r="75%">
      <stop offset="0%" stop-color="#16424a"/>
      <stop offset="60%" stop-color="#0d1e2a"/>
      <stop offset="100%" stop-color="#070d14"/>
    </radialGradient>
    <radialGradient id="glow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#c9fff8" stop-opacity="0.85"/>
      <stop offset="45%" stop-color="#39c5bb" stop-opacity="0.4"/>
      <stop offset="100%" stop-color="#39c5bb" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="skin" cx="45%" cy="40%" r="65%">
      <stop offset="0%" stop-color="#fff3e8"/>
      <stop offset="75%" stop-color="#ffe2cf"/>
      <stop offset="100%" stop-color="#f7cbb2"/>
    </radialGradient>
    <linearGradient id="iris" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#0b4f4c"/>
      <stop offset="55%" stop-color="#1fa59b"/>
      <stop offset="100%" stop-color="#8ff7ec"/>
    </linearGradient>
    <linearGradient id="hair" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#4fd8ce"/>
      <stop offset="100%" stop-color="#22a69c"/>
    </linearGradient>
    <linearGradient id="tail" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#3fcfc4"/>
      <stop offset="100%" stop-color="#1b8f87"/>
    </linearGradient>
    <linearGradient id="shirt" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#e3e7ec"/>
      <stop offset="100%" stop-color="#b9c0c9"/>
    </linearGradient>
    <linearGradient id="synth" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#3a3f47"/>
      <stop offset="100%" stop-color="#1f2227"/>
    </linearGradient>
    <filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="4"/></filter>
    <g id="sparkle">
      <path d="M0,-12 C1.5,-3 3,-1.5 12,0 C3,1.5 1.5,3 0,12 C-1.5,3 -3,1.5 -12,0 C-3,-1.5 -1.5,-3 0,-12Z" fill="#c9fff8"/>
    </g>
  </defs>

  <!-- Concert background -->
  <g id="bg">
    <rect id="sky-rect" width="512" height="512" fill="url(#sky)"/>
    <path d="M150,0 L210,0 L300,512 L120,512Z" fill="#39c5bb" opacity="0.07"/>
    <path d="M330,0 L380,0 L420,512 L250,512Z" fill="#39c5bb" opacity="0.06"/>
    <g fill="#39c5bb" opacity="0.55" font-family="Segoe UI Symbol, sans-serif">
      <text x="60" y="110" font-size="34">&#9834;</text>
      <text x="420" y="90" font-size="30">&#9835;</text>
      <text x="450" y="260" font-size="26">&#9834;</text>
      <text x="40" y="300" font-size="24">&#9835;</text>
    </g>
  </g>

  <circle id="holyGlow" cx="256" cy="250" r="165" fill="url(#glow)"/>

  <!-- Twin tails (behind everything) -->
  <path d="M190,182 C140,190 108,262 110,342 C111,400 120,440 134,474 C150,432 160,384 164,334 C168,276 178,222 198,198Z"
        fill="url(#tail)" stroke="#16807a" stroke-width="2"/>
  <path d="M152,226 C132,290 132,380 140,440" fill="none" stroke="#1b8f87" stroke-width="2.5" stroke-linecap="round" opacity="0.7"/>
  <path d="M322,182 C372,190 404,262 402,342 C401,400 392,440 378,474 C362,432 352,384 348,334 C344,276 334,222 314,198Z"
        fill="url(#tail)" stroke="#16807a" stroke-width="2"/>
  <path d="M360,226 C380,290 380,380 372,440" fill="none" stroke="#1b8f87" stroke-width="2.5" stroke-linecap="round" opacity="0.7"/>

  <!-- Back hair -->
  <path d="M166,252 C160,176 206,146 256,146 C306,146 352,176 346,252 L340,316 L172,316Z" fill="#26a99f"/>

  <!-- Shirt -->
  <path d="M146,372 C146,326 186,308 226,306 L286,306 C326,308 366,326 366,372Z" fill="url(#shirt)" stroke="#8f98a3" stroke-width="2"/>
  <path d="M168,340 C176,330 186,324 196,320" fill="none" stroke="#39c5bb" stroke-width="3" stroke-linecap="round"/>
  <path d="M344,340 C336,330 326,324 316,320" fill="none" stroke="#39c5bb" stroke-width="3" stroke-linecap="round"/>

  <!-- Head -->
  <circle cx="256" cy="250" r="80" fill="url(#skin)"/>

  <!-- Blush -->
  <ellipse cx="204" cy="292" rx="16" ry="9" fill="#ff8fa8" opacity="0.5" filter="url(#soft)"/>
  <ellipse cx="308" cy="292" rx="16" ry="9" fill="#ff8fa8" opacity="0.5" filter="url(#soft)"/>

  <!-- Eyes -->
  <g>
    <ellipse cx="222" cy="266" rx="17" ry="22" fill="#ffffff"/>
    <ellipse cx="222" cy="268" rx="14.5" ry="20" fill="url(#iris)"/>
    <ellipse cx="222" cy="269" rx="6.5" ry="9" fill="#06302e"/>
    <circle cx="215" cy="258" r="6.5" fill="#ffffff"/>
    <circle cx="228" cy="277" r="2.8" fill="#ffffff"/>
    <path d="M201,260 Q221,232 243,258" fill="none" stroke="#1d2b33" stroke-width="5.5" stroke-linecap="round"/>
    <path d="M202,260 L192,253 M205,255 L197,247" stroke="#1d2b33" stroke-width="3.5" stroke-linecap="round"/>
  </g>
  <g>
    <ellipse cx="290" cy="266" rx="17" ry="22" fill="#ffffff"/>
    <ellipse cx="290" cy="268" rx="14.5" ry="20" fill="url(#iris)"/>
    <ellipse cx="290" cy="269" rx="6.5" ry="9" fill="#06302e"/>
    <circle cx="283" cy="258" r="6.5" fill="#ffffff"/>
    <circle cx="296" cy="277" r="2.8" fill="#ffffff"/>
    <path d="M269,258 Q291,232 311,260" fill="none" stroke="#1d2b33" stroke-width="5.5" stroke-linecap="round"/>
    <path d="M310,260 L320,253 M307,255 L315,247" stroke="#1d2b33" stroke-width="3.5" stroke-linecap="round"/>
  </g>

  <!-- Nose and mouth -->
  <ellipse cx="256" cy="290" rx="2" ry="1.5" fill="#f0a88c"/>
  <g class="mouth-closed">
    <path d="M246,302 Q256,314 266,302 Q256,306 246,302Z" fill="#d95c78"/>
  </g>
  <g class="mouth-open">
    <ellipse cx="256" cy="306" rx="8.5" ry="9.5" fill="#b8405e"/>
    <ellipse cx="256" cy="311" rx="5.5" ry="3.5" fill="#ff8fa8"/>
  </g>

  <!-- Bangs with pointed strands and a centre part -->
  <path d="M170,252 C162,180 204,150 256,150 C308,150 350,180 342,252
           Q336,236 328,220 Q324,234 316,242 Q310,226 300,212 Q294,226 284,236
           Q278,220 268,206 Q262,218 256,228 Q250,218 244,206 Q234,220 228,236
           Q218,226 212,212 Q202,226 196,242 Q188,234 184,220 Q176,236 170,252Z"
        fill="url(#hair)" stroke="#1b8f87" stroke-width="2" stroke-linejoin="round"/>
  <path d="M214,176 C232,166 252,163 272,166" fill="none" stroke="#a6f3ec" stroke-width="4" stroke-linecap="round" opacity="0.8"/>

  <!-- Side locks framing the face -->
  <path d="M178,212 C168,258 174,302 192,338 C194,302 196,262 202,226Z" fill="url(#hair)" stroke="#1b8f87" stroke-width="2"/>
  <path d="M334,212 C344,258 338,302 320,338 C318,302 316,262 310,226Z" fill="url(#hair)" stroke="#1b8f87" stroke-width="2"/>

  <!-- Headset -->
  <circle cx="174" cy="262" r="19" fill="#3a3f47" stroke="#1c1f24" stroke-width="2"/>
  <circle cx="174" cy="262" r="11" fill="none" stroke="#39c5bb" stroke-width="3.5"/>
  <circle cx="338" cy="262" r="19" fill="#3a3f47" stroke="#1c1f24" stroke-width="2"/>
  <circle cx="338" cy="262" r="11" fill="none" stroke="#39c5bb" stroke-width="3.5"/>
  <path d="M182,278 Q194,304 224,306" fill="none" stroke="#3a3f47" stroke-width="3.5" stroke-linecap="round"/>
  <ellipse cx="228" cy="306" rx="6" ry="4" fill="#2a2d34"/>

  <!-- Hair ties -->
  <rect x="176" y="174" width="18" height="24" rx="3" transform="rotate(-28 185 186)" fill="#2a2d34" stroke="#e85a8a" stroke-width="2.5"/>
  <rect x="318" y="174" width="18" height="24" rx="3" transform="rotate(28 327 186)" fill="#2a2d34" stroke="#e85a8a" stroke-width="2.5"/>

  <!-- Collar and tie -->
  <path d="M222,318 L256,344 L290,318 L298,330 L256,352 L214,330Z" fill="#eef1f4" stroke="#8f98a3" stroke-width="2" stroke-linejoin="round"/>
  <rect x="248" y="338" width="16" height="10" rx="2" fill="#39c5bb" stroke="#1f8f87" stroke-width="2"/>
  <path d="M249,348 L263,348 L268,366 L256,374 L244,366Z" fill="#39c5bb" stroke="#1f8f87" stroke-width="2" stroke-linejoin="round"/>

  <!-- Synth stand -->
  <g stroke="#2a2d34" stroke-width="12" stroke-linecap="round">
    <line x1="140" y1="432" x2="112" y2="492"/>
    <line x1="160" y1="432" x2="188" y2="492"/>
    <line x1="372" y1="432" x2="400" y2="492"/>
    <line x1="352" y1="432" x2="324" y2="492"/>
  </g>

  <!-- Synth -->
  <path d="M104,364 L408,364 L400,440 L112,440Z" fill="url(#synth)" stroke="#121417" stroke-width="3" stroke-linejoin="round"/>
  <rect x="110" y="350" width="292" height="17" rx="3" fill="#f4f6f9" stroke="#121417" stroke-width="2"/>
  <g stroke="#9aa1ab" stroke-width="1">{key_lines}</g>
  <g fill="#1c1f24">{black_keys}</g>
  <line x1="112" y1="378" x2="400" y2="378" stroke="#39c5bb" stroke-width="3" opacity="0.85"/>
  <circle cx="132" cy="398" r="6" fill="#2a2d34" stroke="#39c5bb" stroke-width="2"/>
  <circle cx="150" cy="398" r="6" fill="#2a2d34" stroke="#39c5bb" stroke-width="2"/>
  <circle cx="372" cy="396" r="3" fill="#ff5f8f"/>
  <circle cx="384" cy="396" r="3" fill="#39c5bb"/>
  <rect x="190" y="390" width="132" height="40" rx="5" fill="#0b1416" stroke="#39c5bb" stroke-width="1.5" opacity="0.9"/>

  <!-- Animatable hands: add class tap-left / tap-right to the <svg> to slap -->
{hands}
  <!-- Sparkles -->
  <use href="#sparkle" transform="translate(122 150) scale(0.9)"/>
  <use href="#sparkle" transform="translate(390 230) scale(0.7)"/>
  <use href="#sparkle" transform="translate(372 146) scale(0.5)" opacity="0.8"/>
</svg>
'''

with open('avatars/miku.svg', 'w', encoding='utf-8', newline='\n') as f:
    f.write(svg)
print('wrote avatars/miku.svg')

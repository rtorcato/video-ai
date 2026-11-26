# Style guide: "talking head + animated UI cards"

Shared by `video-basic` and `video-pro`. Bright gradient backgrounds, white UI cards that spring in, terminals typing real commands, checklists that tick off, highlighter caption pills, and a rounded window for the presenter's camera.

## Brand

Use the project's own brand first: look for `brand/`, `DESIGN.md`, a favicon SVG, a logo, a mascot or a cover image in the repo or on its docs site.

If the user keeps a `brand.json` (in the project root, or the folder they point to), read it and use its values over the defaults below:

```json
{
  "name": "Acme CLI",
  "url": "acme.dev",
  "colors": { "accent": "#22c55e", "dark": "#0a1422", "light": "#f8fafc", "pill": "#ffd43b", "pillText": "#141420" },
  "backgrounds": ["#5b5cf0,#c26bd6", "#4f7cf7,#9a6df2", "#2fae86,#8fdcc0"],
  "fonts": { "heading": "Inter Display", "body": "Inter", "mono": "DejaVu Sans Mono" },
  "logo": "brand/logo.svg",
  "mascot": "brand/mascot.png"
}
```

Every field is optional. `backgrounds` are gradient pairs, one per section.

The [style templates](#styles) read the same file. Paste it into the page's `BRAND` constant, since a `file://` page can't fetch JSON. They use `colors.accent`, `colors.dark` or `colors.light` (the page background for that theme) and `fonts`. They ignore `backgrounds`, because none of them use gradients. To set an exact board token, add a `styles` block keyed by style and theme:

```json
{ "styles": { "ledger": { "dark": { "--acc": "#8AB4FF" }, "light": { "--acc": "#1E40AF" } } } }
```

Re-check contrast after any colour override. Every board pair is WCAG AA in both themes, and your brand colour may not be.

## Canvas and fonts

- `html,body{width:1920px;height:1080px;overflow:hidden}`; everything absolutely positioned.
- Headings: `Inter Display` or `Inter`, weight 850–900, letter-spacing −0.035 to −0.05em.
- Terminals and code: a monospace such as `DejaVu Sans Mono` or `JetBrains Mono`.
- Icon tiles: `Noto Color Emoji` (or the platform emoji font).
- Check what's installed (`fc-list` on Linux, Font Book on macOS) and fall back gracefully.

## Default tokens

- **Backgrounds:** stack full-screen `.bg` divs (a radial white highlight over a 135–170° linear gradient) and crossfade their opacity per section. Defaults: purple `#5b5cf0 → #c26bd6`, blue `#4f7cf7 → #9a6df2`, green `#2fae86 → #8fdcc0`, plus a dark brand field for intros.
- **Cards:** `#fff`, radius 24px, shadow `0 24px 60px rgba(40,20,120,.28)`.
- **Terminal:** dark (`#13151f` or the brand's dark colour), radius 24px, three traffic-light dots, a centred grey title.
- **Caption pill:** `#ffd43b` background, near-black text, 60px weight 850, radius 14px, `rotate(-1.5deg)`, revealed by a left-to-right `clip-path: inset()` wipe. Variants: white, red (`#ff6b6b`).
- **Checklist row:** translucent white (`rgba(255,255,255,.22)`) with a numbered circle. When ticked it turns solid white, the number becomes a green ✓ that springs in, and the text turns dark.
- **Big background word:** 330px, white at 14–16% opacity, drifting slowly sideways.
- **Camera placeholder:** a dark gradient box with a grey head-and-shoulders silhouette and a "● Your talking head here" label with a blinking red dot.

## Animation helpers

Put these at the top of the page script:

```js
const $=id=>document.getElementById(id);
const clamp=(x,a=0,b=1)=>Math.min(b,Math.max(a,x));
const P=(t,s,d)=>clamp((t-s)/d);              // progress of a window starting at s, lasting d
const eo=x=>1-Math.pow(1-x,3);                  // ease-out
const eio=x=>x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2;
const spr=x=>x<=0?0:x>=1?1:1-Math.exp(-6*x)*Math.cos(8.5*x); // spring, ~11% overshoot
const lerp=(a,b,x)=>a+(b-a)*x;
function vis(el,t,a,b){ // scene blur-dissolve in at a, out at b
  const i=eo(P(t,a,.45)),o=1-eio(P(t,b-.45,.45)),v=Math.min(i,o);
  el.style.opacity=v; el.style.filter=v>=.999?"none":`blur(${(1-v)*22}px)`;
  el.style.display=v<=.001?"none":"block";
}
function pill(el,t,s){const x=eo(P(t,s,.4)),sc=spr(P(t,s,.6));
  el.style.clipPath=`inset(0 ${(1-x)*100}% 0 0 round 14px)`;
  el.style.transform=`translateX(-50%) rotate(-1.5deg) scale(${lerp(.9,1,sc)})`;
  el.style.opacity=x>0?1:0;}
```

## Rules for `render(t)`

- Everything is a pure function of `t` in seconds. No CSS transitions, `setTimeout`, `requestAnimationFrame` or `Date.now()`. That is what makes frame-by-frame capture deterministic.
- Give each scene a `[start, end]` window and overlap neighbours by about 0.4s so the blurs crossfade.
- Stagger lists by 0.12–0.25s per item. Springs take 0.7–0.9s.
- Typing effect: slice the command by `(t-start)*24` characters and draw a block cursor that blinks with `Math.floor(t*2.5)%2`. Only the latest line's cursor blinks.
- Expose `window.render` and call `render(0)` on load.

## Styles

Everything above describes the default look: gradients, white cards and caption pills (`templates/index.html`). There are four other looks, each a complete page in `templates/<style>/index.html`:

| Style | Use it for | Look | Motion |
|---|---|---|---|
| `ledger` | tutorials, walkthroughs, explainers | Flat editorial. Inter Tight 800 headings, IBM Plex Mono labels, numbered sections on a faint 160px column grid, one blue accent | Calm: 40px slides along the grid, ease-out. No blur, no spring |
| `prompt` | CLI tools, release notes, changelogs | Terminal-first. All JetBrains Mono: tabs, TUI boxes, a mint accent, an amber highlight. Captions are a full-width status bar | Typing at 24 chars/s with a stepped cursor. Rows appear on their frame. Beats change by switching tabs (hard cuts) |
| `walkthrough` | step-by-step how-tos, settings and setup guides | A generic drawn phone, numbered step discs, progress dots and one caption per step. Navy or cool grey with a teal accent. Manrope plus IBM Plex Mono | The screen slides in 0.3s, the row highlight draws, the tap ring pulses once and the toggle flips. Captions crossfade in 0.2s |
| `gameshow` | 30–60s quizzes and myth-busters: one question per feature, the reveal as the payoff, host VO as the comedy | Quiz-show stage. Black or pale-grey stage, Archivo wide 900 uppercase, A–D keycap options, a yellow question tile, red buzzer accents and a HOST tag for the VO line. JetBrains Mono kickers, clock and split-flap score | A bulb border chases one step every 2 frames. The tile spins in 1.25 turns to −6°, the +1,000 sticker slaps on. Options pop A→D 0.12s apart with a 1.1 overshoot. A 10-tick ring loses one tick per second. The reveal freezes 0.4s, greys the wrong options, fills the correct one yellow and lands a CORRECT stamp. Hard cuts on the VO punchline |

How the style templates work:

- Content lives in one `BEATS` block at the top of the page, so the agent edits data, not markup. Ledger and Prompt share one sample (the homelab-nut beats: `title`, `card`, `terminal`, `caption`, `outro`), so you can compare them like for like. Walkthrough has its own how-to sample: it adds `step` beats and `SCREENS` for the phone, and its `terminal` slot is a settings path. Gameshow has its own quiz sample with `title`, `qnum`, `question`, `countdown`, `reveal` and `score` beats; options are A–D, `answer` is the correct letter, `pick` is the locked-in one, and any beat can take a `vo` host line.
- Wrap a word in `*stars*` to mark the emphasis word. The Walkthrough path highlights it, Gameshow sets it in the buzzer red, and Ledger and Prompt show it plain.
- Every style has a dark and a light theme. Pick one with `?theme=light` while previewing, or set `THEME` in the page before rendering (`render.py` loads the page without a query string).
- The board tokens are WCAG AA for text in both themes. Prompt's light accent (4.7:1) is only for large or bold text. Walkthrough's light tap colour is `#B45309` because brighter ambers fall below 3:1 on white. Keep these values unless you re-check contrast.
- No gradients in any of them. Walkthrough's phone is an original drawn handset: no real device frame, no OS screenshots and no platform icons. Gameshow takes the quiz-show genre only: no logo, host character, question-screen layout, numbered answers, music or SFX from any commercial trivia game, and any buzzer or tick SFX you add must be original or CC0. Its ruled-out options (`#73737F` dark, `#83848F` light) are large bold text at 3.9:1 and 3.7:1; don't make them lighter.
- Each one is a normal page with a deterministic `render(t)` and `window.DURATION`, so `render.py` films it the same way. Add beats by appending to `BEATS.beats` with new `start`/`end` times. Each beat type builds itself.
- They load Google Fonts. Offline, install the fonts locally (the families are named in each page's `<link>`) or set `fonts` in `brand.json`.

## Mascots and logos

- To turn black-on-white art into transparent, recolourable PNGs with PIL: alpha = inverted luminance with a small threshold, then fill with the colour you need.
- An accent-coloured mascot disappears on a background of the same hue. On matching backgrounds, put it on a white or dark tile.
- Inline a favicon SVG as a `<symbol>` and reuse it with `<use>`.

## Pitfalls

- **ID collisions:** helpers build IDs like `prefix+i` (`a0`, `a1`…). Give hand-written elements distinctive IDs (`hA`, `hW`…).
- **Z-order:** elements appended by JS land on top of static markup. Give overlays an explicit `z-index`.
- **Overflow:** long words in big type and stat chips wrap or overflow. Check every busy frame at full size.
- **Time-shifting:** to add an intro in front of a finished timeline, wrap it as `render(t){ intro(t); main(t - T0); }`.
- **Third-party branding:** never reproduce another creator's logos, characters or footage. Use fictional names in sample UI.
- **macOS privacy:** a terminal can't read Desktop or Downloads until it's granted Files & Folders access. `~/Movies` works without it.

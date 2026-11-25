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

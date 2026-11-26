# Adding a new style

A style is one self-contained page: `skills/video-basic/templates/<style>/index.html`. This guide walks through adding one, using [Ledger](../skills/video-basic/templates/ledger/index.html) as the worked example. Read [the style guide](../skills/video-basic/references/style.md) first; this page uses its names (`BEATS`, `BRAND`, `render(t)`, tokens).

This is for adding a look to the repo. To make one video look like a channel you like, use [Copy a style from a video you like](COPY-A-STYLE.md) instead.

## 1. Get a board first

A new look is design work. Before any code:

1. Ask `Arcee` for a board: a mock-up of the title, card, terminal, caption and outro beats in dark and light, with the colour tokens, fonts and motion notes written down.
2. rtorcato signs off on the board. Don't start the template until he has.

The board is the source of truth for tokens and motion. Step 6 compares your render against it.

## 2. Copy the closest template

Pick the existing style nearest to the board and copy its folder:

```sh
cp -r skills/video-basic/templates/ledger skills/video-basic/templates/<style>
```

Ledger is a good base for flat, typographic looks. `prompt` suits terminal-first looks, and `walkthrough` suits step-by-step how-tos with a phone. Use lowercase, one-word folder names.

Then change the identity of the copy, in the page itself:

- the header comment (name, what it's for, fonts, motion in one line);
- `const STYLE = "ledger"` to `"<style>"`. This single string sets the body class and the key read from `brand.json` `styles`, so it must match the folder name;
- the `<link>` to Google Fonts and the `document.fonts.load(...)` calls near the end of the BUILD section, so `render.py` waits for the right fonts.

## 3. Swap tokens and fonts, then check contrast

All colour lives in two CSS rules, one per theme. In Ledger:

```css
body.dark{--bg:#0F1115;--surf:#181B21;--ink:#F3F4F6;--muted:#A1A7B3;--rule:#2C313A;--acc:#7AA2FF;--accInk:#0F1115; ...}
body.light{--bg:#F3F4F6;--surf:#FFFFFF;--ink:#111827;--muted:#4B5563;--rule:#D1D5DB;--acc:#1D4ED8;--accInk:#FFFFFF; ...}
```

Replace the values with the board's, keeping the same variable names so the rest of the page keeps working. Set the font stacks in `body{--sans:...;--mono:...}`. Keep the rules from the style guide: no gradients, one accent, nothing that copies another creator's logo, character or footage.

Then re-check contrast **for both themes**. Don't trust the board's numbers or your eye. Compute the ratios:

```python
def lum(h):
    c = [int(h[i:i+2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= .03928 else ((x + .055) / 1.055) ** 2.4 for x in c]
    return .2126 * c[0] + .7152 * c[1] + .0722 * c[2]

def ratio(a, b):
    hi, lo = sorted((lum(a), lum(b)), reverse=True)
    return (hi + .05) / (lo + .05)

print(round(ratio("#1D4ED8", "#F3F4F6"), 2))   # Ledger light accent on page background
```

Targets:

| What | Needs |
|---|---|
| Text against its background (`--ink`, `--muted`, `--acc` used as text, `--accInk` on `--acc`, terminal text on `--term`) | **4.5:1** (WCAG AA) |
| Large or bold text only (the style guide marks any token that relies on this) | 3:1 |
| Non-text: rules, chips' borders, the accent bar, tap rings | **3:1** |

Light accents are the usual failure: a colour that looks fine on dark often drops under 4.5:1 on white. If one token only passes as large text, say so in the style guide's notes, as Prompt does.

## 4. Adapt the beat builders

Content is data. The `BEATS` block at the top of the page holds the beats, and the `B` object builds one section per type (`title`, `card`, `terminal`, `caption`, `outro`). Edit `B` when the board needs a different layout: change the markup and the `data-in` delays, and add CSS classes next to the others.

Keep the sample content the same as the sibling styles (the homelab-nut beats) so the looks compare like for like. A style that needs a new beat type, like Walkthrough's `step`, adds its own builder and its own sample.

Rules that keep the page renderable:

- `render(t)` stays a **pure function of `t`** in seconds. No CSS transitions, `setTimeout`, `requestAnimationFrame` or `Date.now()`. Follow Ledger's pattern: each element has a `data-in` delay and an `fx` (`slide`, `grow`, `wipe`, `show`, `type`), and `render` computes its state from `t`.
- Motion comes from the board. Ledger uses 40px slides and an ease-out and nothing else. If the new style springs or hard-cuts, change the math in `render`, not by adding CSS animation.
- Set **`window.DURATION`**. In the style templates it is the last beat's `end`, so it follows the content; keep that.
- Keep `window.render(0)` as the last line so the page shows something on load.
- Give hand-written element IDs distinctive names, and set `z-index` on overlays (see Pitfalls in the style guide).

## 5. Register the style

Registering makes the style findable and keeps `brand.json` working. Four places:

1. **`brand.json` support.** Keep `applyBrand(b, theme)` and its line that reads `b.styles[STYLE][theme]`. That is what lets a user write `{ "styles": { "<style>": { "dark": { "--acc": "#..." } } } }`. If you add tokens the brand should be able to set (for example `--acc2`), map them in `applyBrand`.
2. **The Styles table** in [`references/style.md`](../skills/video-basic/references/style.md#styles): one row with the use-it-for, look and motion columns, in the same voice as the others. Update the "how the style templates work" notes if the new style has its own contrast exceptions or its own sample beats.
3. **Pointers elsewhere.** The "Other looks" line in [`skills/video-basic/SKILL.md`](../skills/video-basic/SKILL.md), the Styles table in the [README](../README.md#styles) (and the number of styles in its intro sentence), and an entry under Unreleased in [`CHANGELOG.md`](../CHANGELOG.md).
4. **A README still** at `docs/styles/<style>.jpg`: a 1920×1080 frame of your own sample beats, from step 6. Never use a still of someone else's video.

## 6. Render and compare to the board

From a scratch folder outside the repo:

```sh
mkdir -p ~/Movies/<style>-test && cd ~/Movies/<style>-test
cp <repo>/skills/video-basic/templates/<style>/index.html .
cp <repo>/skills/video-basic/scripts/render.py .
```

Render a still from each beat in each theme. The theme comes from `?theme=` when you preview in a browser, but `render.py` loads the page without a query string, so for light set `THEME` in the page:

```sh
python3 render.py stills index.html 2.5 8.0 16.0 22.0 27.0      # dark (the default)
# set THEME = "light" at the top of index.html, then:
python3 render.py stills index.html 2.5 8.0 16.0 22.0 27.0
```

Use a time inside each beat (the sample's beats start at 0, 5, 12, 20 and 24, so pick times a second or two in, after the entrances finish). Stills are written to `stills/` as `still_<t>.jpg`, so move the dark set aside before the light run.

Compare each still with the board at full size, and look for:

- **Overflow:** long words in big type, the longest row in a card, the longest terminal line.
- **Contrast:** text you can't read at a glance, in both themes.
- **Spacing and grid:** elements on the board's grid, not close to it.
- **Fonts:** the intended family, not a fallback. If a heading looks wrong, the font didn't load before frame 0.
- **Motion:** render a short video (`python3 render.py video index.html test.mp4`) and watch one beat against the board's motion notes.

Fix, then re-render. Once the dark title still is right, copy it to `docs/styles/<style>.jpg` (scale or crop to 1920×1080 if needed, JPEG, under about 60 KB like the others).

## Checklist

- [ ] Board from `Arcee`, signed off by rtorcato
- [ ] `STYLE`, header comment and fonts renamed
- [ ] Dark and light tokens swapped; every text pair 4.5:1, non-text 3:1, computed
- [ ] `render(t)` pure; `window.DURATION` set; no gradients
- [ ] Style guide table, SKILL.md, README, CHANGELOG updated
- [ ] `docs/styles/<style>.jpg` added
- [ ] Dark and light stills compared with the board, no overflow

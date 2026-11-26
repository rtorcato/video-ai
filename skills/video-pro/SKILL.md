---
name: video-pro
description: Make an editable explainer or showcase video as a layered DaVinci Resolve timeline (FCPXML plus separate camera, graphics and caption clips, and Fusion title templates for editable text), in the talking-head + animated UI style. Use when the user wants to record their own voice and camera and re-cut the video in Resolve or Final Cut.
---

# video-pro: a layered, editable Resolve timeline

Instead of one flat MP4, this delivers a **Resolve-ready package**: a timeline file plus separate clips per layer, so the user can record their talking head, swap it in, and re-cut, retime or delete anything in DaVinci Resolve (the free version works) or Final Cut.

Read first:
- the **video-basic** skill's `references/style.md` for the visual style, tokens, animation helpers and research rules (if video-basic isn't installed, follow the same style: gradient backgrounds, white cards, terminals, checklists, caption pills);
- `references/resolve.md` in this skill for the FCPXML rules, alpha, and Fusion templates.

`templates/` is a complete working package source (a 75s portfolio showcase with ten beats). Start from it.

**Other looks:** video-basic ships four more styles (`ledger`, `prompt`, `walkthrough`, `gameshow`) as `templates/<style>/index.html`; see [Styles](../video-basic/references/style.md#styles). They're single-layer pages. To use one here, keep this skill's page and its `LAYER` logic, including the window hole and the camera transform. Take the style's theme tokens, fonts, components and motion into the `gfx` and `cap` layers. In pip beats, lay the style's cards out in the 840px column beside the window.

**Needs:** Python 3 with `pip install playwright` (then `playwright install chromium`, or use an installed Chrome), ffmpeg, and DaVinci Resolve on the editing machine.

The layout: one continuous camera take that cuts between **full frame**, a **tall rounded window on the left or right** with UI cards beside it, and **full-screen graphics** with the voice continuing underneath. Caption pills sit on top.

## 0. Where the package goes

Ask the user where to put it (or read `VIDEO_AI_OUTPUT` from the environment) and create `<output>/<project>-video/`. The FCPXML needs the absolute path the package will have on the editing machine, so settle this before generating it.

## 1. Research and script

- Research the project from its repo and docs (README, AGENTS.md, example configs, brand folder, mascot, DESIGN.md, `brand.json`).
- Write `source/beats.json`: `project`, `kind` (`explainer`, `showcase`…), `fps`, `width`, `height`, `window`, `beats`, `captions`. Each beat has `id, name, mode, bg, start, end, vo`. Modes:
  - `cam`: full-frame camera; captions only.
  - `pipL` / `pipR`: camera in the left or right rounded window, graphics on the other side.
  - `gfx`: full-screen graphics (camera hidden, voice continues).
- Mix the modes: open on pipL, alternate pip, gfx and cam, close on pipL. Beats of 4–12s. About 2.5 spoken words per second.
- `captions`: short pills (2–5 words) with `id, text, start, end, x, y` in global time. In pip beats, place them over the graphics column, not the window.
- Window geometry (1920×1080): left `x60 y60 w840 h960 r34`, right `x1020`. Camera scale `0.9`.

## 2. One page, four layers

`source/index.html` loads `beats.js` (written by `render.py` from `beats.json`). `window.LAYER` selects what's drawn and `render(t)` takes global seconds:

| LAYER | Draws | Encoded as |
|---|---|---|
| `cam` | A-roll placeholder: dark studio gradient, grey silhouette, "A-ROLL PLACEHOLDER", timecode, and a **"SAY THIS" box with the beat's line**. Keep labels inside x 520–1400 so they show through the window | H.264 + silent stereo AAC, full length |
| `gfx` | Background + scene cards. In pip beats the background has a **transparent rounded hole** at the window, plus a 4px white ring | PNG sequence for pip beats, H.264 for gfx beats |
| `cap` | Caption pills on a transparent page | PNG sequence per caption |
| `preview` | Everything composited, with the camera transformed as the timeline will (`translate(dx,dy) scale(0.9)`) | H.264 reference |

Cut the hole with an even-odd clip path on the background div (see `templates/index.html`, `holePath`). The window is static for the whole beat, so animate the cards, not the window. Each beat animates from `u = t - beat.start`. Beats are hard cuts; dissolves get added in Resolve.

## 3. Render

Copy `scripts/render.py` and `scripts/make_fcpxml.py` into `source/`.

1. `python3 render.py stills preview <t> …` at the busiest moment of every beat; tile them into a contact sheet and look at it at full size. Fix overflow, overlaps and contrast **before** the full render.
2. `python3 render.py all` renders every clip into `../media/` (camera, graphics, captions, preview). About 6–8 minutes for 75s; run it in the background and poll.

## 4. Timeline

`python3 make_fcpxml.py "<absolute package path on the editing machine>"` writes `<project>-<kind>.fcpxml` into the package (set `FCPXML_OUT` to write it elsewhere). Tracks: V1 camera cut per beat with window transforms, V2 graphics, V3 captions, a marker per beat with the line to say. Validate it with `xml.dom.minidom.parse`.

## 5. Verify

- Composite one pip frame with ffmpeg using the timeline's numbers (camera scaled to 1728×972, overlaid at (−384,54) for the left window or (576,54) for the right, then the graphics frame, then a caption frame). The camera must fill the rounded window with no gap.
- Sample 9 frames across `preview-flattened.mp4`.
- If computer use is available and the user agrees, import the timeline in their Resolve and check the viewer (not the thumbnails, which show alpha as black).

## 6. Package and deliver

```
<project>-video/
  <project>-<kind>.fcpxml
  README.md      # import steps, track table, swapping the A-roll, re-rendering
  SCRIPT.md      # time | beat | layout | line to say, recorded as one take
  media/camera/a-roll-placeholder.mp4
  media/graphics/b<n>-<slug>/ (PNG sequence) or b<n>-<slug>.mp4
  media/captions/c<n>/ (PNG sequence)
  media/preview/preview-flattened.mp4
  source/  index.html beats.json beats.js render.py make_fcpxml.py assets
  fusion/  *.setting (copy from this skill) + install-fusion-templates.sh
```

Tell the user: run `fusion/install-fusion-templates.sh` once and restart Resolve to get editable caption titles; import with File → Import → Timeline; swap the recording in with Replace Clip; File → Export Project gives a `.drp`.

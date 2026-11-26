---
name: video-basic
description: Make a short MP4 explainer or promo video for a software project in the "talking head + animated UI cards" YouTube style, from one HTML page rendered with headless Chrome and ffmpeg. Use for a quick, finished video; use video-pro for an editable DaVinci Resolve timeline.
---

# video-basic: one HTML page → one MP4

Turns a software project (a repo, README, docs site) into a 30–60s 1080p30 MP4: gradient backgrounds, white UI cards that spring in, terminals typing real commands, checklists that tick off, highlighter caption pills, and a rounded box for the presenter's talking head.

It costs nothing to render: no Remotion license, no paid AI video credits. The video is one self-contained `index.html` with a deterministic `render(t)`, filmed frame by frame by Playwright and piped into ffmpeg.

Read `references/style.md` before writing the page. It has the tokens, animation helpers, `render(t)` rules and pitfalls. `templates/index.html` is a complete working page to start from.

**Other looks:** if the user asks for a different style, or the content suits one better, start from one of `templates/<style>/index.html` instead: `ledger` (flat editorial, tutorials), `prompt` (terminal-first, CLI tools and changelogs) or `walkthrough` (step-by-step phone how-tos). Each has dark and light themes and reads `brand.json`. You fill in its `BEATS` block rather than writing scenes. See [Styles](references/style.md#styles).

**Needs:** Python 3 with `pip install playwright` (then `playwright install chromium`, or use an installed Chrome), and ffmpeg.

## 1. Research the project (accuracy over polish)

Never invent what the tool does when the source is reachable.

- Read the README, AGENTS.md or CLAUDE.md, example configs, and the CLI help or reference. Take real commands, output shapes and example data from them.
- Find brand assets (`brand/`, `DESIGN.md`, favicon, logo, mascot) and any `brand.json` (see the style guide). Use the project's own palette.
- If commands or package names don't exist yet, use plausible ones, keep them in variables at the top of the script, and say in the reply that they're placeholders.
- Check whether the project has been renamed. Use the name the user asked for and mention the other.

## 2. Script it as beats (one idea per scene)

A proven structure for teaching a dev tool to someone new:

1. **Hero** (optional, about 5s): dark brand field, wordmark, tagline, a `$ command` typing, logo or mascot animating in.
2. **Intro with talking head:** camera box on the left; on the right a title card ("New to X?") and three checklist rows that tick off.
3. **The problem / old way:** manual chores pop in and get crossed out, a red pill names the pain, then a yellow pill gives the new way.
4. **Step 1…N:** a `STEP n OF N` tag and a big title, then a terminal or code card with the real commands and output.
5. **Payoff visual:** a hub-and-spokes diagram (centre circle plus cards with progress bars and status pills), or a small simulation of the tool working.
6. **Outro with talking head:** camera box, logo card with URL, recap checklist, a call-to-action pill.

Give each section its own background and blur-dissolve between scenes. Keep caption pills to 2–5 words. Write the spoken line for each beat at about 2.5 words per second, so the user has a script to record.

## 3. Build the page

Work in one folder per video: `index.html`, a copy of `scripts/render.py`, and any assets next to them. Start from `templates/index.html` and replace its scenes. Set `window.DURATION` to the total length. With a style template, copy `templates/<style>/index.html`, edit `BEATS`, paste `brand.json` into `BRAND`, and set `THEME`. Its `DURATION` comes from the last beat's `end`.

## 4. Check, then render once

1. `python3 render.py stills index.html 4.0 12.5 20.0 …`, picking the busiest moment of each scene.
2. Tile the stills into one contact sheet (ffmpeg `xstack` or PIL) and look at it at full size.
3. Fix overlaps, clipping and low contrast. Then render once: `python3 render.py video index.html out.mp4`. A 45s video takes about a minute.
4. Sample a few frames from the MP4 (`select='eq(n\,N)+…',tile=3x3`) to confirm the transitions.

## 5. Deliver

- Hand over the MP4 plus `index.html` and `render.py` so the video can be edited and re-rendered.
- Say what's real (taken from the repo) and what's a placeholder.
- The video is silent. The talking-head recording supplies the audio once it's composited in. For a layered, editable timeline with the camera in its own track, use **video-pro**.

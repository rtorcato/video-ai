# Editing a video-basic video

A video-basic video is one finished MP4 made from one HTML page. **Editing it means regenerating it.** There is no timeline and no layers: an MP4 can't be opened back up into the scenes it came from.

The source of truth is `index.html`, which sits next to the MP4. Change the page, then render again.

## The loop

1. Change `index.html`, either by hand or by asking your agent to.
2. Check the result with stills: `python3 render.py stills index.html 4.0 12.5 20.0` (pick the busiest moment of each scene).
3. Render once: `python3 render.py video index.html out.mp4`. A 45-second video takes about a minute.

`render.py` is in the same folder as `index.html`. If you no longer have it, copy it from [`skills/video-basic/scripts/`](../skills/video-basic/scripts/render.py).

## Asking for a change

Be specific about **which beat** and **what should change**. The agent works from beats (one idea per scene), so name the scene the way you would on a script.

| Vague | Better |
|---|---|
| "The middle is boring" | "In the 'old way' beat, change the red pill to 'Five manual steps'" |
| "Make it faster" | "Cut the intro beat from 8s to 5s" |
| "Change the colours" | "Use `#22c55e` as the accent; keep the backgrounds" |

Give the new text word for word, or the new start and end times in seconds.

## What's cheap and what's a rebuild

| Cheap: edit the page and re-render | A rebuild: ask the agent to rework the page |
|---|---|
| Copy: titles, pill text, checklist rows, terminal commands | New beats or removing a beat |
| Colours, fonts, brand values | A new layout (for example a different card arrangement) |
| Timing of an existing scene | A new kind of scene (for example a diagram that doesn't exist yet) |
| Swapping a logo or mascot image | Changing the total length by a lot (scenes are timed against each other) |

Even a cheap change means a full re-render. There is no partial render in video-basic.

## Trimming or re-cutting the finished MP4 by hand

Any video editor can trim, cut or re-order the MP4. That works, but **those edits are lost the next time you render**, because the render starts again from `index.html`. If you want a change to stick, make it in the page. If you need a real timeline with the camera, graphics and captions on separate tracks, use [video-pro](EDITING-PRO.md) instead.

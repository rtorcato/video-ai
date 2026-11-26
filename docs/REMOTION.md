# Remotion export (optional)

The default path in video-ai uses no Remotion: Python, Playwright and ffmpeg render every video, and neither skill needs Node. This export is for teams that **already use Remotion** and want a finished video-basic or video-pro page inside a Remotion project, for example to drop it into a larger composition or to render it on their Remotion setup.

The export is a thin adapter, not a rewrite. Each page draws any moment with a deterministic `render(t)`. The generated composition hosts the page in an `<IFrame>` and calls `render(frame / fps)`. The animation stays in the HTML page, and the Remotion render matches the Playwright render frame for frame.

## License

Remotion is not free for every user. Read its license before you use the export:

- [Remotion license (LICENSE.md)](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md)
- [Remotion pricing](https://www.remotion.dev/pricing)

video-ai doesn't bundle or install Remotion. The exported project's `package.json` asks npm for it, so whoever runs `npm install` in the export takes on its license.

## When to use it

- Use it when your team already renders with Remotion and has the license it needs.
- Don't use it to make a single video. `render.py` in video-basic, or `render.py all` in video-pro, does that with no license.
- For new videos built in React from the start, use Remotion's own agent skills (below) instead.

## Export a page

You need Python 3 for the export, plus Node.js to open the result in Remotion.

```bash
# video-basic: the folder holding index.html (and its assets)
python3 scripts/export_remotion.py path/to/my-video path/to/my-video-remotion

# video-pro: the folder holding index.html and beats.json
python3 scripts/export_remotion.py path/to/my-pro-video path/to/my-pro-video-remotion --id my-pro-video
```

| Option | What it does |
|---|---|
| `--id NAME` | Composition ID (default: the page folder's name) |
| `--duration S` | Length in seconds. Default: the last beat's `end` in `beats.json`, otherwise `window.DURATION` in the page |
| `--layer L` | video-pro layer to show: `preview` (default), `cam`, `gfx` or `cap` |
| `--force` | Write into an output folder that isn't empty |

The export writes:

```
my-video-remotion/
  package.json          remotion, @remotion/cli, react, react-dom (pinned)
  remotion.config.ts    H.264, CRF 18, yuv420p, JPEG 92 frames, as render.py uses
  tsconfig.json
  src/index.ts          registerRoot
  src/Root.tsx          one <Composition>, 1920x1080 at 30 fps (or the size and fps in beats.json)
  src/HtmlPage.tsx      <IFrame> + render(frame / fps)
  public/page/          a copy of your page and its assets (video-pro: beats.js generated from beats.json)
```

Rendered media (`media/`, `stills/`, `*.mp4`) and the Python scripts are left out of the copy.

## Open it in Remotion Studio and render

```bash
cd path/to/my-video-remotion
npm install
npx remotion studio                                  # scrub and preview
npx remotion render my-video out/my-video.mp4        # the ID from --id or the folder name
```

To change the animation, edit `public/page/index.html` and Studio reloads it. Keep `render(t)` a pure function of time, as the skills' style guide requires. Remotion renders frames in parallel, in any order.

## How closely it matches

Checked on both starter templates (video-basic, 552 frames; video-pro, stills at 3s, 20s and 60s). The Remotion and Playwright renders have the same frame count, and every frame lines up at offset 0. The only pixel differences are text anti-aliasing at glyph edges, because Remotion films with its own headless Chrome build and `render.py` uses your installed Chrome. On the busiest frame the mean difference was under 2.5/255 per channel.

## Building in Remotion from scratch

Starting a new video directly in Remotion, rather than exporting one from these skills? Remotion maintains its own agent skills: [remotion-dev/skills](https://github.com/remotion-dev/skills) (`npx remotion skills add` inside a Remotion project, or `npx skills add remotion-dev/skills`). See also [Remotion's docs on agent skills](https://www.remotion.dev/docs/agents/skills).

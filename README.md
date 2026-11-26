# video-ai

Agent skills for making explainer and showcase videos for software projects: talking head + animated UI cards, the style of popular AI-tools YouTube channels. Built for Claude, works with any agent that reads `SKILL.md` skills.

![Preview: a window beat from the torcato.dev showcase](docs/preview.gif)

Everything renders from HTML with headless Chrome and ffmpeg. No Remotion license, no Adobe, no paid AI video credits.

## Skills

| Skill | What you get | Edit it in |
|---|---|---|
| [`video-basic`](skills/video-basic/SKILL.md) | One finished MP4 from a single HTML page | The HTML, then re-render |
| [`video-pro`](skills/video-pro/SKILL.md) | A layered **DaVinci Resolve** timeline (FCPXML): camera, graphics and caption tracks, a marker with the line to say on every beat, and Fusion title templates for editable text | DaVinci Resolve (free) or Final Cut |
| `video-hyperframes` *(coming)* | The same style built on [HyperFrames](https://github.com/heygen-com/hyperframes), with live preview and its block catalog | HyperFrames |

Already on Remotion? An optional script exports a finished page as a Remotion project; see [`docs/REMOTION.md`](docs/REMOTION.md). The skills themselves never need Remotion.

## Install

```bash
npx skills add rtorcato/video-ai
```

Or copy a folder from `skills/` into your agent's skills directory (for Claude Code: `~/.claude/skills/`). On claude.ai, zip a skill folder and upload it in the skills settings.

What the skills need on your machine:

- Python 3 and Playwright: `pip install playwright && playwright install chromium` (or let it use your installed Google Chrome)
- ffmpeg (`brew install ffmpeg`)
- For `video-pro`: [DaVinci Resolve](https://www.blackmagicdesign.com/products/davinciresolve) (the free version is enough)

## How it works

1. The agent reads your project (README, docs, brand folder) and writes a script as **beats**: one idea per scene, with the line you'll say.
2. It builds one HTML page whose `render(t)` draws any moment of the video as a pure function of time.
3. Playwright films the page frame by frame and pipes it into ffmpeg.
4. `video-pro` renders each layer separately (camera placeholder, graphics with a transparent window, captions) and writes an FCPXML timeline that DaVinci Resolve imports with every cut, position and scale in place.

Then you record yourself reading `SCRIPT.md`, swap your take in for the placeholder (Replace Clip), and edit like any other Resolve project.

## Styles

Pick a look per video. The default is the gradient-and-white-cards style in the preview above. Six more ship as `video-basic` templates in [`skills/video-basic/templates/<style>/`](skills/video-basic/templates/), each with dark and light themes and `brand.json` support. Ledger, Prompt and Orbit render the same sample beats; Market carries its own finance sample. Details are in [the style guide](skills/video-basic/references/style.md#styles).

| Style | Use it for | Still |
|---|---|---|
| **Ledger**: flat editorial | Tutorials, walkthroughs, explainers | ![Ledger](docs/styles/ledger.jpg) |
| **Prompt**: terminal-first | CLI tools, release notes, changelogs | ![Prompt](docs/styles/prompt.jpg) |
| **Walkthrough**: step-by-step how-to | Settings guides, setup videos, one action per step | ![Walkthrough](docs/styles/walkthrough.jpg) |
| **Gameshow**: quiz-show explainer | 30–60s quizzes and myth-busters, one question per feature | ![Gameshow](docs/styles/gameshow.jpg) |
| **Orbit**: space mission control | Launches, feature drops and explainers for a younger audience, one stage per step | ![Orbit](docs/styles/orbit.jpg) |
| **Market**: finance desk, three hosts | Market recaps, earnings breakdowns and money explainers, with live charts and a ticker on every beat | ![Market](docs/styles/market.jpg) |

## Editing your video

- **video-basic:** you edit the HTML and re-render; the MP4 can't be opened back up. See [Editing a video-basic video](docs/EDITING-BASIC.md).
- **video-pro:** you edit the timeline in DaVinci Resolve. See [Editing a video-pro video in Resolve](docs/EDITING-PRO.md).

## Copy a style you like

Want your video to look like a channel you admire? [Copy a style from a video you like](docs/COPY-A-STYLE.md) turns your notes into a `brand.json`, a style brief and a prompt, and says what you can and can't borrow.

## Your brand

The skills use your project's own brand when they find one (`brand/`, `DESIGN.md`, logo, mascot). To set it explicitly, add a `brand.json` (colours, fonts, logo, mascot); see [the style guide](skills/video-basic/references/style.md#brand).

## Examples

[`examples/`](examples/) has the sources of real videos made with these skills: a homelab-nut explainer (pro). The video-pro starter template is the [torcato.dev](https://torcato.dev) showcase.

## DaVinci Resolve gotchas

The ones that cost hours: Resolve ignores alpha in ffmpeg-made ProRes 4444 (so transparent layers ship as PNG sequences), it can't be handed a `.drp` from outside (import the FCPXML, then File → Export Project), and timeline thumbnails show alpha as black. More in [`resolve.md`](skills/video-pro/references/resolve.md).

## License

[MIT](LICENSE). The example mascots and brand images belong to their projects; use your own in your videos.

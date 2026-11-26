# Changelog

## Unreleased

### Added
- `video-basic` skill: one HTML page rendered to an MP4 with Playwright and ffmpeg, with a shared style guide and starter page.
- `video-pro` skill: layered DaVinci Resolve package (FCPXML timeline, camera/graphics/caption layers as PNG sequences, beat markers with the script) and the torcato.dev showcase as a starter.
- `Yellow Pill` Fusion title template with an installer for macOS, Linux and Windows.
- Examples: homelab-nut explainer (pro).
- Four visual styles for `video-basic`, as `templates/<style>/index.html`: Ledger (flat editorial), Prompt (terminal-first), Slab (bold kinetic type) and Walkthrough (step-by-step phone how-to). Each has dark and light themes, reads `brand.json` (including an exact per-style token block), and is documented in the style guide with README stills.
- `video-basic` `render.py` waits for web fonts before the first frame.
- `scripts/export_remotion.py`: optional export of a finished video-basic or video-pro page as a minimal Remotion project, documented in `docs/REMOTION.md`. The default render path still needs no Remotion.
- `docs/COPY-A-STYLE.md`: how to turn a video style you like into a worksheet, `brand.json`, style brief and prompt, and what you can and can't copy.
- `docs/ADD-A-STYLE.md`: how to add a new `video-basic` style (board, template copy, tokens and contrast, beat builders, registering, render and compare), using Ledger as the example.

# Changelog

## Unreleased

### Added
- `video-basic` skill: one HTML page rendered to an MP4 with Playwright and ffmpeg, with a shared style guide and starter page.
- `video-pro` skill: layered DaVinci Resolve package (FCPXML timeline, camera/graphics/caption layers as PNG sequences, beat markers with the script) and the torcato.dev showcase as a starter.
- `Yellow Pill` Fusion title template with an installer for macOS, Linux and Windows.
- Examples: homelab-nut explainer (pro).
- Three visual styles for `video-basic`, as `templates/<style>/index.html`: Ledger (flat editorial), Prompt (terminal-first) and Walkthrough (step-by-step phone how-to). Each has dark and light themes, reads `brand.json` (including an exact per-style token block), and is documented in the style guide with README stills.
- Gameshow style for `video-basic` (`templates/gameshow/index.html`): a quiz-show explainer with title, question number, question, countdown, reveal and score beats, dark and light themes, `brand.json` support, a style-guide row and a README still.
- Orbit style for `video-basic` (`templates/orbit/index.html`): space mission control for launches and feature drops, on the shared homelab-nut beats with a seeded starfield, a ringed planet and orbiting satellite, HUD labels and a mission-log terminal, dark and light themes, `brand.json` support, a style-guide row and a README still.
- Market style for `video-basic` (`templates/market/index.html`): a weeknight finance show with three camera windows, an intraday line chart, diverging sector bars, a 10-day candlestick chart and a stock ticker that scrolls through every beat without resetting. It has its own data-driven finance sample (chart paths are computed from the data), dark and light themes, `brand.json` support, a style-guide row and a README still.
- `video-basic` `render.py` waits for web fonts before the first frame.
- `scripts/export_remotion.py`: optional export of a finished video-basic or video-pro page as a minimal Remotion project, documented in `docs/REMOTION.md`. The default render path still needs no Remotion.
- `docs/COPY-A-STYLE.md`: how to turn a video style you like into a worksheet, `brand.json`, style brief and prompt, and what you can and can't copy.

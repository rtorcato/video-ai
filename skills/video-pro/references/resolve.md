# DaVinci Resolve notes (tested on Resolve 21, free version)

## Importing the timeline

- **File → Import → Timeline…**, pick the `.fcpxml`. Keep "Use sizing information" and "Automatically import source clips" on; 1920×1080, 30p.
- Resolve can't be handed a project file (`.drp`) from outside: it's a closed format, and Python scripting is Studio-only since Resolve 21. FCPXML import is the automation path. After the import, **File → Export Project…** gives a `.drp` to keep or share.
- Timeline thumbnails show alpha as black. Check transparency in the viewer, not the thumbnails.

## Alpha

- Resolve ignores the alpha channel in ffmpeg-made ProRes 4444 (`prores_ks`), whatever `alpha_bits` or clip Alpha Mode you set. QuickTime Animation and PNG-in-MOV don't import either.
- **PNG sequences work.** Write `name/name_0001.png …` and point the FCPXML asset at frame `_0001.png`; Resolve picks up the whole sequence.

## FCPXML 1.9 rules that matter

- 1080p30: `frameDuration="100/3000s"`; every time is `frames*100/3000s`.
- Assets: `<media-rep kind="original-media" src="file:///absolute/url-encoded/path"/>`. The paths must be where the package lives on the editing machine (spaces → `%20`). Re-run `make_fcpxml.py <package path>` after moving the package.
- Spine = the camera clip cut once per beat (`offset = start = beat start`), so its audio runs continuously.
- Window beats: `<adjust-transform position="X Y" scale="0.9 0.9"/>` before connected clips and markers. Position is in **percent of frame height**, origin at the centre, +Y up: X = (window centre x − 960) / 1080 × 100, which is ±44.4444 for windows at x 60 and x 1020.
- Resolve imports position, scale, rotation and opacity. Crops don't import reliably, which is why the window "hole" is cut in the graphics layer.
- Connected clips: `lane="1"` graphics, `lane="2"` captions. Their `offset` is in the **parent clip's own time**, which starts at the parent's `start`.
- One `<marker>` per beat: `value="b3 · The old way"`, `note="SAY: …"`.

## Swapping in the real recording

Media Pool → right-click `a-roll-placeholder` → **Replace Clip…**, pick the recording. Every V1 cut keeps its position and scale. Keep your face centred: at scale 0.9 the window shows source x ≈ 487–1433.

## Editable text: Fusion title templates

Rendered caption pills are pictures. For text you can retype in the Inspector, use a Fusion title template (`fusion/*.setting`, installed by `scripts/install-fusion-templates.sh`). Drag it from Effects → Titles → Fusion Titles onto V3 over the rendered pill and delete the pill, or use it for new captions.

`Yellow Pill.setting` publishes: Caption, Font, Style, Text Size, Text Color, Pill Color, Corner Round, Pill Padding X/Y, Position, Tilt. It springs in (scale 0 → 1.08 → 1 over 11 frames).

Writing a new template: a `MacroOperator` wrapping a `TextPlus`, a `Transform` and a `BezierSpline` for the pop. Verified Text+ inputs:

- Text: `StyledText`, `Font`, `Style`, `Size`, `Red1/Green1/Blue1`.
- Pill background (shading element 3): `Enabled3=1`, `ElementShape3=2` (border fill), `Level3=1`, `ExtendHorizontal3`, `ExtendVertical3`, `Round3`, `Red3/Green3/Blue3`, `Softness3=1`, `SoftnessX3/SoftnessY3=0`, `Offset3={0,0}`.
- To learn any other input name: select a node on the Fusion page, Cmd+C, and paste into a text editor.

Template folder (create it if missing):
- macOS: `~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Templates/Edit/Titles/`
- Windows: `%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Templates\Edit\Titles\`
- Linux: `~/.local/share/DaVinciResolve/Fusion/Templates/Edit/Titles/`

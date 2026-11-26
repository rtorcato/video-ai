# Editing a video-pro video in DaVinci Resolve

A video-pro video is a package: an FCPXML timeline plus separate clips for the camera, the graphics and the captions. You edit it in DaVinci Resolve (the free version works). It was tested on Resolve 21.

This guide covers the Resolve side. The technical details behind each step are in [`resolve.md`](../skills/video-pro/references/resolve.md).

## 1. Install the Fusion title templates (once)

The caption pills in the package are pictures. For captions you can retype, install the Fusion title template:

```bash
skills/video-pro/scripts/install-fusion-templates.sh
```

Inside a delivered package it's `fusion/install-fusion-templates.sh`. It copies `Yellow Pill.setting` into Resolve's Titles folder. **Restart Resolve afterwards.** The title then appears under Effects → Titles → Fusion Titles.

If you'd rather install it yourself, copy the file into:

- macOS: `~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Templates/Edit/Titles/`
- Windows: `%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Templates\Edit\Titles\`
- Linux: `~/.local/share/DaVinciResolve/Fusion/Templates/Edit/Titles/`

## 2. Set up the project

Create or open a project and set the timeline to **1920×1080 at 30 fps (30p) before you import**. The timeline in the package is 1080p30.

## 3. Import the timeline

1. File → Import → Timeline…
2. Choose the `.fcpxml` in the package folder.
3. Keep **Use sizing information** and **Automatically import source clips** ticked.

You get a timeline with the camera on V1, the graphics on V2 and the captions on V3. Each beat has a marker whose note starts with `SAY:` and holds the line to say.

## 4. Why there's no project file

Resolve can't be handed a `.drp` project from outside. It's a closed format, and Resolve's Python scripting needs the Studio version (since Resolve 21). Importing an FCPXML is the only automated way in. Once it's imported, **File → Export Project…** saves a `.drp` you can keep or share.

## 5. Where the media paths point

The FCPXML stores **absolute paths** to the media. If you move or copy the package to another folder or machine, the timeline will point at the old location. Either:

- re-run `python3 make_fcpxml.py "<new absolute path of the package>"` from the package's `source/` folder and import the new file, or
- relink the clips inside Resolve.

## 6. Swap in your recording

The camera track holds a placeholder clip that shows the line to say for each beat. In the Media Pool, right-click `a-roll-placeholder` → **Replace Clip…** and pick your recording. Every cut on V1 keeps its position and scale.

Keep your face centred. In the window beats the camera is scaled to 0.9, and the window shows roughly the middle of the source frame (source x ≈ 487–1433 of 1920).

## 7. Editing text

The rendered caption pills on V3 are images, so you can't retype them. To get editable text:

1. Drag **Yellow Pill** from Effects → Titles → Fusion Titles onto V3, over the rendered pill.
2. Delete the rendered pill.
3. Edit the text in the Inspector. You can also change the font, size, colours, padding, position and tilt there.

The template springs in on its own over 11 frames.

## 8. What stays manual

The package doesn't do these for you:

- **Dissolves.** Beats are hard cuts. Add transitions in Resolve.
- **Audio.** The camera clip carries your voice and nothing is mixed for you. Level, clean up and add music yourself.
- **Colour.** Nothing is graded.
- **Checking transparency.** Timeline thumbnails show alpha as black. Judge transparency in the viewer, not the thumbnails.

## 9. Changing something after the first import

Two different jobs:

**Re-rendering a layer.** Change `source/index.html` or `source/beats.json`, then run `python3 render.py all` from `source/`. There is no way to render a single layer from the command line: `all` redraws every clip (about 6–8 minutes for a 75-second video). Use `render.py stills <layer> <t>` to check a moment first.

**Getting the new media into Resolve.** If you re-run `make_fcpxml.py` and import the new timeline, Resolve gives you a new timeline. **It does not merge with the one you already edited.** So re-importing loses nothing, but it also doesn't carry your edits across. Your options:

- If only the media on disk changed (same file names, same cuts), Resolve reads the files again, so your existing timeline can pick up the new frames. Relink or refresh the clips if they show as offline. We haven't tested this.
- If the cuts changed (beat timings, new beats), you have to redo your edits on the new timeline by hand.

To limit the damage, finish the script and the cuts in `beats.json` **before** you start polishing in Resolve.

## Final Cut Pro

The FCPXML is version 1.9, which Final Cut can read in principle, but **this has not been tested**. The Fusion title template and the Replace Clip steps above are Resolve-specific.

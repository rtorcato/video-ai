"""Build the DaVinci Resolve / Final Cut timeline (FCPXML 1.9) from beats.json.

  python3 make_fcpxml.py [/absolute/path/to/package]   (defaults to the folder above this script)

Tracks (Resolve names them V1, V2, V3 on import):
  V1  A-roll: one camera clip, cut at every beat. Window beats carry position + scale so the
      camera lands inside the rounded window. Audio of this clip is your voice track.
  V2  Graphics: one clip per beat (PNG sequence with alpha for window beats, H.264 for full-screen).
  V3  Captions: caption pills, PNG sequences with alpha.
Markers on V1 carry each beat's name and the line to say.
"""
import json, os, sys
from pathlib import Path
from urllib.parse import quote
from xml.sax.saxutils import escape, quoteattr

HERE = Path(__file__).resolve().parent
CFG = json.loads((HERE / "beats.json").read_text())
ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parent
FPS = CFG["fps"]
KIND = CFG.get("kind", "explainer")  # used in the timeline and file names
H = CFG["height"]


def tm(seconds):
    """Seconds -> FCPXML rational time on the 30p frame grid."""
    frames = round(seconds * FPS)
    return f"{frames * 100}/{FPS * 100}s" if frames else "0s"


def url(rel):
    return "file://" + quote(str((ROOT / rel).as_posix()))


def slug(b):
    return f'{b["id"]}-' + "".join(ch if ch.isalnum() else "-" for ch in b["name"].lower()).strip("-").replace("--", "-")


total = CFG["beats"][-1]["end"]
assets, spine = [], []

assets.append(f'<asset id="cam" name="a-roll-placeholder" start="0s" duration="{tm(total)}" hasVideo="1" hasAudio="1" '
              f'format="r1" audioSources="1" audioChannels="2" audioRate="48000">'
              f'<media-rep kind="original-media" src={quoteattr(url("media/camera/a-roll-placeholder.mp4"))}/></asset>')

for b in CFG["beats"]:
    if b["mode"] != "cam":
        # Transparent layers are PNG sequences: Resolve ignores alpha in ffmpeg-made ProRes 4444,
        # but reads it from PNG frames. Pointing at frame 0001 makes Resolve pick up the whole sequence.
        rel = (f"media/graphics/{slug(b)}/{slug(b)}_0001.png" if b["mode"] in ("pipL", "pipR")
               else f"media/graphics/{slug(b)}.mp4")
        assets.append(f'<asset id="g_{b["id"]}" name="{slug(b)}" start="0s" duration="{tm(b["end"] - b["start"])}" '
                      f'hasVideo="1" format="r1"><media-rep kind="original-media" '
                      f'src={quoteattr(url(rel))}/></asset>')
for c in CFG["captions"]:
    assets.append(f'<asset id="{c["id"]}" name="caption-{c["id"]}" start="0s" duration="{tm(c["end"] - c["start"])}" '
                  f'hasVideo="1" format="r1"><media-rep kind="original-media" '
                  f'src={quoteattr(url("media/captions/" + c["id"] + "/" + c["id"] + "_0001.png"))}/></asset>')

for b in CFG["beats"]:
    s, e = b["start"], b["end"]
    inner = []
    if b["mode"] in ("pipL", "pipR"):
        w = CFG["window"]["left" if b["mode"] == "pipL" else "right"]
        k = CFG["window"]["cameraScale"]
        # FCPXML position is in percent of frame height, origin at centre, +y up.
        px = ((w["x"] + w["w"] / 2) - CFG["width"] / 2) / H * 100
        py = -((w["y"] + w["h"] / 2) - H / 2) / H * 100 + 0.0
        py = 0.0 if abs(py) < 1e-9 else py
        inner.append(f'<adjust-transform position="{px:.4f} {py:.4f}" scale="{k} {k}"/>')
    # connected clips: offset is in the parent clip's own time (its start = s)
    if b["mode"] != "cam":
        inner.append(f'<asset-clip ref="g_{b["id"]}" lane="1" offset="{tm(s)}" name="{slug(b)}" start="0s" '
                     f'duration="{tm(e - s)}" format="r1" tcFormat="NDF"/>')
    for c in CFG["captions"]:
        if s <= c["start"] < e:
            inner.append(f'<asset-clip ref="{c["id"]}" lane="2" offset="{tm(c["start"])}" name="caption: {escape(c["text"])}" '
                         f'start="0s" duration="{tm(c["end"] - c["start"])}" format="r1" tcFormat="NDF"/>')
    inner.append(f'<marker start="{tm(s)}" duration="{tm(1 / FPS)}" value={quoteattr(b["id"] + " · " + b["name"])} '
                 f'note={quoteattr("SAY: " + b["vo"])}/>')
    spine.append(f'<asset-clip ref="cam" offset="{tm(s)}" name="A-roll · {escape(b["name"])}" start="{tm(s)}" '
                 f'duration="{tm(e - s)}" format="r1" tcFormat="NDF" audioRole="dialogue">' + "".join(inner) + '</asset-clip>')

xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE fcpxml>
<fcpxml version="1.9">
  <resources>
    <format id="r1" name="FFVideoFormat1080p30" frameDuration="100/3000s" width="1920" height="1080" colorSpace="1-1-1 (Rec. 709)"/>
    {chr(10).join("    " + a for a in assets).strip()}
  </resources>
  <library>
    <event name="{CFG["project"]} {KIND}">
      <project name="{CFG["project"]} {KIND}">
        <sequence format="r1" duration="{tm(total)}" tcStart="0s" tcFormat="NDF" audioLayout="stereo" audioRate="48k">
          <spine>
            {chr(10).join("            " + c for c in spine).strip()}
          </spine>
        </sequence>
      </project>
    </event>
  </library>
</fcpxml>
'''
out = Path(os.environ.get("FCPXML_OUT", str(ROOT / f'{CFG["project"]}-{KIND}.fcpxml')))
out.write_text(xml)
print("wrote", out)

"""Render the layers of a layered video page (index.html + beats.json in this folder).

  python3 render.py stills <layer> <t> [<t> ...]   -> stills/<layer>_<t>.png
  python3 render.py all                            -> every clip the timeline needs, into ../media/

Layers: preview (everything composited), cam (A-roll placeholder), gfx (graphics), cap (caption pills).
Transparent layers are written as PNG sequences (Resolve ignores alpha in ffmpeg-made ProRes 4444).
"""
import json, os, subprocess, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
CFG = json.loads((HERE / "beats.json").read_text())
FPS = CFG["fps"]
MEDIA = HERE.parent / "media"


def slug(b):
    return f'{b["id"]}-' + "".join(ch if ch.isalnum() else "-" for ch in b["name"].lower()).strip("-").replace("--", "-")


def write_cfg():
    (HERE / "beats.js").write_text("window.CFG=" + json.dumps(CFG) + ";\n")


def render_mp4(pg, layer, start, end, out, audio=False):
    tmp = out[:-4] + ".part.mp4"
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "image2pipe", "-c:v", "mjpeg", "-framerate", str(FPS), "-i", "-"]
    if audio:
        cmd += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-shortest", "-c:a", "aac", "-b:a", "128k"]
    cmd += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", tmp]
    pg.evaluate(f"window.LAYER='{layer}'")
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = int(round((end - start) * FPS))
    for i in range(n):
        pg.evaluate(f"render({start + i / FPS:.6f})")
        ff.stdin.write(pg.screenshot(type="jpeg", quality=92))
    ff.stdin.close()
    if ff.wait() != 0:
        raise SystemExit("ffmpeg failed: " + out)
    os.replace(tmp, out)
    print("ok", out, n)


def render_pngseq(pg, layer, start, end, folder):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    pg.evaluate(f"window.LAYER='{layer}'")
    n = int(round((end - start) * FPS))
    for i in range(n):
        pg.evaluate(f"render({start + i / FPS:.6f})")
        pg.screenshot(path=str(folder / f"{folder.name}_{i + 1:04d}.png"), omit_background=True)
    print("ok", folder, n)


def main():
    write_cfg()
    mode = sys.argv[1]
    with sync_playwright() as p:
        chrome = os.environ.get("CHROME", "/usr/bin/google-chrome")
        opts = {"executable_path": chrome} if os.path.exists(chrome) else ({"channel": "chrome"} if sys.platform == "darwin" else {})
        b = p.chromium.launch(args=["--force-color-profile=srgb"], **opts)
        pg = b.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
        pg.goto((HERE / "index.html").as_uri())
        pg.wait_for_timeout(800)
        if mode == "stills":
            layer = sys.argv[2]
            (HERE / "stills").mkdir(exist_ok=True)
            pg.evaluate(f"window.LAYER='{layer}'")
            for t in sys.argv[3:]:
                pg.evaluate(f"render({t})")
                pg.screenshot(path=str(HERE / "stills" / f"{layer}_{t}.png"), omit_background=True)
        elif mode == "all":
            total = CFG["beats"][-1]["end"]
            for sub in ("camera", "graphics", "captions", "preview"):
                (MEDIA / sub).mkdir(parents=True, exist_ok=True)
            render_mp4(pg, "cam", 0, total, str(MEDIA / "camera" / "a-roll-placeholder.mp4"), audio=True)
            for bt in CFG["beats"]:
                if bt["mode"] == "cam":
                    continue
                if bt["mode"] in ("pipL", "pipR"):
                    render_pngseq(pg, "gfx", bt["start"], bt["end"], MEDIA / "graphics" / slug(bt))
                else:
                    render_mp4(pg, "gfx", bt["start"], bt["end"], str(MEDIA / "graphics" / (slug(bt) + ".mp4")))
            for c in CFG["captions"]:
                render_pngseq(pg, "cap", c["start"], c["end"], MEDIA / "captions" / c["id"])
            render_mp4(pg, "preview", 0, total, str(MEDIA / "preview" / "preview-flattened.mp4"))
        b.close()


if __name__ == "__main__":
    main()

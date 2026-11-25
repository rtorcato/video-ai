"""Film an HTML video page frame by frame with headless Chrome and encode it with ffmpeg.

  python3 render.py stills <page.html> <t> [<t> ...]        -> stills/still_<t>.jpg next to the page
  python3 render.py video  <page.html> <out.mp4> [seconds]  -> 1080p30 H.264 MP4

The page must expose a deterministic window.render(t) (t in seconds). The duration comes from the
command line, or from window.DURATION in the page.

Needs: pip install playwright && playwright install chromium   (or set CHROME=/path/to/chrome), ffmpeg.
"""
import os, subprocess, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

FPS = 30


def launch(p):
    chrome = os.environ.get("CHROME")
    if chrome:
        opts = {"executable_path": chrome}
    elif sys.platform == "darwin":
        opts = {"channel": "chrome"}  # uses the installed Google Chrome
    else:
        opts = {}
    return p.chromium.launch(args=["--force-color-profile=srgb"], **opts)


def main():
    if len(sys.argv) < 4 or sys.argv[1] not in ("stills", "video"):
        raise SystemExit(__doc__)
    mode, page_path = sys.argv[1], Path(sys.argv[2]).resolve()
    with sync_playwright() as p:
        b = launch(p)
        pg = b.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
        pg.goto(page_path.as_uri())
        pg.wait_for_timeout(600)
        if mode == "stills":
            out_dir = page_path.parent / "stills"
            out_dir.mkdir(exist_ok=True)
            for t in sys.argv[3:]:
                pg.evaluate(f"render({float(t)})")
                pg.screenshot(path=str(out_dir / f"still_{t}.jpg"), type="jpeg", quality=92)
            print("stills in", out_dir)
        else:
            out = Path(sys.argv[3]).resolve()
            dur = float(sys.argv[4]) if len(sys.argv) > 4 else pg.evaluate("window.DURATION")
            if not dur:
                raise SystemExit("Give the duration in seconds, or set window.DURATION in the page.")
            tmp = out.with_name(out.stem + ".part.mp4")
            ff = subprocess.Popen(
                ["ffmpeg", "-y", "-v", "error", "-f", "image2pipe", "-c:v", "mjpeg", "-framerate", str(FPS), "-i", "-",
                 "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
                 "-movflags", "+faststart", str(tmp)],
                stdin=subprocess.PIPE)
            n = int(round(dur * FPS))
            for i in range(n):
                pg.evaluate(f"render({i / FPS:.6f})")
                ff.stdin.write(pg.screenshot(type="jpeg", quality=92))
            ff.stdin.close()
            if ff.wait() != 0:
                raise SystemExit("ffmpeg failed")
            os.replace(tmp, out)
            print("ok", out, n, "frames")
        b.close()


if __name__ == "__main__":
    main()

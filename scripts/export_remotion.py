"""Export a finished video-basic or video-pro page as a minimal Remotion project (opt-in).

  python3 scripts/export_remotion.py <page-folder> <out-folder> [--duration S] [--layer L] [--force]

<page-folder> holds the page's index.html and its assets (video-pro: beats.json too). The export
copies the page into <out-folder>/public/page/ and writes a Remotion project whose single
<Composition> hosts the page in an <IFrame> and calls the page's own render(frame / fps).
The page is not rewritten, so the Remotion render matches the Playwright render frame for frame.

  --duration S  length in seconds (default: last beat's end in beats.json, else window.DURATION)
  --id NAME     composition id (default: the page folder's name)
  --layer L     video-pro layer to show: preview (default), cam, gfx or cap
  --force       write into <out-folder> even if it isn't empty

Then: cd <out-folder> && npm install && npx remotion studio
Remotion is free only for some users; read docs/REMOTION.md and Remotion's license first.
Needs only Python 3. Node files live only in <out-folder>; this repo has no package.json.
"""
import argparse, json, re, shutil, sys
from pathlib import Path

REMOTION_VERSION = "4.0.547"  # pinned: remotion and @remotion/cli must match exactly
LAYERS = ("preview", "cam", "gfx", "cap")
SKIP = {"media", "stills", "node_modules", "__pycache__", ".git", ".DS_Store", "render.py",
        "make_fcpxml.py", "install-fusion-templates.sh"}
SKIP_SUFFIXES = (".mp4", ".mov", ".fcpxml", ".part.mp4")
COMP_ID = re.compile(r"[^A-Za-z0-9-]+")


def fail(msg):
    raise SystemExit(f"export_remotion: {msg}")


def read_config(page_dir, duration):
    """Return (fps, width, height, seconds, cfg) from beats.json, the page, or the command line."""
    cfg = None
    beats = page_dir / "beats.json"
    if beats.is_file():
        try:
            cfg = json.loads(beats.read_text())
        except json.JSONDecodeError as e:
            fail(f"{beats} is not valid JSON: {e}")
    fps = int((cfg or {}).get("fps", 30))
    width = int((cfg or {}).get("width", 1920))
    height = int((cfg or {}).get("height", 1080))
    if duration is None and cfg and cfg.get("beats"):
        duration = float(cfg["beats"][-1]["end"])
    if duration is None:
        m = re.search(r"window\.DURATION\s*=\s*([0-9]*\.?[0-9]+)", (page_dir / "index.html").read_text())
        duration = float(m.group(1)) if m else None
    if not duration or duration <= 0:
        fail("no duration: pass --duration, set window.DURATION in the page, or add beats.json")
    return fps, width, height, duration, cfg


def copy_page(page_dir, dest):
    def ignore(_dir, names):
        return [n for n in names if n in SKIP or n.endswith(SKIP_SUFFIXES)]
    shutil.copytree(page_dir, dest, ignore=ignore, symlinks=False)


def ts(value):
    """A JSON literal is a valid TypeScript literal; this keeps every interpolated value quoted."""
    return json.dumps(value)


def write_project(out, name, comp_id, fps, width, height, frames, layer):
    files = {
        "package.json": json.dumps({
            "name": COMP_ID.sub("-", name).strip("-").lower() or "video",
            "private": True,
            "scripts": {"studio": "remotion studio", "render": "remotion render"},
            "dependencies": {
                "@remotion/cli": REMOTION_VERSION,
                "remotion": REMOTION_VERSION,
                "react": "19.2.0",
                "react-dom": "19.2.0",
            },
        }, indent=2) + "\n",
        "remotion.config.ts": (
            'import {Config} from "@remotion/cli/config";\n\n'
            "// Match scripts/render.py: sRGB colours, H.264 at CRF 18, yuv420p.\n"
            'Config.setVideoImageFormat("jpeg");\n'
            "Config.setJpegQuality(92);\n"
            'Config.setCodec("h264");\n'
            "Config.setCrf(18);\n"
            'Config.setPixelFormat("yuv420p");\n'
        ),
        "src/index.ts": 'import {registerRoot} from "remotion";\nimport {Root} from "./Root";\n\nregisterRoot(Root);\n',
        "src/Root.tsx": (
            'import {Composition} from "remotion";\nimport {HtmlPage} from "./HtmlPage";\n\n'
            "export const Root: React.FC = () => (\n"
            "  <Composition\n"
            f"    id={{{ts(comp_id)}}}\n"
            "    component={HtmlPage}\n"
            f"    durationInFrames={{{frames}}}\n"
            f"    fps={{{fps}}}\n"
            f"    width={{{width}}}\n"
            f"    height={{{height}}}\n"
            f"    defaultProps={{{{page: \"page/index.html\", layer: {ts(layer)}}}}}\n"
            "  />\n"
            ");\n"
        ),
        "src/HtmlPage.tsx": HTML_PAGE_TSX,
        "tsconfig.json": json.dumps({
            "compilerOptions": {
                "target": "ES2018", "module": "commonjs", "jsx": "react-jsx", "strict": True,
                "noEmit": True, "lib": ["dom", "es2018"], "esModuleInterop": True, "skipLibCheck": True,
            },
            "exclude": ["remotion.config.ts"],
        }, indent=2)+ "\n",
        ".gitignore": "node_modules/\nout/\n",
        "README.md": README_MD.format(name=name, comp_id=comp_id, seconds=frames / fps, fps=fps, width=width, height=height),
    }
    for rel, text in files.items():
        path = out / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)


HTML_PAGE_TSX = """import {useCallback, useLayoutEffect, useRef, useState} from "react";
import {AbsoluteFill, IFrame, continueRender, delayRender, staticFile, useCurrentFrame, useVideoConfig} from "remotion";

// The exported page draws any moment as a pure function of time: window.render(t), t in seconds.
type PageWindow = Window & {render?: (t: number) => void; LAYER?: string};

export const HtmlPage: React.FC<{page: string; layer: string | null}> = ({page, layer}) => {
  const frame = useCurrentFrame();
  const {fps, width, height} = useVideoConfig();
  const ref = useRef<HTMLIFrameElement>(null);
  // Hold every frame until the page has loaded, its fonts are ready and render(t) has run once.
  const [handle] = useState(() => delayRender(`Loading ${page}`));
  const [ready, setReady] = useState(false);
  const released = useRef(false);

  const onLoad = useCallback(() => {
    const doc = ref.current?.contentDocument;
    if (!doc) throw new Error(`${page} did not load in the iframe`);
    doc.fonts.ready.then(() => setReady(true));
  }, [page]);

  useLayoutEffect(() => {
    if (!ready) return;
    const win = ref.current?.contentWindow as PageWindow | null;
    if (!win || typeof win.render !== "function") {
      throw new Error(`${page} has no window.render(t)`);
    }
    if (layer) win.LAYER = layer;
    win.render(frame / fps);
    if (!released.current) {
      released.current = true;
      continueRender(handle);
    }
  }, [ready, frame, fps, layer, page, handle]);

  return (
    <AbsoluteFill>
      <IFrame ref={ref} src={staticFile(page)} onLoad={onLoad} style={{width, height, border: 0}} />
    </AbsoluteFill>
  );
};
"""

README_MD = """# {comp_id} (Remotion export)

Generated by `scripts/export_remotion.py` from video-ai (page folder `{name}`). {width}x{height}, {fps} fps, {seconds:.2f}s.
`public/page/` is the original HTML page; `src/HtmlPage.tsx` calls its `render(frame / fps)`.

Remotion is not free for every user. Read its license before you use this export:
https://github.com/remotion-dev/remotion/blob/main/LICENSE.md

```bash
npm install
npx remotion studio            # preview and scrub
npx remotion render {comp_id} out/{comp_id}.mp4
```

Edit the animation in `public/page/index.html`, not in React.
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("page_dir", type=Path)
    ap.add_argument("out_dir", type=Path)
    ap.add_argument("--duration", type=float)
    ap.add_argument("--layer", choices=LAYERS)
    ap.add_argument("--id", help="composition id (default: the page folder's name)")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    page_dir, out = a.page_dir.resolve(), a.out_dir.resolve()
    if not (page_dir / "index.html").is_file():
        fail(f"{page_dir} has no index.html")
    if out == page_dir or page_dir in out.parents:
        fail("write the export outside the page folder")
    if out.exists() and any(out.iterdir()) and not a.force:
        fail(f"{out} is not empty (use --force to write into it)")

    fps, width, height, seconds, cfg = read_config(page_dir, a.duration)
    frames = int(round(seconds * fps))
    layer = a.layer or ("preview" if cfg else None)

    page_dest = out / "public" / "page"
    if page_dest.exists():
        shutil.rmtree(page_dest)
    copy_page(page_dir, page_dest)
    if cfg is not None:  # video-pro pages read their beats from beats.js, as render.py writes it
        (page_dest / "beats.js").write_text("window.CFG=" + json.dumps(cfg) + ";\n")

    comp_id = COMP_ID.sub("-", a.id or page_dir.name).strip("-") or "Video"
    write_project(out, page_dir.name, comp_id, fps, width, height, frames, layer)
    print(f"ok {out} ({frames} frames at {fps} fps)")
    print(f"next: cd {out} && npm install && npx remotion studio")


if __name__ == "__main__":
    main()

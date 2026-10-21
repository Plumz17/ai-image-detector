"""Run YOUR images through the original backend pipeline and the slim server, and compare with the true labels.

    python compare_folder.py IMAGES_DIR --slim-url https://<hosted address> [--csv out.csv]

IMAGES_DIR must contain two subfolders, `ai/` (AI-generated images) and `real/` (genuine photos).
Run it with the backend's pinned packages installed (backend/requirements.txt, Python 3.12), because the original
pipeline is imported from ../backend. The slim server is called over HTTP, so it can be the hosted one or a local
container; the hosted one allows 10 requests a minute, so the script waits between calls unless --no-throttle.
The model shuffles tiles at random, so a borderline image can change label between runs: use --repeats to see it.
"""
import argparse, csv, io, pathlib, sys, time, urllib.error, urllib.request, uuid
sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from PIL import Image
from app import config, pipeline  # the original backend code, unchanged

EXT = {".jpg", ".jpeg", ".png"}


def slim_predict(url, data, name):
    boundary = uuid.uuid4().hex
    body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{name}\"\r\n"
            f"Content-Type: application/octet-stream\r\n\r\n").encode() + data + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(url.rstrip("/") + "/predict", data=body,
                                 headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    try:
        import json
        return json.load(urllib.request.urlopen(req, timeout=120))
    except urllib.error.HTTPError as e:
        import json
        return json.loads(e.read() or b"{}") | {"http": e.code}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("images"); ap.add_argument("--slim-url", required=True)
    ap.add_argument("--repeats", type=int, default=1); ap.add_argument("--no-throttle", action="store_true")
    ap.add_argument("--csv")
    a = ap.parse_args()
    det = pipeline.Detector(config.FEATURE_EXTRACTOR_PATH, config.SVM_PATH)
    rows = []
    for truth, want in (("ai", "fake"), ("real", "real")):
        for f in sorted((pathlib.Path(a.images) / truth).iterdir()):
            if f.suffix.lower() not in EXT: continue
            data = f.read_bytes(); w, h = Image.open(io.BytesIO(data)).size
            for _ in range(a.repeats):
                try: o = det.analyze(data)["label"]
                except pipeline.PipelineError as e: o = f"rejected: {e.message}"
                s = slim_predict(a.slim_url, data, f.name)
                s = s.get("label") or f"error {s.get('http', '')}: {s.get('message', '')}"
                if not a.no_throttle: time.sleep(6.5)
                rows.append((f.name, round(len(data) / 1e6, 2), f"{w}x{h}", want, o, s))
                print(f"{f.name[:34]:34s} {len(data)/1e6:6.2f} MB {w:>5}x{h:<5} true={want:4s} original={o:10s} slim={s}", flush=True)
    def acc(i): ok = [r for r in rows if r[i] in ("real", "fake")]; return sum(r[i] == r[3] for r in ok), len(ok)
    n = len(rows); print(f"\nimages x repeats: {n}")
    for name, i in (("original", 4), ("slim", 5)): c, t = acc(i); print(f"{name:9s} correct: {c}/{t}")
    print(f"original and slim agree: {sum(r[4] == r[5] for r in rows)}/{n}")
    for truth in ("fake", "real"):
        for i, name in ((4, "original"), (5, "slim")):
            sub = [r for r in rows if r[3] == truth and r[i] in ("real", "fake")]
            print(f"  true {truth}: {name} says fake in {sum(r[i]=='fake' for r in sub)}/{len(sub)}")
    if a.csv:
        with open(a.csv, "w", newline="") as fh:
            w = csv.writer(fh); w.writerow(["file", "MB", "size", "true", "original", "slim"]); w.writerows(rows)

main()

# Does JPEG compression (WhatsApp, downloads, camera files) change the ORIGINAL model's answers?
import glob, io, os, sys
sys.dont_write_bytecode = True
import pathlib
REPO = os.environ.get("REPO") or str(pathlib.Path(__file__).resolve().parents[1]); sys.path.insert(0, os.path.join(REPO, "backend"))
from PIL import Image
from app import config, pipeline
det = pipeline.Detector(config.FEATURE_EXTRACTOR_PATH, config.SVM_PATH)
S = os.path.join(REPO, "backend", "tests", "sample_images")
ai = [Image.open(f).convert("RGB") for f in sorted(glob.glob(S + "/ai*.png"))]
real = [Image.open(f).convert("RGB") for f in sorted(glob.glob(S + "/no_ai*.png"))]
def label(img, q, runs=3):
    b = io.BytesIO()
    if q: img.save(b, "JPEG", quality=q)
    else: img.save(b, "PNG")
    d = b.getvalue(); v = [det.classify(d)["label"] for _ in range(runs)]
    return "fake" if v.count("fake") * 2 > runs else "real"
print("quality      AI called fake    REAL called fake   (correct: AI high, REAL low)")
for q in (0, 95, 85, 70, 50):
    a = sum(label(i, q) == "fake" for i in ai); r = sum(label(i, q) == "fake" for i in real)
    print(f"{'PNG (none)' if q == 0 else 'JPEG q=' + str(q):12s} {a:2d}/20            {r:2d}/20")

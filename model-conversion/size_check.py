# Does the ORIGINAL model react to image size? Uses the backend's own Detector, unchanged.
import glob, io, os, sys
sys.dont_write_bytecode = True
import pathlib
REPO = os.environ.get("REPO") or str(pathlib.Path(__file__).resolve().parents[1]); sys.path.insert(0, os.path.join(REPO, "backend"))
from PIL import Image
from app import config, pipeline
det = pipeline.Detector(config.FEATURE_EXTRACTOR_PATH, config.SVM_PATH)
def label(img, runs=3):
    b = io.BytesIO(); img.save(b, "PNG"); d = b.getvalue()
    votes = [det.classify(d)["label"] for _ in range(runs)]
    return "fake" if votes.count("fake") * 2 > runs else "real"
S = os.path.join(REPO, "backend", "tests", "sample_images")
ai = [Image.open(f).convert("RGB") for f in sorted(glob.glob(S + "/ai*.png"))]
real = [Image.open(f).convert("RGB") for f in sorted(glob.glob(S + "/no_ai*.png"))]
def rate(imgs): l = [label(i) for i in imgs]; return f"{l.count('fake')}/{len(l)} labelled fake"
print("AI   512 (as given)          :", rate(ai))
print("AI   shrunk to 256 first     :", rate([i.resize((256, 256), Image.BICUBIC) for i in ai]))
print("REAL 256 (as given)          :", rate(real))
print("REAL enlarged to 512 first   :", rate([i.resize((512, 512), Image.BICUBIC) for i in real]))
print("REAL enlarged to 1024 first  :", rate([i.resize((1024, 1024), Image.BICUBIC) for i in real]))

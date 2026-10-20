# 100 runs of the ORIGINAL pipeline on the two borderline images; prints fraction labelled fake. Run in ref-env.
import pathlib
import io, os, sys
sys.dont_write_bytecode = True
import torch
REPO = str(pathlib.Path(__file__).resolve().parents[1] / "backend")
sys.path.insert(0, REPO)
from app.patchcraft_original import ModelInference, preprocess
m = ModelInference(os.path.join(REPO, "weights", "headless_model.pth"), os.path.join(REPO, "weights", "svm.pkl")); m.feature_extractor.eval()
for name in ("no_ai (20).png", "no_ai (7).png"):
    data = open(os.path.join(REPO, "tests", "sample_images", name), "rb").read()
    fake = 0
    for _ in range(100):
        crop = m.multiple_crop(io.BytesIO(data))[0]
        frt, fpt = preprocess(crop)
        with torch.no_grad(): f = m.feature_extractor(frt.unsqueeze(0), fpt.unsqueeze(0)).numpy()
        fake += int(m.best_clf.predict(f)[0])
    print(f"original {name}: fake in {fake}/100 runs")

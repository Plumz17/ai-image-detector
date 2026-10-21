# Spike step 2: record what the ORIGINAL pipeline does on the 40 sample images (read-only on the repo).
# Run in ref-env. Big files (tensors) go to SPIKE_DATA; a small summary JSON stays here.
import pathlib
import glob, io, json, os, sys, time
sys.dont_write_bytecode = True
import numpy as np
import torch

REPO = str(pathlib.Path(__file__).resolve().parents[1] / "backend")
DATA = os.environ["SPIKE_DATA"]
REPEATS = 5
sys.path.insert(0, REPO)
from app.patchcraft_original import ModelInference, preprocess  # unchanged original code

m = ModelInference(os.path.join(REPO, "weights", "headless_model.pth"), os.path.join(REPO, "weights", "svm.pkl"))
m.feature_extractor.eval()  # same as backend/app/pipeline.py Detector

os.makedirs(os.path.join(DATA, "golden"), exist_ok=True)
files = sorted(glob.glob(os.path.join(REPO, "tests", "sample_images", "*.png")))
rows = []
for f in files:
    name = os.path.basename(f)
    expected = "real" if name.startswith("no_ai") else "fake"
    crops = m.multiple_crop(io.BytesIO(open(f, "rb").read()))
    runs = []
    for rep in range(REPEATS):  # preprocessing is random (shuffle/duplicate), so repeat
        votes, feats = [], []
        for k, crop in enumerate(crops):
            frt, fpt = preprocess(crop)
            with torch.no_grad():
                feat = m.feature_extractor(frt.unsqueeze(0), fpt.unsqueeze(0)).numpy()
            votes.append(int(m.best_clf.predict(feat)[0]))
            feats.append(feat[0])
            if rep == 0:  # save inputs/outputs of the first run as the golden fixtures
                np.savez_compressed(os.path.join(DATA, "golden", f"{name[:-4]}_c{k}.npz"),
                                    frt=frt.numpy(), fpt=fpt.numpy(), feature=feat[0].astype(np.float32),
                                    svm_pred=votes[-1])
        ratio = sum(votes) / len(votes)
        runs.append({"votes": votes, "fake_ratio": ratio,
                     "label": "fake" if ratio > 0.5 else "real" if ratio < 0.5 else "tie"})
    labels = [r["label"] for r in runs]
    rows.append({"image": name, "expected": expected, "crops": len(crops), "labels": labels,
                 "stable": len(set(labels)) == 1, "match_expected": labels.count(expected)})
    print(name, expected, labels, flush=True)

summary = {"repeats": REPEATS, "images": rows,
           "unstable_images": [r["image"] for r in rows if not r["stable"]],
           "total_runs": len(rows) * REPEATS,
           "runs_matching_expected": sum(r["match_expected"] for r in rows)}
json.dump(summary, open(os.path.join(os.path.dirname(__file__), "golden_summary.json"), "w"), indent=1)
print("unstable:", summary["unstable_images"], "| matching expected:", summary["runs_matching_expected"], "/", summary["total_runs"])

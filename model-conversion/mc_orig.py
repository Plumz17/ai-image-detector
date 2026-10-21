# The backend's own Detector (original model code + backend glue) on the multi-crop cases. Run in ref-env.
import pathlib
import json, os, sys, time
sys.dont_write_bytecode = True
REPO = str(pathlib.Path(__file__).resolve().parents[1] / "backend")
sys.path.insert(0, REPO); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app import config, pipeline
import multicrop_cases
det = pipeline.Detector(config.FEATURE_EXTRACTOR_PATH, config.SVM_PATH)
res = {}
for name, data in multicrop_cases.build(os.path.join(REPO, "tests", "sample_images")).items():
    runs = []; t = time.perf_counter()
    for _ in range(20):
        r = det.classify(data); runs.append((r["label"], r["crops_analyzed"], r["fake_crop_ratio"]))
    res[name] = runs
    print(f"orig {name:30s} fake {sum(r[0]=='fake' for r in runs):2d}/20  crops {runs[0][1]}  ratios {sorted({r[2] for r in runs})}  {(time.perf_counter()-t)/20:.2f}s/img", flush=True)
json.dump(res, open(os.path.join(os.environ["SPIKE_DATA"], "mc_orig.json"), "w"))

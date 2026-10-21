# End-to-end: NumPy port + cnn.tflite + NumPy SVM on the 40 samples x 5 runs. Runs in the Linux container with
# ONLY numpy, pillow and ai-edge-litert installed (no torch, cv2, scikit-learn).
import glob, json, os, resource, statistics, sys, time
sys.dont_write_bytecode = True
sys.path.insert(0, "/repo/slim-server/app")
import numpy as np
from ai_edge_litert.interpreter import Interpreter
import np_pipeline as npp

params = dict(np.load("/data/params.npz"))
it = Interpreter(model_path="/data/cnn.tflite"); it.allocate_tensors()
ins, out = it.get_input_details(), it.get_output_details()[0]
def cnn(frt, fpt):
    it.set_tensor(ins[0]["index"], frt); it.set_tensor(ins[1]["index"], fpt); it.invoke()
    return it.get_tensor(out["index"])

ref = {r["image"]: r for r in json.load(open("/spike/golden_summary.json"))["images"]}
rows, times, same_as_orig = [], [], 0
for f in sorted(glob.glob("/repo/backend/tests/sample_images/*.png")):
    name = os.path.basename(f); data = open(f, "rb").read()
    labels = []
    for seed in range(5):
        t = time.perf_counter(); r = npp.classify(data, params, cnn, seed=seed); times.append(time.perf_counter() - t)
        labels.append(r["label"])
    exp = "real" if name.startswith("no_ai") else "fake"
    rows.append((name, exp, labels))
    same_as_orig += sum(a == b for a, b in zip(sorted(labels), sorted(ref[name]["labels"])))
    print(name, exp, labels, "| original:", ref[name]["labels"], flush=True)

match = sum(l.count(e) for _, e, l in rows)
print(f"\nport matches filename label: {match}/{len(rows)*5}  (original: 194/200)")
print("unstable in port:", [n for n, _, l in rows if len(set(l)) > 1], "| unstable in original:", [n for n, r in ref.items() if not r["stable"]])
print("always-wrong in port:", [n for n, e, l in rows if l.count(e) == 0], "| in original:", [n for n, r in ref.items() if r["match_expected"] == 0])
print(f"time per image: median {statistics.median(times)*1000:.0f} ms, max {max(times)*1000:.0f} ms")
print(f"peak memory: {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024:.0f} MB")

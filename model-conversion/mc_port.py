# The port on the same cases (container: numpy + pillow + ai-edge-litert only).
import sys, time
sys.dont_write_bytecode = True; sys.path.insert(0, "/repo/slim-server/app"); sys.path.insert(0, "/spike")
import numpy as np
from ai_edge_litert.interpreter import Interpreter
import np_pipeline as npp, multicrop_cases
params = dict(np.load("/data/params.npz"))
it = Interpreter(model_path="/data/cnn.tflite"); it.allocate_tensors(); ins, out = it.get_input_details(), it.get_output_details()[0]
def cnn(a, b):
    it.set_tensor(ins[0]["index"], a); it.set_tensor(ins[1]["index"], b); it.invoke(); return it.get_tensor(out["index"])
for name, data in multicrop_cases.build("/repo/backend/tests/sample_images").items():
    runs = []; t = time.perf_counter()
    for i in range(20):
        r = npp.classify(data, params, cnn, seed=i); runs.append((r["label"], r["crops_analyzed"], r["fake_crop_ratio"]))
    print(f"port {name:30s} fake {sum(r[0]=='fake' for r in runs):2d}/20  crops {runs[0][1]}  ratios {sorted({r[2] for r in runs})}  {(time.perf_counter()-t)/20:.2f}s/img", flush=True)

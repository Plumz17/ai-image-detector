import resource, sys, time
sys.dont_write_bytecode = True; sys.path.insert(0, "/repo/slim-server/app")
import numpy as np
t0 = time.perf_counter()
from ai_edge_litert.interpreter import Interpreter
import np_pipeline as npp
params = dict(np.load("/data/params.npz"))
it = Interpreter(model_path="/data/cnn.tflite"); it.allocate_tensors(); ins, out = it.get_input_details(), it.get_output_details()[0]
def cnn(a, b):
    it.set_tensor(ins[0]["index"], a); it.set_tensor(ins[1]["index"], b); it.invoke(); return it.get_tensor(out["index"])
print(f"startup {time.perf_counter()-t0:.1f}s", flush=True)
for n in ("ai (1).png", "no_ai (1).png", "ai (10).png"):
    t = time.perf_counter(); r = npp.classify(open(f"/repo/backend/tests/sample_images/{n}", "rb").read(), params, cnn, seed=1)
    print(f"{n}: {r['label']} in {time.perf_counter()-t:.2f}s", flush=True)
print(f"peak memory {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024:.0f} MB")

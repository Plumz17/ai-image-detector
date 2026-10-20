# 100 runs of the PORT (container) on the same two images.
import os, sys
sys.dont_write_bytecode = True; sys.path.insert(0, "/repo/slim-server/app")
import numpy as np
from ai_edge_litert.interpreter import Interpreter
import np_pipeline as npp
params = dict(np.load("/data/params.npz"))
it = Interpreter(model_path="/data/cnn.tflite"); it.allocate_tensors(); ins, out = it.get_input_details(), it.get_output_details()[0]
def cnn(a, b):
    it.set_tensor(ins[0]["index"], a); it.set_tensor(ins[1]["index"], b); it.invoke(); return it.get_tensor(out["index"])
for name in ("no_ai (20).png", "no_ai (7).png"):
    data = open(f"/repo/backend/tests/sample_images/{name}", "rb").read()
    fake = sum(npp.classify(data, params, cnn, seed=1000 + i)["label"] == "fake" for i in range(100))
    print(f"port     {name}: fake in {fake}/100 runs")

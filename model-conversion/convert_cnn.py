# Spike step 4: convert the CNN (HeadlessPatchCraft) to .tflite and compare with the golden outputs.
# Runs inside the Linux container (litert-torch has no Windows build). The original model code is imported unchanged.
import glob, os, sys, time, types
sys.dont_write_bytecode = True
import numpy as np
import torch

# The original module imports cv2 / torchvision at the top, but only uses them in preprocessing,
# which this script does not call. Stub them so the unchanged original file can be imported.
for name in ("cv2", "torchvision", "torchvision.transforms"):
    sys.modules[name] = types.ModuleType(name)
sys.modules["torchvision.transforms"].transforms = types.SimpleNamespace(Compose=None, Normalize=None)
sys.modules["torchvision"].transforms = sys.modules["torchvision.transforms"]

sys.path.insert(0, "/repo/backend")
from app.patchcraft_original import HeadlessPatchCraft, PatchCraft

DATA = "/data"
model = HeadlessPatchCraft(PatchCraft())
model.load_state_dict(torch.load("/repo/backend/weights/headless_model.pth", map_location="cpu", weights_only=True))
model.eval()

golden = sorted(glob.glob(f"{DATA}/golden/*.npz"))
first = np.load(golden[0])
sample = (torch.from_numpy(first["frt"]).unsqueeze(0), torch.from_numpy(first["fpt"]).unsqueeze(0))
print("input shapes", [tuple(t.shape) for t in sample])

import litert_torch
edge = litert_torch.convert(model, sample)
out = f"{DATA}/cnn.tflite"
edge.export(out)
print("tflite size KB:", os.path.getsize(out) // 1024)

# 1) in-memory converted model vs golden (golden was made by torch 2.11 in the reference env)
# 2) exported file run by the standalone LiteRT interpreter vs golden
from ai_edge_litert.interpreter import Interpreter
interp = Interpreter(model_path=out)
interp.allocate_tensors()
ins, outs = interp.get_input_details(), interp.get_output_details()
print("interpreter inputs:", [(d["name"], d["shape"].tolist()) for d in ins], "output:", outs[0]["shape"].tolist())

d_mem, d_file, d_swap, d_torch, times = [], [], [], [], []
for f in golden:
    g = np.load(f)
    frt, fpt, want = g["frt"][None].astype(np.float32), g["fpt"][None].astype(np.float32), g["feature"]
    got = np.asarray(edge(torch.from_numpy(frt), torch.from_numpy(fpt))).reshape(-1)
    d_mem.append(np.abs(got - want).max())
    with torch.no_grad():
        d_torch.append(np.abs(model(torch.from_numpy(frt), torch.from_numpy(fpt)).numpy().reshape(-1) - want).max())
    def run(a, b):
        interp.set_tensor(ins[0]["index"], a); interp.set_tensor(ins[1]["index"], b); interp.invoke()
        return interp.get_tensor(outs[0]["index"]).reshape(-1)
    t = time.perf_counter(); y = run(frt, fpt); times.append(time.perf_counter() - t)
    d_file.append(np.abs(y - want).max())
    d_swap.append(np.abs(run(fpt, frt) - want).max())

def s(name, v): print(f"{name:42s} max {max(v):.2e}  mean {np.mean(v):.2e}")
print(f"images/crops compared: {len(golden)}")
s("torch 2.14 (container) vs golden", d_torch)
s("converted (in memory) vs golden", d_mem)
s("exported .tflite via Interpreter vs golden", d_file)
s("(control) .tflite with inputs swapped", d_swap)
print(f"interpreter time per crop: median {np.median(times)*1000:.0f} ms")

# Run the exported .tflite on every golden crop and save its 32 outputs (runs in the Linux container).
import glob, numpy as np
from ai_edge_litert.interpreter import Interpreter
it = Interpreter(model_path="/data/cnn.tflite"); it.allocate_tensors()
i, o = it.get_input_details(), it.get_output_details()[0]
names, feats = [], []
for f in sorted(glob.glob("/data/golden/*.npz")):
    g = np.load(f)
    it.set_tensor(i[0]["index"], g["frt"][None].astype(np.float32))
    it.set_tensor(i[1]["index"], g["fpt"][None].astype(np.float32))
    it.invoke(); feats.append(it.get_tensor(o["index"]).reshape(-1)); names.append(f.split("/")[-1])
np.savez("/data/tflite_features.npz", names=np.array(names), feats=np.array(feats))
print("saved", len(names))

# Export the constants the port needs from the ORIGINAL code/weights: 30 filters and SVM parameters. Run in ref-env.
import pathlib
import os, pickle, sys
sys.dont_write_bytecode = True
import numpy as np
REPO = str(pathlib.Path(__file__).resolve().parents[1] / "backend")
sys.path.insert(0, REPO)
from app import patchcraft_original as po
from PIL import Image
DATA = os.environ["SPIKE_DATA"]
w = po.apply_all_filters.__self__.hpf.weight.detach().numpy().astype(np.float32)  # (30,3,5,5)
svc = pickle.load(open(os.path.join(REPO, "weights", "svm.pkl"), "rb"))
np.savez(os.path.join(DATA, "params.npz"), hpf=w, sv=svc.support_vectors_, coef=svc.dual_coef_[0],
         b=svc.intercept_[0], gamma=svc._gamma, pa=svc.probA_[0], pb=svc.probB_[0])
print("hpf", w.shape, "sv", svc.support_vectors_.shape)
import glob
sizes = {Image.open(f).size for f in glob.glob(os.path.join(REPO, "tests", "sample_images", "*.png"))}
print("sample image sizes:", sizes)

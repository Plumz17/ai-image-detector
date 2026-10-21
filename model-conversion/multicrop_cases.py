# Shared by both runners: build multi-crop test images out of real samples, so each crop is one known sample.
import io, glob, os
import numpy as np
from PIL import Image

def build(sample_dir):
    L = lambda n: Image.open(os.path.join(sample_dir, n)).convert("RGB")
    s256 = lambda n: np.asarray(L(n).resize((256, 256)))        # force 256 so crop == sample
    a1, a2, n1, n2 = s256("ai (1).png"), s256("ai (10).png"), s256("no_ai (1).png"), s256("no_ai (10).png")
    big = [f for f in sorted(glob.glob(os.path.join(sample_dir, "*.png"))) if Image.open(f).size == (512, 512)][:2]
    cases = {
        "2 crops fake+real (tie)":      np.hstack([a1, n1]),
        "3 crops fake,fake,real":       np.hstack([a1, a2, n1]),
        "3 crops real,real,fake":       np.hstack([n1, n2, a1]),
        "4 crops alternating (tie)":    np.hstack([a1, n1, a2, n2]),
        "2 crops tall real+fake (tie)": np.vstack([n1, a1]),
        "8 crops (max)":                np.hstack([a1, n1, a2, n2, a1, n1, a2, n2]),
    }
    if len(big) == 2:  # 512x512 crops go through the resize step
        cases["2 crops of 512px (resize)"] = np.hstack([np.asarray(Image.open(f).convert("RGB")) for f in big])
    out = {}
    for k, arr in cases.items():
        b = io.BytesIO(); Image.fromarray(arr).save(b, "PNG"); out[k] = b.getvalue()
    return out

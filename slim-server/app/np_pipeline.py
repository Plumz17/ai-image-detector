"""PatchCraft preprocessing + SVM in plain NumPy/Pillow (no torch, cv2 or scikit-learn).
Line-by-line port of backend/app/patchcraft_original.py, written to be easy to re-write in Kotlin.
The CNN is NOT here: it runs from cnn.tflite. Constants come from params.npz (exported from the original)."""
import io, math, random
import numpy as np
from PIL import Image

P = 32           # tile size
SIDE = 256       # every crop is resized to 256x256 first
SUB = 192        # rich/poor texture images are 192x192 = 6x6 tiles


def multiple_crop(img):
    """Cut the image into overlapping squares along its long side (same box arithmetic as the original)."""
    img = img.convert("RGB")
    w, h = img.size
    max_d, min_d = max(w, h), min(w, h)
    n = math.ceil(max_d / min_d)
    offset = 0 if n == 1 else (max_d - min_d) / (n - 1)
    out = []
    for i in range(n):
        if w > h:
            out.append(img.crop((int(i * offset), 0, int(i * offset + min_d), min_d)))
        else:
            out.append(img.crop((0, int(i * offset), min_d, int(i * offset + min_d))))
    return out


def gray_u8(rgb):
    """cv2.COLOR_RGB2GRAY for uint8 in OpenCV 5.0.0 (the version the backend pins): 15-bit fixed point,
    coefficients 0.299/0.587/0.114 scaled by 2^15, rounded. (OpenCV 4 used 14 bits and differs on ~0.3% of values.)"""
    r, g, b = (rgb[..., c].astype(np.int32) for c in range(3))
    return ((r * 9798 + g * 19235 + b * 3735 + (1 << 14)) >> 15).astype(np.int32)


def to_tiles(arr):
    """(256,256[,3]) -> (64,32,32[,3]); tile index = row*8 + col, same order as img_to_patches."""
    s = arr.shape
    t = arr.reshape(8, P, 8, P, *s[2:]).swapaxes(1, 2)
    return t.reshape(64, P, P, *s[2:])


def tile_scores(gray_tiles):
    """get_patch_IPV: sum of absolute neighbour differences (horizontal + vertical + both diagonals)."""
    p = gray_tiles
    h = np.abs(p[:, :, :-1] - p[:, :, 1:]).sum(axis=(1, 2))
    v = np.abs(p[:, :-1, :] - p[:, 1:, :]).sum(axis=(1, 2))
    d1 = np.abs(p[:, :-1, :-1] - p[:, 1:, 1:]).sum(axis=(1, 2))
    d2 = np.abs(p[:, 1:, :-1] - p[:, :-1, 1:]).sum(axis=(1, 2))
    return h + v + d1 + d2


def split_rich_poor(scores):
    """Stable sort by score; the calmer half is 'poor', the busier half is 'rich'."""
    order = np.argsort(scores, kind="stable")
    mid = len(order) // 2
    return order[mid:], order[:mid]          # rich ids, poor ids


def assemble(tiles, rng):
    """get_complete_image: shuffle, pad to 36 tiles with random repeats of the first 32, tile into 192x192."""
    tiles = list(tiles)
    rng.shuffle(tiles)
    n = len(tiles)
    while len(tiles) < (SUB // P) ** 2:
        tiles.append(tiles[rng.randint(0, n - 1)])
    grid = np.asarray(tiles).reshape(SUB // P, SUB // P, P, P, 3)
    return grid.swapaxes(1, 2).reshape(SUB, SUB, 3)


def hpf(img_hwc, weights):
    """30 high-pass filters: 5x5 'same' cross-correlation over the 3 colour channels, zero padding."""
    x = np.pad(img_hwc.astype(np.float32).transpose(2, 0, 1), ((0, 0), (2, 2), (2, 2)))
    win = np.lib.stride_tricks.sliding_window_view(x, (5, 5), axis=(1, 2))   # (3,192,192,5,5)
    return np.einsum("chwij,kcij->khw", win, weights, optimize=True).astype(np.float32)   # (30,192,192)


def preprocess(crop, weights, rng):
    """One crop -> (frt, fpt), each (1,30,192,192) float32. Note: the original never normalises before filtering."""
    if crop.size != (SIDE, SIDE):
        crop = crop.resize((SIDE, SIDE))     # Pillow default resample, same call as the original
    rgb = np.asarray(crop)
    tiles = to_tiles(rgb)
    rich, poor = split_rich_poor(tile_scores(to_tiles(gray_u8(rgb))))
    rt, pt = assemble(tiles[rich], rng), assemble(tiles[poor], rng)
    return hpf(rt, weights)[None], hpf(pt, weights)[None]


class SVM:
    """RBF SVC from svm.pkl: class 1 (fake) when sum(coef * exp(-gamma*||x-sv||^2)) + b > 0."""
    def __init__(self, p):
        self.sv, self.coef, self.b, self.gamma = p["sv"], p["coef"], float(p["b"]), float(p["gamma"])
        self.pa, self.pb = float(p["pa"]), float(p["pb"])

    def decision(self, x):
        return float(self.coef @ np.exp(-self.gamma * ((self.sv - x) ** 2).sum(axis=1)) + self.b)

    def prob_fake(self, x):                  # Platt scaling; only used to break exact ties
        return 1.0 - 1.0 / (1.0 + math.exp(-self.pa * self.decision(x) + self.pb))


def classify(image_bytes, params, cnn, seed=None):
    """Whole pipeline. `cnn(frt, fpt) -> 32 floats` is the LiteRT model. Returns the backend's result shape."""
    rng = random.Random(seed)
    svm = SVM(params)
    votes, feats = [], []
    for crop in multiple_crop(Image.open(io.BytesIO(image_bytes))):
        frt, fpt = preprocess(crop, params["hpf"], rng)
        f = np.asarray(cnn(frt, fpt), dtype=np.float64).reshape(-1)
        feats.append(f)
        votes.append(int(svm.decision(f) > 0))
    ratio = sum(votes) / len(votes)
    if ratio > 0.5: label = "fake"
    elif ratio < 0.5: label = "real"
    else: label = "fake" if np.mean([svm.prob_fake(f) for f in feats]) >= 0.5 else "real"
    return {"label": label, "crops_analyzed": len(votes), "fake_crop_ratio": round(ratio, 4)}

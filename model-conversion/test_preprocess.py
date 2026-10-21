# Stage-by-stage comparison: NumPy port vs the ORIGINAL code. Run in ref-env.
import pathlib
import glob, io, os, random, sys
sys.dont_write_bytecode = True
import cv2, numpy as np, torch
from PIL import Image
REPO = str(pathlib.Path(__file__).resolve().parents[1] / "backend")
sys.path.insert(0, REPO); sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "slim-server" / "app"))
from app import patchcraft_original as po
import np_pipeline as npp

params = np.load(os.path.join(os.environ["SPIKE_DATA"], "params.npz"))
gen = po.PatchGenerator()
files = sorted(glob.glob(os.path.join(REPO, "tests", "sample_images", "*.png")))
imgs = [Image.open(f).convert("RGB") for f in files]
fails = {k: 0 for k in ("crop", "gray", "ipv", "split", "assemble_rich", "assemble_poor", "mine_rich", "mine_poor")}
hpf_abs, hpf_rel, n_crops = [], [], 0

# 1) multiple_crop on odd shapes too (wide 3:1, tall 2:1, near-square), original has the same box arithmetic
synth = [Image.fromarray(np.hstack([np.asarray(imgs[0].resize((256,256)))] * 3)),
         Image.fromarray(np.vstack([np.asarray(imgs[1].resize((256,256)))] * 2)),
         Image.fromarray(np.asarray(imgs[2].resize((300, 256))))]
mi = po.ModelInference.__new__(po.ModelInference)  # only used for its multiple_crop method (no weights needed)
for im in synth + imgs:
    b = io.BytesIO(); im.save(b, "PNG"); b.seek(0)
    a, c = mi.multiple_crop(b), npp.multiple_crop(Image.open(io.BytesIO(b.getvalue())))
    fails["crop"] += len(a) != len(c) or any(x.size != y.size or np.asarray(x).tobytes() != np.asarray(y).tobytes() for x, y in zip(a, c))

for im in imgs:
    n_crops += 1
    crop = im if im.size == (256, 256) else im.resize((256, 256))   # same call as the original
    rgb = np.asarray(crop)
    # 2) grayscale vs OpenCV
    g = npp.gray_u8(rgb); gcv = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype(np.int32)
    fails["gray"] += int((g != gcv).any())
    # 3) tile scores vs the original (Python loops)
    orig_patches = gen.img_to_patches(crop, 32)
    orig_ipv = [gen.get_patch_IPV(cv2.cvtColor(p, cv2.COLOR_RGB2GRAY).astype(np.int32)) for p in orig_patches]
    mine = npp.tile_scores(npp.to_tiles(g))
    fails["ipv"] += int(list(mine) != list(orig_ipv))
    # 4) rich/poor split vs the original (same tiles, same order)
    tiles = npp.to_tiles(rgb)
    orich, opoor = gen.extract_rich_and_poor_textures(orig_ipv, orig_patches)
    rid, pid = npp.split_rich_poor(mine)
    fails["split"] += int(not (np.array_equal(np.array(orich), tiles[rid]) and np.array_equal(np.array(opoor), tiles[pid])))
    # 5) the original's shuffled assembly: every tile must come from the right half, and all 32 must appear
    rt, pt = gen.smash_n_reconstruct(crop, 32)
    for out, ids, key in ((rt, rid, "assemble_rich"), (pt, pid, "assemble_poor")):
        used = {t.tobytes() for t in out.reshape(6, 32, 6, 32, 3).swapaxes(1, 2).reshape(36, 32, 32, 3)}
        want = {tiles[i].tobytes() for i in ids}
        fails[key] += int(not (used <= want and used >= want))
    # 5b) same property for MY assembly
    rng = random.Random(1)
    for ids, key in ((rid, "mine_rich"), (pid, "mine_poor")):
        out = npp.assemble(tiles[ids], rng)
        used = {t.tobytes() for t in out.reshape(6, 32, 6, 32, 3).swapaxes(1, 2).reshape(36, 32, 32, 3)}
        want = {tiles[i].tobytes() for i in ids}
        fails[key] += int(used != want)
    # 6) the 30 filters on IDENTICAL input (the original's rt)
    t = po.ndarrimg2tensor(rt)
    with torch.no_grad():
        ref = po.apply_all_filters(t).numpy()
    got = npp.hpf(rt, params["hpf"])
    d = np.abs(got - ref); hpf_abs.append(d.max()); hpf_rel.append(d.max() / max(np.abs(ref).max(), 1))

print(f"images tested: {n_crops} (+{len(synth)} synthetic shapes for cropping)")
for k, v in fails.items(): print(f"  mismatches {k:14s}: {v}")
print(f"  filters: max abs diff {max(hpf_abs):.2e}, relative to output range {max(hpf_rel):.2e}")

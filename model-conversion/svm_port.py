# Spike step 5: re-implement the SVM with NumPy only (parameters taken from svm.pkl) and compare with scikit-learn.
import pathlib
import glob, os, pickle, sys
sys.dont_write_bytecode = True
import numpy as np

DATA = os.environ["SPIKE_DATA"]
svc = pickle.load(open(str(pathlib.Path(__file__).resolve().parents[1] / "backend" / "weights" / "svm.pkl"), "rb"))
SV, COEF, B, GAMMA = svc.support_vectors_, svc.dual_coef_[0], svc.intercept_[0], svc._gamma
A, PB = svc.probA_[0], svc.probB_[0]

def decision(x):          # RBF kernel: sum(coef * exp(-gamma * ||x - sv||^2)) + intercept
    return COEF @ np.exp(-GAMMA * ((SV - x) ** 2).sum(axis=1)) + B

def label(x):             # class 1 (fake) when decision > 0
    return int(decision(x) > 0)

def prob_fake(x):         # Platt scaling, only used by the backend to break exact ties
    # libsvm fits Platt on the opposite-sign decision, and its probability is for class 0
    return 1.0 - 1.0 / (1.0 + np.exp(-A * decision(x) + PB))

gold = {os.path.basename(f): np.load(f) for f in sorted(glob.glob(os.path.join(DATA, "golden", "*.npz")))}
tfl = np.load(os.path.join(DATA, "tflite_features.npz"))
tfl = dict(zip(tfl["names"], tfl["feats"]))

bad_label = bad_tfl = 0; dd = []; dp = []; margins = []
for n, g in gold.items():
    x, want = g["feature"].astype(np.float64), int(g["svm_pred"])
    sk_dec = svc.decision_function(x[None])[0]
    dd.append(abs(decision(x) - sk_dec)); margins.append(abs(sk_dec))
    dp.append(abs(prob_fake(x) - svc.predict_proba(x[None])[0, 1]))
    bad_label += label(x) != want
    bad_tfl += label(tfl[n].astype(np.float64)) != want   # converted CNN -> NumPy SVM vs the original decision
print(f"crops: {len(gold)} | numpy SVM label mismatches vs scikit-learn: {bad_label}")
print(f"decision value max diff vs sklearn: {max(dd):.2e}")
print(f"predict_proba max diff vs sklearn (Platt): {max(dp):.2e}")
print(f"converted CNN -> numpy SVM label mismatches vs original: {bad_tfl}")
print(f"smallest |decision| margin among crops: {min(margins):.4f}")

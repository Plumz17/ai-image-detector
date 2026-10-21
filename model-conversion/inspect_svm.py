# Spike step 3: describe svm.pkl (read-only). Run in ref-env.
import pathlib
import pickle, sys
sys.dont_write_bytecode = True

PATH = str(pathlib.Path(__file__).resolve().parents[1] / "backend" / "weights" / "svm.pkl")
obj = pickle.load(open(PATH, "rb"))

def describe(o, indent=0):
    pad = " " * indent
    print(f"{pad}{type(o).__module__}.{type(o).__name__}")
    if hasattr(o, "steps"):  # sklearn Pipeline
        for name, step in o.steps:
            print(f"{pad}  step '{name}':")
            describe(step, indent + 4)
        return
    if hasattr(o, "best_estimator_"):  # GridSearchCV / RandomizedSearchCV
        print(f"{pad}  best_params_ = {getattr(o, 'best_params_', None)}")
        describe(o.best_estimator_, indent + 4)
        return
    for a in ("kernel", "C", "gamma", "degree", "coef0", "probability", "class_weight",
              "decision_function_shape", "tol", "max_iter", "penalty", "loss", "dual"):
        if hasattr(o, a):
            print(f"{pad}  {a} = {getattr(o, a)!r}")
    for a in ("classes_", "n_features_in_", "n_support_", "_gamma", "intercept_", "probA_", "probB_",
              "support_vectors_", "dual_coef_", "coef_", "mean_", "scale_"):
        if hasattr(o, a):
            v = getattr(o, a)
            print(f"{pad}  {a}: shape={getattr(v, 'shape', None)} value={v if getattr(v, 'size', 99) <= 8 else '...'}")

describe(obj)

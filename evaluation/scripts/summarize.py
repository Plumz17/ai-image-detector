# Reads a CSV from run_folder.py and prints the confusion matrix and the metrics.
"""
What it does:
  1. Keeps only the rows with HTTP 200 (real answers).
  2. For each image, the final label is the majority of its runs (5 runs, so no ties).
  3. Counts TP, FN, FP, TN with fake as the positive class, and prints the metrics.
  4. Repeats the numbers for the manual subset, if manual_subset.txt exists.
  5. With --baseline, counts how many images changed label compared with another CSV.

Examples, from the repository root:
  backend\\.venv\\Scripts\\python.exe evaluation\\scripts\\summarize.py --csv evaluation\\results\\baseline_runs.csv
  backend\\.venv\\Scripts\\python.exe evaluation\\scripts\\summarize.py --csv evaluation\\results\\jpeg_q95_runs.csv --baseline evaluation\\results\\baseline_runs.csv
"""

# Imports
import argparse
import csv
import statistics
from collections import defaultdict
from pathlib import Path

# Configs
EVAL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_SUBSET = EVAL_DIR / "results" / "manual_subset.txt"


def make_key(file_name):
    # "0_real/abc.png" and "0_real/abc.jpg" give the same key, so a changed copy matches its original
    folder, name = file_name.split("/", 1)
    return (folder, Path(name).stem)


def read_runs(csv_path):
    # Return {key: list of labels} for the successful runs, plus the list of times in ms and the true labels
    labels = defaultdict(list)
    truth = {}
    times = []
    failed = 0
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["http_status"] != "200":
                failed += 1
                continue
            key = make_key(row["file"])
            labels[key].append(row["label"])
            truth[key] = row["true_label"]
            times.append(int(row["ms"]))
    return labels, truth, times, failed


def final_labels(labels):
    # Majority label per image. A tie (only possible if some runs failed) gives None.
    result = {}
    for key, runs in labels.items():
        fake = runs.count("fake")
        real = runs.count("real")
        result[key] = "fake" if fake > real else "real" if real > fake else None
    return result


def divide(a, b):
    return a / b if b else 0.0


def report(title, keys, final, truth):
    # Count the four cells for the given images and print the table and the metrics
    tp = fn = fp = tn = 0
    for key in sorted(keys):
        if final.get(key) is None:
            continue
        predicted, actual = final[key], truth[key]
        if actual == "fake" and predicted == "fake":
            tp += 1
        elif actual == "fake" and predicted == "real":
            fn += 1
        elif actual == "real" and predicted == "fake":
            fp += 1
        else:
            tn += 1

    total = tp + fn + fp + tn
    print(f"\n=== {title} ({total} images) ===")
    print(f"                predicted fake   predicted real")
    print(f"actual fake     TP = {tp:<10}   FN = {fn}")
    print(f"actual real     FP = {fp:<10}   TN = {tn}")
    print(f"accuracy    {divide(tp + tn, total):.3f}")
    print(f"recall      {divide(tp, tp + fn):.3f}   (fake images found)")
    print(f"specificity {divide(tn, tn + fp):.3f}   (real images found)")
    precision = divide(tp, tp + fp)
    recall = divide(tp, tp + fn)
    print(f"precision   {precision:.3f}   (when it says fake, how often it is right)")
    print(f"F1          {divide(2 * precision * recall, precision + recall):.3f}   (balance of precision and recall)")


def read_subset(subset_path):
    # The subset file has lines like "0_real/abc.png"
    if not subset_path.exists():
        return set()
    lines = subset_path.read_text(encoding="utf-8").splitlines()
    return {make_key(line.strip()) for line in lines if line.strip()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="CSV written by run_folder.py")
    parser.add_argument("--subset", default=str(DEFAULT_SUBSET), help="list of the manual subset images")
    parser.add_argument("--baseline", help="CSV of the baseline, to count label changes")
    args = parser.parse_args()

    labels, truth, times, failed = read_runs(args.csv)
    final = final_labels(labels)

    print(f"{len(labels)} images, {sum(len(r) for r in labels.values())} successful runs, {failed} failed requests")
    if times:
        print(f"median time per request: {statistics.median(times)} ms")

    undecided = [k for k, v in final.items() if v is None]

    report("All images", labels.keys(), final, truth)

    if undecided:
        print(f"left out because of a tie between runs: {len(undecided)}")

    subset = read_subset(Path(args.subset)) & set(labels.keys())
    if subset:
        report("Manual subset", subset, final, truth)

    if args.baseline:
        base_labels, _, _, _ = read_runs(args.baseline)
        base_final = final_labels(base_labels)
        both = [k for k in final if k in base_final and final[k] and base_final[k]]
        changed = [k for k in both if final[k] != base_final[k]]
        print(f"\n=== Compared with the baseline ({len(both)} images in both) ===")
        print(f"label changed: {len(changed)}")
        for key in sorted(changed):
            print(f"  {key[0]}/{key[1]}: {base_final[key]} -> {final[key]}")


if __name__ == "__main__":
    main()

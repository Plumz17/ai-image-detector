# Picks the baseline test images from the thesis dataset.
"""
What it does:
  1. Reads the image names in <source>/0_real and <source>/1_fake.
  2. Sorts them, then shuffles them with a fixed seed (so the pick is always the same).
  3. Keeps the first 100 of each class (the baseline).
  4. The first 20 of those 100 are the manual subset.
  5. Writes the two lists into evaluation/results/ and copies the 200 images into evaluation/data/baseline/.
"""

# You can run it from the repository root:
# e.g. backend\\.venv\\Scripts\\python.exe evaluation\\scripts\\select_baseline.py --source "C:\\datasets\\ai_image_detection_test"

# Imports
import argparse
import random
import shutil
from pathlib import Path

# Configs
SEED = 67
BASELINE_PER_CLASS = 100
MANUAL_PER_CLASS = 20
CLASSES = ["0_real", "1_fake"]  # the folder names are the true labels
IMAGE_TYPES = {".png", ".jpg", ".jpeg"}

# evaluation folder = two levels above this file (evaluation/scripts/select_baseline.py)
EVAL_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = EVAL_DIR / "data" / "baseline"
RESULTS_DIR = EVAL_DIR / "results"


def list_images(folder):
    #Return the image file names in a folder, sorted, so the order is the same on every computer.
    names = [p.name for p in folder.iterdir() if p.suffix.lower() in IMAGE_TYPES]
    return sorted(names)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="folder that contains 0_real and 1_fake")
    args = parser.parse_args()
    source = Path(args.source)

    baseline = []  # lines like "0_real/image.png"
    manual = []

    for label in CLASSES:
        names = list_images(source / label)
        print(f"{label}: found {len(names)} images")
        if len(names) < BASELINE_PER_CLASS:
            raise SystemExit(f"{label} has fewer than {BASELINE_PER_CLASS} images, check --source")

        # A new Random with the same seed for each class, so the pick never depends on the other class
        random.Random(SEED).shuffle(names)
        chosen = names[:BASELINE_PER_CLASS]
        chosen_manual = chosen[:MANUAL_PER_CLASS]  # first 20 of the 100, so they are always inside the baseline

        baseline += [f"{label}/{name}" for name in chosen]
        manual += [f"{label}/{name}" for name in chosen_manual]

        # Copy the chosen images
        out_folder = DATA_DIR / label
        out_folder.mkdir(parents=True, exist_ok=True)
        for name in chosen:
            shutil.copy2(source / label / name, out_folder / name)

    # Write the two lists (these are small, so they can be committed)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / "baseline_files.txt").write_text("\n".join(baseline) + "\n", encoding="utf-8")
    (RESULTS_DIR / "manual_subset.txt").write_text("\n".join(manual) + "\n", encoding="utf-8")

    print(f"baseline: {len(baseline)} images, manual subset: {len(manual)} images")
    print(f"images copied to {DATA_DIR}")
    print(f"lists written to {RESULTS_DIR}")


if __name__ == "__main__":
    main()

# Sends every image in a test folder to the API, several times, and saves each answer in a CSV file.
"""
What it does:
  1. Reads the images in <folder>/0_real and <folder>/1_fake.
  2. Sends each image to POST /predict, 5 times (preprocessing is random, so one run is not enough).
  3. Adds one row per request to the CSV file. The true label comes from the folder name.
  4. If the CSV already exists, it skips the runs that already have an answer (HTTP 200),
     so you can stop it with Ctrl+C and start it again later.

The server must already be running (and started with a high rate limit, see below).

Example, from the repository root:
  backend\\.venv\\Scripts\\python.exe evaluation\\scripts\\run_folder.py --folder evaluation\\data\\baseline --out evaluation\\results\\baseline_runs.csv
"""

# Imports
import argparse
import csv
import time
from pathlib import Path

import httpx

# Configs
CLASSES = ["0_real", "1_fake"]  # the folder names are the true labels
IMAGE_TYPES = {".png", ".jpg", ".jpeg"}
COLUMNS = ["file", "true_label", "run", "http_status", "label", "crops_analyzed", "fake_crop_ratio", "ms"]
TIMEOUT_SECONDS = 60
MAX_FAILS_IN_A_ROW = 5  # stop early if the server does not answer (for example it is not running)


def list_files(folder):
    # Return the images as "0_real/name.png", sorted
    files = []
    for label in CLASSES:
        if not (folder / label).exists():
            continue  # some tests have only one class (for example the enhanced real photos)
        for path in sorted((folder / label).iterdir()):
            if path.suffix.lower() in IMAGE_TYPES:
                files.append(f"{label}/{path.name}")
    return files


def read_done(csv_path):
    # Return the (file, run) pairs that already have a successful answer
    done = set()
    if csv_path.exists():
        with open(csv_path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row["http_status"] == "200":
                    done.add((row["file"], int(row["run"])))
    return done


def send_image(client, url, image_path):
    # Send one image. Returns (http_status, answer_dict, milliseconds). Status 0 means no answer at all.
    start = time.perf_counter()
    try:
        with open(image_path, "rb") as f:
            response = client.post(url, files={"file": (image_path.name, f)})
        ms = round((time.perf_counter() - start) * 1000)
        try:
            return response.status_code, response.json(), ms
        except ValueError:
            return response.status_code, {}, ms
    except httpx.HTTPError:
        ms = round((time.perf_counter() - start) * 1000)
        return 0, {}, ms


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", required=True, help="folder that contains 0_real and 1_fake")
    parser.add_argument("--out", required=True, help="CSV file to write (created if it does not exist)")
    parser.add_argument("--url", default="http://localhost:8000/predict")
    parser.add_argument("--runs", type=int, default=5, help="how many times each image is sent")
    args = parser.parse_args()

    folder = Path(args.folder)
    csv_path = Path(args.out)
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    files = list_files(folder)
    done = read_done(csv_path)
    total = len(files) * args.runs
    print(f"{len(files)} images x {args.runs} runs = {total} requests, {len(done)} already done")

    is_new_file = not csv_path.exists()
    fails_in_a_row = 0
    sent = 0

    with open(csv_path, "a", newline="", encoding="utf-8") as f, httpx.Client(timeout=TIMEOUT_SECONDS) as client:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        if is_new_file:
            writer.writeheader()

        for name in files:
            true_label = "fake" if name.startswith("1_fake") else "real"

            for run in range(1, args.runs + 1):
                if (name, run) in done:
                    continue

                status, answer, ms = send_image(client, args.url, folder / name)
                writer.writerow({
                    "file": name,
                    "true_label": true_label,
                    "run": run,
                    "http_status": status,
                    "label": answer.get("label", ""),
                    "crops_analyzed": answer.get("crops_analyzed", ""),
                    "fake_crop_ratio": answer.get("fake_crop_ratio", ""),
                    "ms": ms,
                })
                f.flush()  # write to disk now, so a crash loses nothing
                sent += 1

                # Progress bar: \r goes back to the start of the line, so the bar is redrawn in place
                finished = len(done) + sent
                filled = 30 * finished // max(total, 1)
                print(f"\r[{'#' * filled}{'-' * (30 - filled)}] {finished}/{total}", end="", flush=True)

                if status == 200:
                    fails_in_a_row = 0
                else:
                    fails_in_a_row += 1
                    print(f"\n  {name} run {run}: HTTP {status}")
                    if fails_in_a_row >= MAX_FAILS_IN_A_ROW:
                        raise SystemExit(f"{MAX_FAILS_IN_A_ROW} failed requests in a row, stopping. Is the server running?")

    print(f"\ndone, {sent} requests sent in this run. Results in {csv_path}")


if __name__ == "__main__":
    main()

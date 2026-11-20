# Makes a changed copy of the baseline images (for example JPEG compressed or smaller).
"""
What it does:
  1. Reads every image in evaluation/data/baseline/0_real and 1_fake.
  2. Optionally crops the centre (--crop), then makes it smaller (--scale), then saves it as JPEG (--quality).
  3. Writes the result to evaluation/data/<name>/0_real and 1_fake, with the same file names
     (only the ending changes to .jpg when --quality is used).

Examples, from the repository root:
  JPEG quality 95:        python evaluation\\scripts\\make_variants.py --name jpeg_q95 --quality 95
  JPEG quality 70:        python evaluation\\scripts\\make_variants.py --name jpeg_q70 --quality 70
  Half size, still PNG:   python evaluation\\scripts\\make_variants.py --name half --scale 0.5
  Half size + JPEG q70:   python evaluation\\scripts\\make_variants.py --name half_q70 --scale 0.5 --quality 70
  Centre crop (50%):      python evaluation\\scripts\\make_variants.py --name crop50 --crop 0.5
"""

# Imports
import argparse
from pathlib import Path

from PIL import Image

# Configs
CLASSES = ["0_real", "1_fake"]  # the folder names are the true labels
IMAGE_TYPES = {".png", ".jpg", ".jpeg"}

EVAL_DIR = Path(__file__).resolve().parent.parent
BASELINE_DIR = EVAL_DIR / "data" / "baseline"


def change_image(image, crop, scale, quality, out_path):
    # Crop first (if asked), then smaller, then save. JPEG has no transparency, so convert to RGB for it.
    if crop is not None:
        # keep the centre part: crop=0.5 keeps half of the width and half of the height
        new_w, new_h = round(image.width * crop), round(image.height * crop)
        left, top = (image.width - new_w) // 2, (image.height - new_h) // 2
        image = image.crop((left, top, left + new_w, top + new_h))

    if scale is not None:
        new_size = (round(image.width * scale), round(image.height * scale))
        image = image.resize(new_size, Image.Resampling.LANCZOS)

    if quality is not None:
        image.convert("RGB").save(out_path, "JPEG", quality=quality)
    else:
        image.save(out_path, "PNG")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True, help="name of the new folder inside evaluation/data/")
    parser.add_argument("--quality", type=int, help="JPEG quality from 1 to 100 (leave out to keep PNG)")
    parser.add_argument("--scale", type=float, help="size factor, for example 0.5 for half the width and height")
    parser.add_argument("--crop", type=float, help="keep the centre part, for example 0.5 keeps half the width and height")
    args = parser.parse_args()

    if args.quality is None and args.scale is None and args.crop is None:
        raise SystemExit("Give at least --quality, --scale or --crop, otherwise the images would not change")
    if args.crop is not None and not 0 < args.crop < 1:
        raise SystemExit("--crop must be between 0 and 1, for example 0.5")

    out_root = EVAL_DIR / "data" / args.name
    extension = ".jpg" if args.quality is not None else ".png"
    count = 0

    for label in CLASSES:
        out_folder = out_root / label
        out_folder.mkdir(parents=True, exist_ok=True)

        for path in sorted((BASELINE_DIR / label).iterdir()):
            if path.suffix.lower() not in IMAGE_TYPES:
                continue
            with Image.open(path) as image:
                change_image(image, args.crop, args.scale, args.quality, out_folder / (path.stem + extension))
            count += 1

    print(f"{count} images written to {out_root}")


if __name__ == "__main__":
    main()

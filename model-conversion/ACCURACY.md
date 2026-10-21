# Accuracy on real-world images: what we know and what to do next

## The problem
Testers on the phone app (camera photos, WhatsApp/downloaded images, AI images from ChatGPT/Midjourney, screenshots)
report that the result looks wrong or random for most images. On the 40 repo sample images the result is about 97% right.

## What has been established
- **The slim server behaves like the original** on the repo samples and on multi-crop test images
  (see [RESULTS.md](RESULTS.md)). So the problem is not specific to the slim server.
- **The original model is very sensitive to JPEG compression** (`jpeg_check.py`, 20 AI + 20 real samples, majority of 3 runs,
  only the file format changed):

  | Format | AI called fake (should be high) | Real called fake (should be low) |
  |---|---|---|
  | PNG, as given | 20/20 | 1/20 |
  | JPEG q=95 | 20/20 | 8/20 |
  | JPEG q=85 | 15/20 | 8/20 |
  | JPEG q=70 | 5/20 | 6/20 |
  | JPEG q=50 | 0/20 | 3/20 |

  Camera photos, WhatsApp and downloaded images are all JPEGs, which fits the reports. The model reads very fine pixel
  texture, and JPEG compression destroys it. Every crop is also shrunk to 256x256 first, which removes more of it from large photos.
- **Image size alone is not the cue** (`size_check.py`): in the repo samples every AI image is 512x512 and every real one is 256x256,
  but shrinking the AI ones to 256 still gives fake (20/20) and enlarging the real ones to 512 still gives real (19/20).
- **The original is random by design on borderline images** (tiles are shuffled), so one image can get different labels on different calls.

## What has NOT been established
- Accuracy on a large labelled set. The 40 samples have an unknown source, and only PNGs.
- Whether the slim server and the original also agree on JPEGs and large photos. Run `compare_folder.py` on real images to check.
- How the model does on newer generators.

## Next steps
1. Collect 10-20 images per class (`ai/` and `real/` subfolders), as original files, in a mix of PNG and JPEG, and run
   `python compare_folder.py <folder> --slim-url <hosted address> --csv result.csv` (needs the backend's packages, see the script).
2. Ask the model's author: what data was it trained on (formats, generators, resolution, were the images JPEG-compressed)?
   Is there a held-out test set and the expected accuracy? Could the model be retrained or adjusted for compressed images?
3. Decide what the app should say. Until accuracy on compressed images is known, the app should not present the result as certain
   (the API contract already says `fake_crop_ratio` is a vote share, not a probability).

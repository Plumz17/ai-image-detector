# LiteRT feasibility spike: results (21 Oct 2026)

No repo file was changed. Scripts are in this folder; environments and the 157 MB of reference tensors are in a temp folder.

| Check | Result |
|---|---|
| Original model, 40 images x 5 runs | 194/200 match filename label; `no_ai (7)` flips (1 of 5); `no_ai (20)` always wrong. Preprocessing is random (shuffle/duplicate), so the original is not fully deterministic. |
| `svm.pkl` | scikit-learn SVC, RBF, 1343 support vectors x 32 features, gamma 0.0468, no scaler. |
| CNN -> `.tflite` (`litert-torch` 0.10.0, Linux container) | Converts without edits. 547 KB. Max abs difference vs original features: 1.4e-5 on 40 crops. Control (inputs swapped) differs by 1.8, so the test is sensitive. |
| NumPy SVM vs scikit-learn | 0 label mismatches, decision values within 1e-12. `predict_proba` within 2.4e-3 (used only to break exact ties). |
| Converted CNN -> NumPy SVM vs original decisions | 0 mismatches on 40 crops. Smallest decision margin 0.53. |
| Speed | `.tflite` CNN 63 ms per crop (PC, Linux container); 3.2 G multiply-adds. Phone speed not measured. |
| Runtime size | ai-edge-litert + NumPy + Pillow = about 155 MB (Linux) vs PyTorch stack about 949 MB (Windows measurement). Not like-for-like. |

## Not yet covered
- All 40 samples are square, single-crop images. The multi-crop path is untested end to end (crop boxes were tested).
- (Preprocessing was ported and tested later, see the section below.)
- No phone timing. No larger labelled test set (ask the model's author).
- `litert-converter` has no Windows build; conversion needs Linux/Docker.
- The 30 high-pass filters were not folded into the graph; they are still applied in preprocessing.

# Preprocessing port (NumPy + Pillow), added 21 Oct 2026
Code: `port/np_pipeline.py`. Tests: `test_preprocess.py` (stage by stage vs the original), `e2e_container.py`, `flip_*.py`.

| Check | Result |
|---|---|
| Crops (40 samples + 3 odd shapes) | 0 mismatches |
| Grayscale vs OpenCV 5.0.0 | 0 mismatches once the 15-bit formula is used (9798/19235/3735 >> 15). OpenCV 4's 14-bit formula differs on ~0.3% of values: the result depends on the OpenCV version. |
| Tile scores, rich/poor split | 0 mismatches (exact integers, same order) |
| Shuffled assembly | Same tile sets as the original (the shuffle itself is random by design) |
| 30 filters on identical input | max abs diff 2.4e-4 on values up to ~1e3 (relative 3e-7) |
| Whole pipeline, container with only numpy + pillow + ai-edge-litert (no torch/cv2/sklearn) | 197/200 runs match filename label (original 194/200); median 114 ms per image, peak 115 MB |
| Two borderline images, 100 runs each | `no_ai (20)`: fake 76 (port) vs 69 (original); `no_ai (7)`: fake 6 vs 4. Differences are within random noise. |

## Findings
- The original model is genuinely random on borderline images: `no_ai (20)` is labelled fake in about 70% of runs, so one request can give either answer. Worth telling the model's author.
- The port runs on a server with ~155 MB of packages and ~115 MB RAM instead of ~949 MB / ~0.3 GB.
- Biggest risk for an Android (Kotlin) port: `Image.resize((256,256))` on the 512x512 samples uses Pillow's antialiased bicubic. The port matched because it uses Pillow; Kotlin has no identical built-in (Android's scaler is different), so it must be re-implemented and tested. A server port does not have this problem.
- Not yet tested: images with more than 1 crop in the full pipeline (crop logic itself matched), phone speed, a larger labelled dataset, and the filters inside the TFLite graph.

# Multi-crop and limited-hardware tests, added 21 Oct 2026
Multi-crop cases are built from real samples (`multicrop_cases.py`); original = the backend's own `Detector`, 20 runs per case.

| Case | Original | Port |
|---|---|---|
| 2 crops fake+real (tie) | fake 20/20 | fake 20/20 |
| 3 crops, 2 fake | fake 20/20 | fake 20/20 |
| 3 crops, 2 real | fake 1/20 | fake 0/20 |
| 4 crops alternating (tie) | fake 20/20 | fake 20/20 |
| 2 crops stacked vertically (tie) | fake 20/20 | fake 20/20 |
| 8 crops, the maximum (tie) | fake 20/20 | fake 20/20 |
| 2 crops of 512 px (resize path) | fake 20/20 | fake 20/20 |
Crop counts and vote ratios identical in every case; differences are single random flips. Every tie in these cases resolved to `fake` in both versions, so the "tie resolves to real" direction is untested.

Docker CPU/RAM limits (emulation; real hosts may behave differently), 3 images:
| Limit | Original backend image | Port |
|---|---|---|
| 0.1 CPU, 512 MB (Render free plan numbers) | ready after 47 s; 26-29 s per prediction; 318 MiB used, no out-of-memory kill | startup 0.5 s; 2.7-3.5 s per prediction; 115 MB peak |
| 1 CPU, 512 MB | ready after 4 s; 1.3-2.0 s per prediction | 0.4-0.7 s per prediction |
Correction: the original backend does NOT run out of memory in 512 MB (318 MiB used), contrary to my earlier guess. On 0.1 CPU it is about 10x slower than the port.

Still untested: a real phone, a larger labelled dataset, ties that should resolve to real.

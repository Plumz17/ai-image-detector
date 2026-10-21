# Model conversion and checks

Scripts that check the slim server against the original model, and the results ([RESULTS.md](RESULTS.md)).
The original code in `backend/app/patchcraft_original.py` and the weights in `backend/weights/` are only read, never changed.

Set `SPIKE_DATA` to a folder outside the repo for big files (reference tensors are ~150 MB). Scripts that import the
original model need the backend's pinned packages (`backend/requirements.txt`, Python 3.12); the LiteRT ones run in a
Linux container because `litert-converter` has no Windows build:
```
docker build -t spike-conv -f Dockerfile.convert .
docker run --rm -v <repo>:/repo:ro -v <SPIKE_DATA>:/data -v <repo>/model-conversion:/spike:ro spike-conv python /spike/convert_cnn.py
```
Order: `gen_golden.py` (reference outputs) -> `export_params.py` -> `convert_cnn.py` (writes `cnn.tflite`) ->
`tflite_features.py` -> `svm_port.py` -> `test_preprocess.py` -> `e2e_container.py`, `mc_*.py`, `flip_*.py`, `limits_port.py`.
`golden_summary.json` is the output of `gen_golden.py` (40 sample images x 5 runs of the original).

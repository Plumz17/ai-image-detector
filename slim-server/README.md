# Slim server

Same API as `backend/` (`GET /health`, `POST /predict`, same errors, 10 MB limit, rate limit, CORS), but the model runs
on **LiteRT + NumPy** instead of PyTorch, OpenCV and scikit-learn. About 155 MB of packages and ~120 MB of RAM
(the original backend needs ~950 MB of packages and ~0.3 GB), so it fits small free hosts.

The model is the PatchCraft CNN + SVM from the original thesis implementation. Nothing in `backend/` or its weights was changed: the CNN was
converted to `app/model/cnn.tflite`, and the preprocessing and the SVM were re-written in `app/np_pipeline.py`
(constants for the 30 filters and the SVM are in `app/model/params.npz`). How it was checked against the original,
and what is still untested, is in [../model-conversion/RESULTS.md](../model-conversion/RESULTS.md).

## Run locally
```
docker build -t slim-server .
docker run -p 8000:8000 slim-server
curl -F "file=@../backend/tests/sample_images/ai (1).png" http://localhost:8000/predict
```

## Deploy to Modal (free Starter plan, scales to zero)
```
pip install modal
modal setup
modal deploy modal_app.py      # prints the public HTTPS URL
```
Settings (edit in `modal_app.py`, then deploy again): `CORS_ORIGINS` (websites allowed to call the API from a browser),
`RATE_LIMIT` (default `10/minute` per client). `REQUEST_TIMEOUT_SECONDS` (default 30) is how long a request may wait for its turn before getting a 503; set it with an environment variable. The app is limited to one container so the free credit cannot run away.

## Known differences from `backend/`
- The original shuffles image tiles at random, so a borderline image can get different labels on different calls.
  This server does too (same design); results were consistent with the original in the tests.
- `predict_proba` is re-implemented and differs from scikit-learn by up to 0.002; it is only used to break exact ties
  between crops.
- Needs OpenCV 5.0.0's grayscale rounding, which the port copies (OpenCV 4 differs on about 0.3% of values).

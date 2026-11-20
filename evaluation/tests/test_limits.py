# Test 9: sends invalid requests to /predict and checks the status code and the error message.
"""
The files it sends are in evaluation/tests/images/:
  ok.png          256 x 256 grey image (a normal, valid image, used as the control)
  empty.png       0 bytes
  notimage.png    a text file with a .png name
  anim.gif        256 x 256 GIF image
  tiny.png        32 x 32 image (smaller than the 64 px minimum)
  pixels.png      6000 x 5000 image (30 million pixels, the limit is 25 million)
  thin.png        2000 x 100 image (too long and thin, the limit is a ratio of 8)
  big.png         11 MB of zero bytes (the limit is 10 MB)

Run it from the repository root:
  backend\\.venv\\Scripts\\python.exe -m pytest evaluation\\tests -v
"""

# Imports
import os
from pathlib import Path

import httpx
import pytest

# Configs
API_URL = os.getenv("API_URL", "http://localhost:8000").rstrip("/")
IMAGES = Path(__file__).resolve().parent / "images"

# Each case: name, how the file is sent (field name, file name in the images folder; None = no file), expected status, expected message
CASES = [
    ("no file in the request", None, 400, "Missing or invalid 'file' field."),
    ("file under the wrong field name", ("image", "ok.png"), 400, "Missing or invalid 'file' field."),
    ("empty file", ("file", "empty.png"), 400, "Empty file."),
    ("text file named .png", ("file", "notimage.png"), 400, "File is not a valid or readable image."),
    ("GIF image", ("file", "anim.gif"), 400, "File must be a JPG or PNG image."),
    ("image smaller than 64 px (32 x 32)", ("file", "tiny.png"), 400, "Image is too small (shortest side must be at least 64 px)."),
    ("too many pixels (30 million)", ("file", "pixels.png"), 400, "Image has too many pixels."),
    ("too long and thin (2000 x 100)", ("file", "thin.png"), 400, "Image shape is too long and thin."),
    ("file larger than 10 MB", ("file", "big.png"), 413, "File is larger than 10 MB."),
]


def post(base_url, upload):
    files = None
    if upload is not None:
        field, name = upload
        files = {field: (name, (IMAGES / name).read_bytes())}
    return httpx.post(f"{base_url}/predict", files=files, timeout=60)


@pytest.fixture(scope="session", autouse=True)
def server_is_up():
    try:
        health = httpx.get(f"{API_URL}/health", timeout=5).json()
    except httpx.HTTPError:
        pytest.exit(f"No server answers at {API_URL}. Start it first.", returncode=1)
    assert health.get("model_loaded") is True, "The server is up but the model is not loaded."


@pytest.mark.parametrize("name, upload, status, message", CASES, ids=[c[0] for c in CASES])
def test_invalid_input_is_rejected(name, upload, status, message):
    response = post(API_URL, upload)
    assert response.status_code == status
    assert response.json() == {"status": "error", "message": message}


# Control: a normal image must still work after all the bad ones
def test_valid_image_is_accepted():
    response = post(API_URL, ("file", "ok.png"))
    assert response.status_code == 200
    assert response.json()["status"] == "success"

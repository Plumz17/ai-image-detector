# Contains every setting and limit for the slim server scripts
import os
from pathlib import Path

# Define Important Paths
MODEL_DIR = Path(__file__).resolve().parent / "model"
CNN_PATH = MODEL_DIR / "cnn.tflite"
PARAMS_PATH = MODEL_DIR / "params.npz"

# Define Limits
MAX_UPLOAD_BYTES = 10 * 1024 * 1024 # 10 MB
MIN_SIDE = 64 # Smallest allowed width/heights is 64 px
MAX_PIXELS = 25000000
MAX_CROPS = 8
REQUEST_TIMEOUT_SECONDS = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "30")) # How long the request may wait before a 503 response

# Settings from environment variables (there is no .env file here)
RATE_LIMIT = os.getenv("RATE_LIMIT", "10/minute")
_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173")
CORS_ORIGINS = [o.strip() for o in _origins.split(",") if o.strip()]
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

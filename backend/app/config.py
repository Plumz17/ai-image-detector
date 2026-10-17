# Contains every setting and limit for the backend scripts
import os
from pathlib import Path
from dotenv import load_dotenv

# Define Important Paths
BASE_DIR = Path(__file__).resolve().parent.parent
WEIGHTS_DIR = BASE_DIR / "weights"
FEATURE_EXTRACTOR_PATH = WEIGHTS_DIR / "headless_model.pth"
SVM_PATH = WEIGHTS_DIR / "svm.pkl"

# Define Limits
MAX_UPLOAD_BYTES = 10 * 1024 * 1024 # 10 MB
ALLOWED_TYPES = {"image/jpeg", "image/png"} # Only jpg/jpeg and png
MIN_SIDE = 64 # Smallest allowed width/heights is 64 px
MAX_PIXELS = 25000000
MAX_CROPS = 8
REQUEST_TIMEOUT_SECONDS = 30 # How long the request may wait before a 503 response
load_dotenv(BASE_DIR / ".env")
RATE_LIMIT = os.getenv("RATE_LIMIT","10/minute")
_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173")
CORS_ORIGINS = [o.strip() for o in _origins.split(",") if o.strip()]
LOG_LEVEL = os.getenv("LOG_LEVEL","INFO").upper()
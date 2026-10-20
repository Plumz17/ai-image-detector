# Slim server: same /health and /predict contract as backend/app/main.py, but the model runs on
# LiteRT + NumPy (no PyTorch, OpenCV or scikit-learn). See ../README.md for what is and isn't equal.
import io, logging, math, os, threading, time, uuid
from contextlib import asynccontextmanager

import numpy as np
from ai_edge_litert.interpreter import Interpreter
from fastapi import FastAPI, File, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.exceptions import HTTPException as StarletteHTTPException

from app import np_pipeline

log = logging.getLogger("app")
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO").upper(), format="%(asctime)s %(levelname)s %(message)s")

MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model")
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
RATE_LIMIT = os.getenv("RATE_LIMIT", "10/minute")      # same setting and default as backend/app/config.py
MIN_SIDE, MAX_PIXELS, MAX_CROPS = 64, 25_000_000, 8
state = {}                      # filled at startup: {"params": ..., "interp": ..., "cnn": ...}
lock = threading.Lock()         # the LiteRT interpreter is not thread-safe: one prediction at a time


class ApiError(Exception):
    def __init__(self, status_code, message):
        self.status_code, self.message = status_code, message


def error_response(status_code, message):
    return JSONResponse(status_code=status_code, content={"status": "error", "message": message})


def load_model():
    interp = Interpreter(model_path=os.path.join(MODEL_DIR, "cnn.tflite"))
    interp.allocate_tensors()
    ins, out = interp.get_input_details(), interp.get_output_details()[0]

    def cnn(frt, fpt):
        interp.set_tensor(ins[0]["index"], frt)
        interp.set_tensor(ins[1]["index"], fpt)
        interp.invoke()
        return interp.get_tensor(out["index"])

    state["params"] = dict(np.load(os.path.join(MODEL_DIR, "params.npz")))
    state["cnn"] = cnn


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        load_model()
        log.info("Model loaded")
    except Exception:
        log.exception("Model failed to load")
    yield




def client_key(request: Request):
    # Behind a platform proxy every request would look like it comes from the proxy. The LAST X-Forwarded-For entry
    # is the address that proxy saw, so a client cannot fake it by sending its own header.
    forwarded = request.headers.get("x-forwarded-for")
    return forwarded.split(",")[-1].strip() if forwarded else get_remote_address(request)


limiter = Limiter(key_func=client_key)      # counters live in memory: fine for a single container
app = FastAPI(title="AI PatchCraft Image Detector (slim)", version="0.1", lifespan=lifespan)
app.state.limiter = limiter
# Same setting and defaults as backend/app/config.py: web addresses allowed to call the API, comma separated
_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173")
app.add_middleware(CORSMiddleware, allow_origins=[o.strip() for o in _origins.split(",") if o.strip()],
                   allow_methods=["GET", "POST"], allow_headers=["*"])


# Same checks and messages as backend/app/pipeline.py::_validate_image
def validate_image(data):
    try:
        img = Image.open(io.BytesIO(data))
        if img.format not in ("JPEG", "PNG"):
            raise ApiError(400, "File must be a JPG or PNG image.")
        w, h = img.size
        if min(w, h) < MIN_SIDE:
            raise ApiError(400, f"Image is too small (shortest side must be at least {MIN_SIDE} px).")
        if w * h > MAX_PIXELS:
            raise ApiError(400, "Image has too many pixels.")
        if math.ceil(max(w, h) / min(w, h)) > MAX_CROPS:
            raise ApiError(400, "Image shape is too long and thin.")
        img.load()              # forces a full decode, so corrupt files fail here
    except ApiError:
        raise
    except Image.DecompressionBombError:
        raise ApiError(400, "Image has too many pixels.")
    except Exception:
        raise ApiError(400, "File is not a valid or readable image.")


@app.exception_handler(ApiError)
async def api_error_handler(request, exc):
    return error_response(exc.status_code, exc.message)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return error_response(429, "Too many requests. Please wait a moment and try again.")


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request, exc):
    return error_response(400, "Missing or invalid 'file' field.")


@app.exception_handler(StarletteHTTPException)
async def http_error_handler(request, exc):
    return error_response(exc.status_code, str(exc.detail))


@app.exception_handler(Exception)
async def unexpected_error_handler(request, exc):
    log.exception("Unexpected error")
    return error_response(500, "Internal server error.")


@app.get("/health")
async def check_health():
    return {"status": "ok", "model_loaded": "cnn" in state}


@app.post("/predict", summary="Classify one image as real or fake")
@limiter.limit(RATE_LIMIT)
def predict(request: Request, file: UploadFile = File()):
    start, request_id = time.perf_counter(), uuid.uuid4().hex[:8]
    data = file.file.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        return error_response(413, "File is larger than 10 MB.")
    if len(data) == 0:
        return error_response(400, "Empty file.")
    if "cnn" not in state:
        return error_response(503, "Model has not been loaded")
    validate_image(data)        # before the lock, so bad uploads fail fast
    with lock:
        result = np_pipeline.classify(data, state["params"], state["cnn"])
    log.info("predict id=%s label=%s crops=%s ms=%d", request_id, result["label"],
             result["crops_analyzed"], (time.perf_counter() - start) * 1000)
    return {"status": "success", **result}

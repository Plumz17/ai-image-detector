# The web API: /health and /predict.
import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.exceptions import HTTPException as StarletteHTTPException

from app import config, pipeline

# Log request id, duration, status and label.
logging.basicConfig(level=config.LOG_LEVEL, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("app")


# Code that runs once at startup: load the model once.
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        pipeline.load_pipeline()
        log.info("Model loaded")
    except Exception:
        log.exception("Model failed to load")
    yield
    # nothing to clean up on shutdown


# The app, rate limiter and CORS.
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="AI PatchCraft Image Detector", lifespan=lifespan)
app.state.limiter = limiter
app.add_middleware(CORSMiddleware, allow_origins=config.CORS_ORIGINS,
                   allow_methods=["GET", "POST"], allow_headers=["*"])


# Helper function to send error response
def error_response(status_code, message):
    return JSONResponse(status_code=status_code, content={
        "status": "error",
        "message": message
    })

# Our own errors from pipeline.py (bad image, too small, server busy, model not loaded)
@app.exception_handler(pipeline.PipelineError)
async def pipeline_error_handler(request: Request, exc: pipeline.PipelineError):
    return error_response(exc.status_code, exc.message)


# FastAPI's own input check failed, e.g. the "file" field is missing (default is 422)
@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    return error_response(400, "Missing or invalid 'file' field.")


# Unknown URL (404), wrong method (405), and any HTTPException raised by FastAPI itself
@app.exception_handler(StarletteHTTPException)
async def http_error_handler(request: Request, exc: StarletteHTTPException):
    return error_response(exc.status_code, str(exc.detail))


# Too many requests from one client (slowapi's own handler would break the contract)
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return error_response(429, "Too many requests. Please wait a moment and try again.")


# Anything unexpected: log the full traceback, but never send it to the client
@app.exception_handler(Exception)
async def unexpected_error_handler(request: Request, exc: Exception):
    log.exception("Unexpected error")
    return error_response(500, "Internal server error.")


# GET /health
@app.get("/health")
def check_health():
    return {"status": "ok", "model_loaded": pipeline.is_loaded()}

# POST /predict
@app.post("/predict")
# Rate Limiting
@limiter.limit(config.RATE_LIMIT)
def predict(request: Request, file: UploadFile = File()):
    start = time.perf_counter() # Start Timer
    request_id = uuid.uuid4().hex[:8] # Make UUID for Logging
    data = file.file.read(config.MAX_UPLOAD_BYTES + 1) # Read data
    if len(data) > config.MAX_UPLOAD_BYTES: # Respond with 413 if file is too large
        log.warning("predict id=%s rejected: file too large", request_id)
        return error_response(413, "File is larger than 10 MB.")
    elif len(data) == 0: # Respond with 400 if file is empty
        log.warning("predict id=%s rejected: empty file", request_id)
        return error_response(400, "Empty file.")
    result = pipeline.predict(data) # If file is valid, predict image
    elapsed_ms = (time.perf_counter() - start) * 1000 # Stop Timer
    # Log prediction
    log.info("predict id=%s label=%s crops=%s ms=%d",
             request_id, result["label"], result["crops_analyzed"], elapsed_ms)
    return {"status": "success", **result}

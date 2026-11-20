# Loads the PatchCraft model once and turns image bytes into a prediction.
import io
import math
import threading

import numpy as np
from ai_edge_litert.interpreter import Interpreter
from PIL import Image

from app import config, np_pipeline


# Errors. main.py reads status_code and message to build the response.
class PipelineError(Exception):
    status_code = 500

    def __init__(self, message):
        super().__init__(message)
        self.message = message


class InvalidImage(PipelineError):
    status_code = 400


class ImageTooSmall(PipelineError):
    status_code = 400


class ImageTooLarge(PipelineError):
    status_code = 400


class ServerBusy(PipelineError):
    status_code = 503


class ModelNotLoaded(PipelineError):
    status_code = 503


# Validate the upload before any model work. Raises a PipelineError if it is bad.
def _validate_image(image_bytes):
    try:
        img = Image.open(io.BytesIO(image_bytes))
        if img.format not in ("JPEG", "PNG"):
            raise InvalidImage("File must be a JPG or PNG image.")

        w, h = img.size
        if min(w, h) < config.MIN_SIDE:
            raise ImageTooSmall(
                f"Image is too small (shortest side must be at least {config.MIN_SIDE} px)."
            )
        if w * h > config.MAX_PIXELS:
            raise ImageTooLarge("Image has too many pixels.")
        if math.ceil(max(w, h) / min(w, h)) > config.MAX_CROPS:
            raise ImageTooLarge("Image shape is too long and thin.")

        img.load()  # forces a full decode, so corrupt files fail here
    except PipelineError:
        raise
    except Image.DecompressionBombError:
        raise ImageTooLarge("Image has too many pixels.")
    except Exception:
        raise InvalidImage("File is not a valid or readable image.")


# Module-level state and the functions main.py will call.
_params = None  # constants for the 30 filters and the SVM (from params.npz)
_cnn = None  # function that runs the LiteRT model: cnn(frt, fpt) -> features
_lock = threading.Lock()  # the LiteRT interpreter is not thread-safe: one prediction at a time


def load_pipeline():
    # Load the model once at startup.
    global _params, _cnn
    for path in (config.CNN_PATH, config.PARAMS_PATH):
        if not path.exists():
            raise PipelineError(f"Missing model file: {path.name}")

    interp = Interpreter(model_path=str(config.CNN_PATH))
    interp.allocate_tensors()
    ins, out = interp.get_input_details(), interp.get_output_details()[0]

    def cnn(frt, fpt):
        interp.set_tensor(ins[0]["index"], frt)
        interp.set_tensor(ins[1]["index"], fpt)
        interp.invoke()
        return interp.get_tensor(out["index"])

    _params = dict(np.load(config.PARAMS_PATH))
    _cnn = cnn


def predict(image_bytes):
    if _cnn is None:
        raise ModelNotLoaded("Model has not been loaded")
    # Validate outside the lock: bad uploads fail fast and never wait in the queue
    _validate_image(image_bytes)
    if not _lock.acquire(timeout=config.REQUEST_TIMEOUT_SECONDS):
        raise ServerBusy("Server busy, try again later")
    try:
        return np_pipeline.classify(image_bytes, _params, _cnn)
    finally:
        _lock.release()


def is_loaded():
    return _cnn is not None

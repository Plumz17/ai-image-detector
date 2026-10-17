# Loads the PatchCraft model once and turns image bytes into a prediction.
import io
import math
import threading

import numpy as np
import torch
from PIL import Image

from app import config
from app.patchcraft_original import ModelInference, preprocess


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


class Detector(ModelInference):
    def __init__(self, feature_extractor_path, svm_path):
        super().__init__(feature_extractor_path, svm_path)
        # put the feature extractor in eval mode
        self.feature_extractor.eval()

    def classify(self, image_bytes):
        # Run the CNN and the SVM once per crop. 1 = fake, 0 = real.
        crops = self.multiple_crop(io.BytesIO(image_bytes))
        votes = []  # Will contain a list of 0/1
        features = []

        with torch.no_grad():
            for crop in crops:
                frt, fpt = preprocess(crop)  # get "rich" and "poor" tensors
                feature = self.feature_extractor(frt.unsqueeze(0), fpt.unsqueeze(0))
                feature = feature.numpy()
                votes.append(int(self.best_clf.predict(feature)[0]))
                features.append(feature)

        # Get the ratio of votes
        ratio = sum(votes) / len(votes)
        if ratio > 0.5:
            label = "fake"
        elif ratio < 0.5:
            label = "real"
        else:
            # Exactly 0.5: break the tie with the average probability over the crops
            probs = [self.best_clf.predict_proba(f) for f in features]
            p = np.mean(probs, axis=0)
            label = "real" if p[0][0] > p[0][1] else "fake"
        return {
            "label": label,
            "crops_analyzed": len(votes),
            "fake_crop_ratio": round(ratio, 4),
        }

    def analyze(self, image_bytes):
        # Validate image
        _validate_image(image_bytes)
        return self.classify(image_bytes)


# Module-level state and the two functions main.py will call.
_detector = None
_lock = threading.Lock()


def load_pipeline():
    # Load the model once at startup.
    global _detector
    for path in (config.FEATURE_EXTRACTOR_PATH, config.SVM_PATH):
        if not path.exists():
            raise PipelineError(f"Missing model file: {path.name}")
    _detector = Detector(config.FEATURE_EXTRACTOR_PATH, config.SVM_PATH)


def predict(image_bytes):
    if _detector is None:
        raise ModelNotLoaded("Model has not been loaded")
    # Validate outside the lock: bad uploads fail fast and never wait in the queue
    _validate_image(image_bytes)
    if not _lock.acquire(timeout=config.REQUEST_TIMEOUT_SECONDS):
        raise ServerBusy("Server busy, try again later")
    try:
        return _detector.classify(image_bytes)
    finally:
        _lock.release()


def is_loaded():
    return _detector is not None
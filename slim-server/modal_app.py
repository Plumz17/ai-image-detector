# Deploy to Modal (run from this folder):  modal deploy modal_app.py   (after `pip install modal` and `modal setup`)
import modal

# Web addresses allowed to call the API from a browser (comma separated). Add the website's URL when it exists.
CORS_ORIGINS = "http://localhost:3000,http://localhost:5173,https://ai-image-detector-web-seven.vercel.app"

# Requests one client may send to /predict (same default as the original backend).
RATE_LIMIT = "10/minute"

image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install_from_requirements("requirements.txt")           # pinned, same versions as the Dockerfile
    .env({"CORS_ORIGINS": CORS_ORIGINS, "RATE_LIMIT": RATE_LIMIT})
    .add_local_dir("app", remote_path="/root/app")          # code + cnn.tflite + params.npz (< 1 MB)
)
app = modal.App("ai-image-detector", image=image)


# Scales to zero when idle (no cost). max_containers=1 keeps the free credit safe from abuse.
@app.function(cpu=1.0, memory=512, max_containers=1, scaledown_window=120, timeout=60)
@modal.asgi_app()
def web():
    from app.main import app as fastapi_app
    return fastapi_app

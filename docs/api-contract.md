# API Contract: AI Image Detector Backend

Version 0.1 (draft, 17 Oct 2026). Owner: Anders (backend).

The web and mobile apps are built against this file. I will only add things (new optional fields, new error codes). If I ever need to rename or remove something, I'll tell both teams first.

Both `backend/` and `slim-server/` follow this contract, so the apps do not need to know which one is running.

Base URL: `http://localhost:8000` when running locally. The deployed URL goes here once hosting is chosen.
Interactive Docs (Swagger UI) is available at `GET /docs`.

---

## GET /health

Checks that the server is running. Good for warm-up pings and the hosting platform's health check.

Response 200:
```json
{"status": "ok", "model_loaded": true}
```

- `status` is always `"ok"` if the server answers at all.
- `model_loaded` is `false` if the server started but the model failed to load. In that case, `/predict` returns 503.

---

## POST /predict

Takes one image and says whether it looks real or AI-generated.

Request: `multipart/form-data`

| Field  | Type | Required | Notes                      |
|--------|------|----------|----------------------------|
| `file` | file | yes      | JPG or PNG, max 10 MB      |

Example:
```
curl.exe -F "file=@photo.jpg" http://localhost:8000/predict
```

What the server checks:
- The file type is read from the file's actual bytes, not from the extension or the `Content-Type` header.
- The shortest side must be at least 64 px.
- Images with too many pixels, or a very extreme shape (for example a very long thin strip), are rejected with 400.
- Images are processed in memory and never saved.

Response 200:
```json
{
  "status": "success",
  "label": "fake",
  "crops_analyzed": 2,
  "fake_crop_ratio": 1.0
}
```

| Field             | Type   | Meaning                                                                 |
|-------------------|--------|-------------------------------------------------------------------------|
| `status`          | string | Always `"success"` here.                                                |
| `label`           | string | `"real"` or `"fake"` (fake means AI-generated).                         |
| `crops_analyzed`  | int    | How many square crops the image was cut into. 1 for a square image.     |
| `fake_crop_ratio` | float  | Share of crops judged fake, from 0.0 to 1.0. `label` is `"fake"` if this is above 0.5. |

More optional fields may be added later (for example `confidence` or `processing_ms`). Your code should ignore any field it doesn't know.

`fake_crop_ratio` is a vote share, not a probability, so please don't show it to users as "X% chance of AI".

---

## Errors

Every error on every endpoint looks like this:

```json
{"status": "error", "message": "Explanation of what went wrong"}
```

| Status | Name                  | When                                                                                                                       |
|--------|-----------------------|----------------------------------------------------------------------------------------------------------------------------|
| 400    | Bad Request           | No `file` field, not a JPG/PNG, corrupt image, shortest side under 64 px, or the image is too big or too oddly shaped        |
| 413    | Content Too Large     | File is bigger than 10 MB                                                                                                  |
| 429    | Too Many Requests     | One client sent too many requests (rate limit). Wait a bit and try again.                                                  |
| 500    | Internal Server Error | Something unexpected broke on the server                                                                                   |
| 503    | Service Unavailable   | The model isn't loaded, or the server was too busy and the request timed out. Try again later.                             |

Decide what to do from the HTTP status code. The `message` text is only for showing to the user and may be reworded later.

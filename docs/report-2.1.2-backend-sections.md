## 2.1.1 Base Model

We did not create the detection model. The product uses PatchCraft, an AI-generated image detector that was implemented and trained in a separate thesis by a previous student. We received her code and trained weights and wrapped them in our backend. This section only gives an overview of how the model works, so that the rest of the report can be understood. The training and the model's own results are in her thesis.

PatchCraft does not look at what is in a picture. It looks at the texture, because AI generators tend to leave different pixel patterns than cameras do. The model works in four steps:

1. **Cropping.** The image is cut into square crops, and every crop is processed on its own.
2. **Smash and reconstruct.** Each crop is split into small 32x32 tiles, and the tiles are sorted by how much the neighbouring pixels differ. The busiest half is shuffled into one "rich texture" image, and the calmest half into one "poor texture" image. This removes the content of the picture and keeps only the texture. The shuffling is random, so a borderline image can get different results on different runs.
3. **Feature extraction.** Thirty high-pass filters bring out the fine pixel noise in both texture images. A small convolutional neural network (CNN) then turns the pair into 32 numbers that describe the texture.
4. **Classification.** A support vector machine (SVM) with an RBF kernel decides real or fake for the crop. The crops then vote, and the image is labelled fake if more than half of its crops are fake.

[Figure: PatchCraft pipeline (smash and reconstruct, filters, CNN, SVM, vote). Reuse the model figure from the thesis, with credit, or draw a simple one.]

The model was trained on images from six generators (ProGAN, ADM, Stable Diffusion, DALL-E 3, Midjourney 6 and SDXL), with real photos from the LSUN dataset. In the model, 1 means fake and 0 means real.

Two things matter for our backend. First, the CNN contains batch normalisation layers, so it must run in evaluation mode and without gradients. Otherwise almost every image comes out as fake. Second, the original script rounds the vote down, so a vote of 0.67 becomes 0. We did not copy this. Our backend uses the rule "fake if the mean vote is above 0.5", and it only uses the author's tie-break at exactly 0.5.

## Add to the end of 2.1.2.1 (after the two-server list)

The backend is split into layers, and each layer has one job. This is called separation of concerns. The web and mobile apps only handle the user interface, and the backend only handles detection. They talk through one written agreement, the API contract, so the apps do not depend on how the backend works inside. Inside the backend, `main.py` handles HTTP (endpoints, rate limit, CORS, logging and error responses), `pipeline.py` handles the processing (image checks, cropping, the model lock and the voting rule), `config.py` keeps the limits and settings in one place, and the thesis author's model code in `patchcraft_original.py` is never edited. Because of this split, we could build the slim server by replacing only the model layer, and the apps did not need any changes.

## 2.1.2.2 Endpoints

The backend has two endpoints that the apps use, and one extra page for developers. All of them are defined in `main.py`.

[Table 1: API endpoints]

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Checks that the server is running and that the model is loaded. |
| POST | `/predict` | Takes one image and returns the verdict. |
| GET | `/docs` | Interactive Swagger page that FastAPI generates from the code. |

**GET /health.** The apps can call this to wake up the server or to check that it is alive. It returns `{"status": "ok", "model_loaded": true}`. The field `model_loaded` is `false` if the server started but the model failed to load. In that case `/predict` returns 503.

**POST /predict.** The request is `multipart/form-data` with one field named `file`. The file must be a JPG or PNG of at most 10 MB. A successful response looks like this:

```json
{"status": "success", "label": "fake", "crops_analyzed": 2, "fake_crop_ratio": 1.0}
```

| Field | Meaning |
|---|---|
| `status` | Always `"success"` for a valid response. |
| `label` | `"real"` or `"fake"`. Fake means AI-generated. |
| `crops_analyzed` | How many square crops the image was cut into. A square image gives 1. |
| `fake_crop_ratio` | Share of crops judged fake, from 0.0 to 1.0. The label is `"fake"` if this is above 0.5. |

`fake_crop_ratio` is a vote share and not a probability. The apps must not show it to users as "X% chance of AI". The apps should also ignore fields they do not know, because we may add optional fields later.

[Figure 2: Screenshot of the Swagger page at `/docs` showing both endpoints]

## 2.1.2.3 Input Validation

Every upload is checked before it reaches the model. The file type is read from the real bytes of the file, not from its extension or its `Content-Type` header, so renaming a text file to `.png` does not work. These checks happen before the model lock (see 2.1.2.5), so a bad upload is rejected at once and never waits in the queue.

[Table 2: Validation rules and responses]

| Case | Status | Message |
|---|---|---|
| Missing or wrong `file` field | 400 | Missing or invalid 'file' field. |
| Empty file | 400 | Empty file. |
| Not a readable image | 400 | File is not a valid or readable image. |
| Not a JPG or PNG (for example a GIF) | 400 | File must be a JPG or PNG image. |
| Shortest side under 64 px | 400 | Image is too small (shortest side must be at least 64 px). |
| More than 25 million pixels | 400 | Image has too many pixels. |
| Very long and thin image (side ratio above 8) | 400 | Image shape is too long and thin. |
| Larger than 10 MB | 413 | File is larger than 10 MB. |

The limits exist for different reasons. The 64 px minimum is there because the model needs enough pixels to cut tiles from. The pixel limit and the 10 MB limit protect the server's memory and processing time. The shape limit stops very thin strips from producing a large number of crops. The server also analyzes at most 8 crops per image.

All of these cases are tested automatically by the Test 9 suite in Chapter 3 (`evaluation/tests/test_limits.py`).

## 2.1.2.4 Error Handling

Every error on every endpoint uses the same JSON format, so the apps only need one error handler:

```json
{"status": "error", "message": "Explanation of what went wrong"}
```

FastAPI and the libraries we use would normally return errors in their own formats, for example a 422 with a long list of details for a missing field. To keep one format, `main.py` registers a handler for each kind of failure and turns it into our format:

- **Our own errors.** The pipeline raises its own error classes (for example a too small image or a busy server). Each class carries a status code and a message, and one handler in `main.py` converts it to the response. This keeps the pipeline free of any HTTP code.
- **Missing field.** FastAPI's own validation error is changed from 422 to 400 with a fixed message.
- **Unknown URL or wrong method.** These return 404 or 405 in our format.
- **Rate limit.** The library's default response would break the contract, so we replace it with our own 429 response.
- **Anything unexpected.** The full error is written to the log, but the client only gets a short "Internal server error." message with status 500. The traceback is never sent to the client. The predict function also catches unexpected errors itself, so even a 500 response still carries the CORS headers and the browser can read it.

[Table 3: Status codes the apps can receive]

| Status | Meaning | What the app should do |
|---|---|---|
| 200 | Prediction succeeded. | Show the label. |
| 400 | The input is wrong. | Tell the user to pick another image. |
| 413 | The file is too large. | Tell the user the 10 MB limit. |
| 429 | Too many requests. | Ask the user to wait and try again. |
| 500 | Unexpected server error. | Show a general error message. |
| 503 | Model not loaded, or the server was too busy. | Ask the user to try again later. |

The apps should decide what to do from the status code. The message text is meant for display and may be reworded later.

## 2.1.2.5 Concurrency, Rate Limit and CORS

**Concurrency.** The model is loaded once at startup and shared by all requests. The LiteRT interpreter is not thread-safe, so a lock lets only one prediction run at a time in each process. A request that cannot get the lock within 30 seconds (`REQUEST_TIMEOUT_SECONDS`) receives a 503. The two endpoints are written differently on purpose. `/predict` is a plain function, so FastAPI runs it in a thread pool and it does not block the whole server. `/health` is an `async` function, so it still answers quickly while a prediction is running. We found that `/health` froze under load before we made it `async`. More traffic is handled by running more processes or copies of the server, and not by removing the lock.

**Rate limit.** The server uses the library `slowapi` to allow 10 requests per minute for each client by default. The value can be changed with the `RATE_LIMIT` environment variable. Hosting platforms put a proxy in front of the server, so every request would look like it comes from the same address and all users would share one limit. To avoid this, the server reads the client address from the `X-Forwarded-For` header and uses the last entry, which is the address the platform's proxy saw, so a client cannot fake it by sending its own header. The counters are kept in memory, which is fine for a single container. With several copies of the server, each copy would count on its own.

**CORS.** Browsers block a website from calling an API on another address unless the API allows it. This rule is called CORS (cross-origin resource sharing). The server only allows the websites listed in the `CORS_ORIGINS` environment variable, and only the GET and POST methods. By default the list holds only local development addresses (`localhost:3000` and `localhost:5173`). The deployment adds the address of the web app. The mobile app does not need CORS, because the rule only applies to browsers.

**Logging.** For each prediction the server logs a short request id, the label, the number of crops and the time in milliseconds. It never logs the image or its content. The log level is set with the `LOG_LEVEL` variable.

## 3.5.2 Web App Deployment

The web app is a static site built with Vite. It has no server of its own. After `npm run build`, Vite produces plain HTML, CSS and JavaScript files in the `dist/` folder, and any static host can serve them. We host the web app on Vercel, and it is available at https://ai-image-detector-web-seven.vercel.app/. The code is in the `web/` folder of the GitHub repository (https://github.com/Plumz17/ai-image-detector.git), and Vercel runs the build command and serves the files from `dist/`.

[Figure: Screenshot of the deployed web app at the Vercel address]

The web app finds the backend through one setting, `VITE_API_URL`, which is read in `src/api.js`. When the setting is missing, the app uses `http://localhost:8000`, the address used during development. In the deployed app, the setting holds the address of the deployed API. Vite puts this value into the JavaScript at build time, so the web app must be built again after the API address changes. All calls to the backend go through `api.js`, so no other file has to change.

The web app has more than one page, and React switches between them in the browser. If a user opens a page such as `/about` directly or reloads the page, the host looks for a file with that name and finds nothing. The file `vercel.json` fixes this with a rewrite rule that sends every path to `index.html`, and React then shows the right page. We added this rule after the About page returned an error on Vercel.

A browser only lets the web app call the API if the API allows the web app's address, so the Vercel address is in the `CORS_ORIGINS` list of the deployed backend (see 2.1.2.5). If the web app moves to a new address, that list must be updated, or the browser will block every request. In short, the deployment order is: deploy the backend and note its address, set `VITE_API_URL` in Vercel to that address, add the web app's address to `CORS_ORIGINS` and deploy the backend again, and then deploy the web app and test it with an upload.

[Table: Deployment settings. Columns: Setting, Where it is set, Value. Rows: `VITE_API_URL` (Vercel), `CORS_ORIGINS` (backend host), `RATE_LIMIT` (backend host).]

Please check before submitting: I don't know your Vercel settings, so confirm that Vercel builds from the GitHub repo (root directory `web/`) and that `VITE_API_URL` is set there. Add the real API address if the report should show it. Ask the supervisor about the patent question before putting the links in the final report.

## 2.1.4 changes (items 3, 4 and 5 only)

Replace item 3's first paragraph with:

The frontend communicates with the backend service to process uploaded images. It sends each image to the `/predict` endpoint described in Section 2.1.2.2.

Item 3's five-step interaction list stays as it is.

Replace item 4 with:

The frontend is designed to provide feedback during the image detection process. Loading indicators help communicate that the image is being analyzed, and error messages tell the user what went wrong when an upload or prediction request cannot be processed. The errors the backend can return are described in Section 2.1.2.4.

Replace item 5 with:

The initial development stage produced a React-based demonstration application with the image upload page and result display. After that, frontend development continued with further UI/UX revisions, integration and testing. The deployment of the web app is described in Section 3.5.2.

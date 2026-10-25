// The only file that talks to the backend.
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Sends one image to POST /predict.
// Returns {status, ms, data}: the HTTP status (null if there was no answer), the time, and the JSON body.
export async function predictImage(file) {
  const body = new FormData();
  body.append("file", file); // the field name must be "file"

  const started = performance.now();
  try {
    // Do not set Content-Type by hand: the browser adds it, including the multipart boundary.
    const response = await fetch(`${API_URL}/predict`, { method: "POST", body });
    const text = await response.text();
    let data;
    try {
      data = JSON.parse(text);
    } catch {
      data = text;
    }
    return { status: response.status, ms: Math.round(performance.now() - started), data };
  } catch {
    return {
      status: null,
      ms: Math.round(performance.now() - started),
      data: `No answer from ${API_URL}. Is the backend running, and does its CORS_ORIGINS allow this page?`,
    };
  }
}

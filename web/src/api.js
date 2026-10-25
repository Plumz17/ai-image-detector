// The only file that talks to the backend. See docs/api-contract.md.
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Same limit as the backend (10 MB), checked here too so the user gets a quick message.
export const MAX_UPLOAD_BYTES = 10 * 1024 * 1024;

// Sends one image to POST /predict.
// Returns {label, crops_analyzed, fake_crop_ratio}, or throws an Error with a message to show.
export async function predictImage(file) {
  const body = new FormData();
  body.append("file", file); // the field name must be "file"

  let response;
  try {
    // Do not set Content-Type by hand: the browser adds it, including the multipart boundary.
    response = await fetch(`${API_URL}/predict`, { method: "POST", body });
  } catch {
    throw new Error("Cannot reach the server. Check that the backend is running.");
  }

  const data = await response.json().catch(() => null);
  if (!response.ok || !data || data.status !== "success") {
    // Every backend error looks like {"status": "error", "message": "..."}
    throw new Error(data?.message || "Something went wrong. Please try again.");
  }
  return data;
}

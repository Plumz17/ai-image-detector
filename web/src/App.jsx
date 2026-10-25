import { useState } from "react";
import { predictImage } from "./api.js";

export default function App() {
  const [previewUrl, setPreviewUrl] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null); // {status, ms, data} from api.js

  // Called when a file is dropped or chosen: show a preview, send it, keep the answer
  async function handleFile(file) {
    if (!file) return;
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setPreviewUrl(URL.createObjectURL(file));
    setResult(null);
    setLoading(true);
    setResult(await predictImage(file));
    setLoading(false);
  }

  function handleDrop(e) {
    e.preventDefault(); // otherwise the browser opens the image
    setDragging(false);
    handleFile(e.dataTransfer.files[0]);
  }

  // What to show for the answer
  let summary = "";
  let summaryClass = "";
  if (result) {
    const { status, data } = result;
    if (status !== null && status < 400 && data.status === "success") {
      summary = `${data.label.toUpperCase()} (${data.crops_analyzed} crop(s) analyzed, fake_crop_ratio ${data.fake_crop_ratio})`;
      summaryClass = data.label;
    } else {
      summary = (data && data.message) || (typeof data === "string" ? data : "Request failed");
      summaryClass = "bad";
    }
  }

  return (
    <main>
      <h1>AI Image Detector</h1>

      <label
        className={dragging ? "drop-zone over" : "drop-zone"}
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
      >
        <span>Drag and drop an image here, or click to choose one</span>
        {previewUrl && <img src={previewUrl} alt="Selected upload" />}
        <input
          type="file"
          accept="image/jpeg,image/png"
          hidden
          onChange={(e) => {
            handleFile(e.target.files[0]);
            e.target.value = ""; // so choosing the same file again still counts as a change
          }}
        />
      </label>

      {loading && <p>Analyzing...</p>}

      {result && (
        <section>
          <p className={`summary ${summaryClass}`}>{summary}</p>
          <p className="small">
            {result.status === null ? "no response" : `HTTP ${result.status}`}, {result.ms} ms
          </p>
          <pre>{typeof result.data === "string" ? result.data : JSON.stringify(result.data, null, 2)}</pre>
        </section>
      )}
    </main>
  );
}

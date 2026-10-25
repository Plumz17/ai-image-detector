import { useEffect, useState } from "react";
import { predictImage, MAX_UPLOAD_BYTES } from "./api.js";
import UploadForm from "./components/UploadForm.jsx";
import ResultCard from "./components/ResultCard.jsx";

// status is one of: "idle", "loading", "done", "error"
export default function App() {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [status, setStatus] = useState("idle");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  // Free the preview URL when it is replaced or the page closes
  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl);
    };
  }, [previewUrl]);

  function handleFileChosen(chosen) {
    setResult(null);
    setError("");
    if (chosen && chosen.size > MAX_UPLOAD_BYTES) {
      setFile(null);
      setPreviewUrl(null);
      setStatus("error");
      setError("The file is larger than 10 MB.");
      return;
    }
    setFile(chosen);
    setPreviewUrl(chosen ? URL.createObjectURL(chosen) : null);
    setStatus("idle");
  }

  async function handleAnalyze() {
    if (!file) return;
    setStatus("loading");
    setError("");
    try {
      setResult(await predictImage(file));
      setStatus("done");
    } catch (err) {
      setError(err.message);
      setStatus("error");
    }
  }

  return (
    <main className="page">
      <h1>AI Image Detector</h1>
      <p className="subtitle">Upload a JPG or PNG image to see if it looks AI-generated.</p>

      <UploadForm
        previewUrl={previewUrl}
        canAnalyze={Boolean(file) && status !== "loading"}
        loading={status === "loading"}
        onFileChosen={handleFileChosen}
        onAnalyze={handleAnalyze}
      />

      {status === "error" && <p className="error">{error}</p>}
      {status === "done" && result && <ResultCard result={result} />}
    </main>
  );
}

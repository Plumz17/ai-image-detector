import { useState } from "react";
import { predictImage } from "./api.js";
import Navbar from "./components/Navbar.jsx";
import About from "./pages/About.jsx";

function Home() {
  const [previewUrl, setPreviewUrl] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  async function handleFile(file) {
    if (!file) return;

    if (!["image/jpeg", "image/png"].includes(file.type)) {
      setResult({
        status: 400,
        ms: 0,
        data: { message: "Please choose a JPG or PNG image." },
      });
      return;
    }

    if (previewUrl) URL.revokeObjectURL(previewUrl);

    setPreviewUrl(URL.createObjectURL(file));
    setResult(null);
    setLoading(true);

    try {
      setResult(await predictImage(file));
    } finally {
      setLoading(false);
    }
  }

  function handleDrop(e) {
    e.preventDefault();
    setDragging(false);
    handleFile(e.dataTransfer.files[0]);
  }

  let summary = "";
  let summaryClass = "";

  if (result) {
    const { status, data } = result;

    if (status !== null && status < 400 && data.status === "success") {
      summary = `${data.label.toUpperCase()} (${data.crops_analyzed} crop(s) analyzed, fake_crop_ratio ${data.fake_crop_ratio})`;
      summaryClass = data.label;
    } else {
      summary =
        (data && data.message) ||
        (typeof data === "string" ? data : "Request failed");
      summaryClass = "bad";
    }
  }

  return (
    <main className="home-page">
      <section className="home-intro">
        <p className="eyebrow">DIGITAL AUTHENTICITY CHECK</p>
        <h1>
          AI Image <span>Detector</span>
        </h1>
        <p className="home-subtitle">
          See what may be behind the pixels. Upload an image and let our
          model analyze it.
        </p>
      </section>

      <label
        className={dragging ? "drop-zone over" : "drop-zone"}
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
      >
        <span className="upload-icon">↑</span>
        <strong>Drop your image here</strong>
        <span className="drop-copy">or click to browse your files</span>
        <span className="file-hint">JPG or PNG · Up to 10 MB</span>

        {previewUrl && <img src={previewUrl} alt="Selected upload" />}

        <input
          type="file"
          accept="image/jpeg,image/png"
          hidden
          onChange={(e) => {
            handleFile(e.target.files[0]);
            e.target.value = "";
          }}
        />
      </label>

      {loading && (
        <div className="loading-state">
          <span className="spinner" />
          Analyzing image…
        </div>
      )}

      {result && (
        <section className="result-panel">
          <p className={`summary ${summaryClass}`}>{summary}</p>
          <p className="small">
            {result.status === null ? "No response" : `HTTP ${result.status}`}
            {" · "}
            {result.ms} ms
          </p>
          <details>
            <summary>Technical response</summary>
            <pre>
              {typeof result.data === "string"
                ? result.data
                : JSON.stringify(result.data, null, 2)}
            </pre>
          </details>
        </section>
      )}

      <p className="home-disclaimer">
        This result is an estimate, not a guarantee. Use additional context
        when evaluating an image’s authenticity.
      </p>
    </main>
  );
}

export default function App() {
  const isAbout =
    window.location.pathname.replace(/\/+$/, "") === "/about";

  return (
    <div className="app-shell">
      <Navbar active={isAbout ? "about" : "home"} />
      {isAbout ? <About /> : <Home />}
    </div>
  );
}

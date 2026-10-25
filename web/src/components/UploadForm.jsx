// File picker, image preview and the Analyze button. It keeps no state of its own.
export default function UploadForm({ previewUrl, canAnalyze, loading, onFileChosen, onAnalyze }) {
  return (
    <section className="card">
      <input
        type="file"
        accept="image/jpeg,image/png"
        onChange={(e) => onFileChosen(e.target.files[0] || null)}
      />
      {previewUrl && <img className="preview" src={previewUrl} alt="Selected upload" />}
      <button onClick={onAnalyze} disabled={!canAnalyze}>
        {loading ? "Analyzing..." : "Analyze"}
      </button>
    </section>
  );
}

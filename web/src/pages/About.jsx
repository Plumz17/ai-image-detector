const steps = [
  {
    number: "01",
    title: "Upload",
    text: "Choose a supported image and submit it for analysis.",
  },
  {
    number: "02",
    title: "Analyze",
    text: "The detector examines image texture patterns through the PatchCraft feature-extraction pipeline.",
  },
  {
    number: "03",
    title: "Get Results",
    text: "The classifier aggregates crop-level predictions and returns an estimate: real or AI-generated.",
  },
];

export default function About() {
  return (
    <main className="about-page">
      <section className="about-hero">
        <p className="eyebrow">HOW IT WORKS</p>
        <h1>
          Behind the <span>Detector</span>
        </h1>
        <p className="about-lead">
          Understand the technology behind identifying AI-generated images
          and explore how our tool helps distinguish artificial creations
          from real-world visuals.
        </p>
      </section>

      <section className="about-content">
        <div className="content-label">
          <h2>What does it do?</h2>
        </div>

        <div className="content-body">
          <p>
            Our AI Image Detector analyzes uploaded images to estimate
            whether they were created using generative AI or captured
            in the real world. It uses <strong>PatchCraft</strong>, a
            method that focuses on fine-grained image texture patterns,
            to provide an additional signal when assessing digital content.
          </p>
        </div>

        <div className="content-label">
          <h2>How does it work?</h2>
        </div>

        <div className="content-body steps">
          {steps.map((step) => (
            <article className="step" key={step.number}>
              <span className="step-number">{step.number}</span>
              <div>
                <h3>{step.title}</h3>
                <p>{step.text}</p>
              </div>
            </article>
          ))}
        </div>

        <div className="content-label">
          <h2>Inside the model</h2>
        </div>

        <div className="content-body">
          <p>
            The pipeline creates texture-rich and texture-poor patch
            reconstructions, applies high-pass filters, and extracts
            features with a convolutional neural network. A support
            vector machine (SVM) then classifies the extracted features.
            Images are evaluated using multiple crops, with their
            predictions combined into a final label.
          </p>

          <div className="model-tags">
            <span>PatchCraft</span>
            <span>High-pass filters</span>
            <span>CNN features</span>
            <span>SVM classifier</span>
            <span>Multi-crop inference</span>
          </div>
        </div>
      </section>

      <aside className="disclaimer">
        <div className="disclaimer-heading">
          <span className="warning-icon">!</span>
          <h2>Important Disclaimer</h2>
        </div>
        <p>
          Predictions are estimates, not guarantees. Detection can be
          affected by compression, image processing, and the types of
          images the model has encountered. Always consider additional
          context when evaluating an image’s authenticity.
        </p>
      </aside>

      <footer className="about-footer">
        AI Image Detector <span>·</span> A tool for image authenticity assessment
      </footer>
    </main>
  );
}

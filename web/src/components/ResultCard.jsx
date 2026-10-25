// Shows the answer from /predict.
// fake_crop_ratio is the share of image sections (crops) that voted fake. It is NOT a probability,
// so we show it as "x of y sections" and never as a percentage. See docs/api-contract.md.
export default function ResultCard({ result }) {
  const isFake = result.label === "fake";
  const fakeCrops = Math.round(result.fake_crop_ratio * result.crops_analyzed);

  return (
    <section className={`card result ${isFake ? "fake" : "real"}`}>
      <h2>{isFake ? "Likely AI-generated" : "Likely real"}</h2>
      {result.crops_analyzed > 1 && (
        <p>
          {fakeCrops} of {result.crops_analyzed} sections of the image looked AI-generated.
        </p>
      )}
      <p className="note">
        This result can be wrong, especially for compressed images such as JPEG photos or images
        downloaded from the web.
      </p>
    </section>
  );
}

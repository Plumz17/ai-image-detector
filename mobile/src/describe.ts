// Same sentences as the web app's describeResult (web/src/App.jsx), so both apps say the same thing.
export function describeResult(isFake: boolean, total: number, flagged: number) {
  const headline = isFake ? 'This image is likely AI-generated.' : 'This image is likely a real photo.';
  let explanation: string;
  if (total === 1) {
    explanation = isFake
      ? 'The detector studied the fine pixel texture of the image and found patterns that are typical of AI-generated images.'
      : 'The detector studied the fine pixel texture of the image and found patterns that are typical of real camera photos.';
  } else if (flagged === total) {
    explanation = `The image was checked in ${total} parts, and all of them looked AI-generated.`;
  } else if (flagged === 0) {
    explanation = `The image was checked in ${total} parts, and none of them looked AI-generated.`;
  } else if (flagged * 2 === total) {
    explanation = `The image was checked in ${total} parts, and ${flagged} of them looked AI-generated, exactly half. In a tie, the detector decides by its average confidence across the parts.`;
  } else {
    explanation = `The image was checked in ${total} parts, and ${flagged} of them looked AI-generated, which is ${isFake ? 'more' : 'fewer'} than half.`;
  }
  return { headline, explanation };
}

export const DISCLAIMER = 'This result is an estimate, not a guarantee. Use additional context when evaluating an image’s authenticity.';
export const JPEG_NOTE = 'Note: photos saved as JPEG, or sent through chat apps, are harder to judge, so this result may be less reliable.';
export const SLOW_NOTE = 'The server may be starting up. This can take up to 30 seconds.';

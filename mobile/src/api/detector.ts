import { predict, ApiError } from '../api';
import type { DetectionResult, UploadImage } from '../types';

// Shown to the user, chosen by HTTP status (0 = server unreachable). 400 uses the server's own text, which says what is wrong with the file.
const MESSAGES: Record<number, string> = {
  0: 'No connection. Check your internet and try again.',
  413: 'The photo is too large (maximum 10 MB).',
  429: 'Please wait a moment and try again.',
  503: 'The server is busy. Try again shortly.',
};

export async function detectImage(image: UploadImage, signal?: AbortSignal): Promise<DetectionResult> {
  try {
    const r = await predict(image.uri, image.mimeType, image.size ?? undefined, signal);
    return { verdict: r.label === 'fake' ? 'ai' : 'real', confidence: null, aiProbability: null, explanation: null, model: null, isDemo: false };
  } catch (e) {
    if (!(e instanceof ApiError)) throw e;
    throw new Error(e.status === 400 ? e.message : MESSAGES[e.status] ?? 'Something went wrong. Please try again.');
  }
}

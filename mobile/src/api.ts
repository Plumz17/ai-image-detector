import { File } from 'expo-file-system';

// API layer for the backend described in docs/api-contract.md. The UI should only call these functions.
const BASE_URL = (process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:8000').replace(/\/$/, '');
const MOCK = process.env.EXPO_PUBLIC_API_MOCK === '1';
const MAX_BYTES = 10 * 1024 * 1024;
const TIMEOUT_MS = 60_000; // long enough for a sleeping hosted server to wake up

export type PredictResult = {
  label: 'real' | 'fake'; // fake = AI-generated
  cropsAnalyzed: number;
  fakeCropRatio: number; // a vote share, not a probability: don't show it as "% chance"
};

export class ApiError extends Error {
  // status is the HTTP code, or 0 when the server could not be reached
  detail?: string; // the underlying error text, for debugging
  constructor(public status: number, message: string) {
    super(message);
  }
}

async function request(path: string, init?: RequestInit) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), TIMEOUT_MS);
  try {
    const res = await fetch(BASE_URL + path, { ...init, signal: ctrl.signal });
    const body = await res.json().catch(() => null);
    if (!res.ok) {
      // Decide by status code; the message text is only for display (per the contract)
      throw new ApiError(res.status, body?.message ?? `Server error (${res.status}).`);
    }
    return body;
  } catch (e) {
    if (e instanceof ApiError) throw e;
    const err = new ApiError(0, 'Could not reach the server. Check your connection and try again.');
    err.detail = String(e);
    throw err;
  } finally {
    clearTimeout(timer);
  }
}

export async function health(): Promise<{ modelLoaded: boolean }> {
  if (MOCK) return { modelLoaded: true };
  const body = await request('/health');
  return { modelLoaded: !!body.model_loaded };
}

// mimeType is kept for callers but no longer needed: the file's type is read from the file itself.
// sizeBytes: pass the picker's fileSize if you have it, so oversized files fail before uploading.
export async function predict(uri: string, mimeType = 'image/jpeg', sizeBytes?: number): Promise<PredictResult> {
  if (sizeBytes !== undefined && sizeBytes > MAX_BYTES) {
    throw new ApiError(413, 'File is larger than 10 MB.');
  }
  if (MOCK) return mockPredict(uri);

  const form = new FormData();
  // Expo's fetch (the global fetch since SDK 53+) needs a real file object (a Blob), not React Native's old {uri, name, type}.
  // The bytes are sent unchanged: the model reads pixel texture, so never resize or recompress.
  form.append('file', new File(uri) as any);
  const body = await request('/predict', { method: 'POST', body: form });
  return {
    label: body.label,
    cropsAnalyzed: body.crops_analyzed,
    fakeCropRatio: body.fake_crop_ratio,
  };
}

// Mock mode: a uri containing "error" fails with 400, one containing "fake" returns fake, anything else real.
async function mockPredict(uri: string): Promise<PredictResult> {
  await new Promise((r) => setTimeout(r, 800));
  if (uri.includes('error')) throw new ApiError(400, 'File is not a valid or readable image.');
  const fake = uri.includes('fake');
  return { label: fake ? 'fake' : 'real', cropsAnalyzed: 1, fakeCropRatio: fake ? 1 : 0 };
}

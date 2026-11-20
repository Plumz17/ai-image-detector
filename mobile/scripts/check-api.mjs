// Run against a live backend: EXPO_PUBLIC_API_URL=http://localhost:8000 node scripts/check-api.mjs
// Uploads one fake and one real sample with plain fetch and checks the labels from the contract.
import { readFileSync } from 'node:fs';

const base = process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:8000';
const dir = new URL('../../backend/tests/sample_images/', import.meta.url);

async function label(name) {
  const form = new FormData();
  form.append('file', new Blob([readFileSync(new URL(name, dir))], { type: 'image/png' }), name);
  const res = await fetch(base + '/predict', { method: 'POST', body: form });
  return (await res.json()).label;
}

(async () => {
  const h = await (await fetch(base + '/health')).json();
  if (!h.model_loaded) throw new Error('model not loaded');
  const ai = await label('ai (1).png');
  const real = await label('no_ai (1).png');
  if (ai !== 'fake' || real !== 'real') throw new Error(`unexpected labels: ai=${ai} no_ai=${real}`);
  console.log('OK', { ai, real });
})();

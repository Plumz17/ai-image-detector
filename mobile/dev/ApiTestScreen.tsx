// Optional debug screen (not used by the app): checks src/api.ts end to end on a real phone. To try it, make App.tsx contain:
//   export { default } from "./dev/ApiTestScreen";
import { useState } from 'react';
import { ActivityIndicator, Button, Image, ScrollView, StyleSheet, Text, View } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { ApiError, health, predict, type PredictResult } from '../src/api';

export default function App() {
  const [uri, setUri] = useState<string>();
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<PredictResult>();
  const [error, setError] = useState<string>();
  const [note, setNote] = useState<string>();

  const run = async (p: Promise<ImagePicker.ImagePickerResult>) => {
    const r = await p;
    if (r.canceled) return;
    const a = r.assets[0];
    setUri(a.uri); setResult(undefined); setError(undefined); setBusy(true);
    const t = Date.now();
    setNote(`${a.width}x${a.height}, ${a.mimeType ?? '?'}, ${a.fileSize ? (a.fileSize / 1e6).toFixed(2) + ' MB' : 'size unknown'}`);
    try {
      setResult(await predict(a.uri, a.mimeType ?? 'image/jpeg', a.fileSize));
      setNote((n) => `${n} | ${((Date.now() - t) / 1000).toFixed(1)} s`);
    } catch (e) {
      const secs = ((Date.now() - t) / 1000).toFixed(1);
      setError(e instanceof ApiError ? `Error ${e.status}: ${e.message}${e.detail ? ' | ' + e.detail : ''} (after ${secs} s)` : String(e));
    } finally { setBusy(false); }
  };

  const take = async () => {
    const perm = await ImagePicker.requestCameraPermissionsAsync();
    if (!perm.granted) { setError('Camera permission denied'); return; }
    await run(ImagePicker.launchCameraAsync({ quality: 1, allowsEditing: false }));
  };
  const pick = () => run(ImagePicker.launchImageLibraryAsync({ mediaTypes: ['images'], quality: 1, allowsEditing: false }));
  // Raw fetch (no api.ts) so the real error text is visible
  const raw = async (label: string, url: string) => {
    setError(undefined); setResult(undefined); setNote(`${label}: trying ${url} ...`); setBusy(true);
    const t = Date.now();
    try {
      const c = new AbortController(); const id = setTimeout(() => c.abort(), 20000);
      const r = await fetch(url, { signal: c.signal }); clearTimeout(id);
      const body = (await r.text()).slice(0, 80);
      setNote(`${label}: HTTP ${r.status} in ${((Date.now() - t) / 1000).toFixed(1)} s ${body}`);
    } catch (e) { setError(`${label} failed after ${((Date.now() - t) / 1000).toFixed(1)} s: ${String(e)}`); }
    finally { setBusy(false); }
  };
  const ping = () => raw('Server', (process.env.EXPO_PUBLIC_API_URL ?? '') + '/health');
  const internet = () => raw('Internet', 'https://www.google.com/generate_204');

  return (
    <ScrollView contentContainerStyle={s.c}>
      <Text style={s.h}>API test</Text>
      <Text style={s.small}>{process.env.EXPO_PUBLIC_API_URL ?? 'no EXPO_PUBLIC_API_URL set'}</Text>
      <View style={s.row}><Button title="Internet" onPress={internet} /><Button title="Server" onPress={ping} /><Button title="Take photo" onPress={take} /><Button title="Gallery" onPress={pick} /></View>
      {uri && <Image source={{ uri }} style={s.img} resizeMode="contain" />}
      {busy && <ActivityIndicator size="large" />}
      {note && <Text style={s.small}>{note}</Text>}
      {result && <Text style={s.res}>{result.label === 'fake' ? 'Likely AI-generated' : 'Likely real'}{'\n'}({result.cropsAnalyzed} crop{result.cropsAnalyzed > 1 ? 's' : ''} analysed)</Text>}
      {error && <Text style={s.err}>{error}</Text>}
    </ScrollView>
  );
}
const s = StyleSheet.create({
  c: { padding: 24, paddingTop: 64, gap: 12, alignItems: 'center' },
  h: { fontSize: 24, fontWeight: '600' }, small: { fontSize: 12, color: '#555', textAlign: 'center' },
  row: { flexDirection: 'row', gap: 8 }, img: { width: 280, height: 280, backgroundColor: '#eee' },
  res: { fontSize: 22, fontWeight: '600', textAlign: 'center' }, err: { color: '#b00020', textAlign: 'center' },
});

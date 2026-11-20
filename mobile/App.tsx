import React, { useCallback, useEffect, useRef, useState } from 'react';
import { Alert, BackHandler, Platform, StyleSheet, View } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
import { BottomNav } from './src/components/BottomNav';
import { Glow } from './src/components/UI';
import { Welcome } from './src/screens/Welcome';
import { Home } from './src/screens/Home';
import { Preview } from './src/screens/Preview';
import { Loading } from './src/screens/Loading';
import { Result } from './src/screens/Result';
import { About } from './src/screens/About';
import { Failure } from './src/screens/Failure';
import { config } from './src/config';
import { detectImage } from './src/api/detector';
import { colors } from './src/theme';
import type { DetectionResult, Screen, UploadImage } from './src/types';

function VeriPixel() {
  const [screen, setScreen] = useState<Screen>('welcome');
  const [selected, setSelected] = useState<UploadImage | null>(null);
  const [result, setResult] = useState<DetectionResult | null>(null);
  const [error, setError] = useState('');
  const activeController = useRef<AbortController | null>(null);
  const requestSequence = useRef(0);

  const cancelActive = useCallback(() => {
    requestSequence.current += 1;
    activeController.current?.abort();
    activeController.current = null;
  }, []);

  const reset = useCallback(() => {
    cancelActive();
    setSelected(null); setResult(null); setError(''); setScreen('home');
  }, [cancelActive]);

  const pick = useCallback(async (source: 'library' | 'camera') => {
    try {
      if (source === 'camera') {
        const permission = await ImagePicker.requestCameraPermissionsAsync();
        if (!permission.granted) { Alert.alert('Camera permission', 'Allow camera access to take a picture, or choose a photo from your gallery.'); return; }
      }
      const pickerOptions: ImagePicker.ImagePickerOptions = {
        mediaTypes: ['images'], allowsEditing: false, quality: 1,
        selectionLimit: 1,
      };
      const response = source === 'camera' ? await ImagePicker.launchCameraAsync(pickerOptions) : await ImagePicker.launchImageLibraryAsync(pickerOptions);
      if (response.canceled || response.assets.length === 0) return;
      const asset = response.assets[0];
      const name = asset.fileName || `veripixel-${Date.now()}.jpg`;
      const type = asset.mimeType || (name.toLowerCase().endsWith('.png') ? 'image/png' : 'image/jpeg');
      if (!['image/jpeg','image/png'].includes(type.toLowerCase())) {
        Alert.alert('Unsupported image', 'Please choose a JPG or PNG image. You may need to export HEIC/HEIF photos as JPG.'); return;
      }
      if (typeof asset.fileSize === 'number' && asset.fileSize > config.maxBytes) {
        Alert.alert('Image is too large', 'Please choose an image smaller than 10 MB.'); return;
      }
      cancelActive();setResult(null);setError('');
      setSelected({ uri: asset.uri, name, mimeType: type, size: asset.fileSize, width: asset.width, height: asset.height });
      setScreen('preview');
    } catch (e) {
      Alert.alert('Could not open image', e instanceof Error ? e.message : 'Please try again.');
    }
  }, [cancelActive]);

  const analyze = useCallback(async () => {
    if (!selected) return;
    cancelActive();
    const controller = new AbortController();
    activeController.current = controller;
    const current = requestSequence.current;
    setError('');setResult(null);setScreen('loading');
    try {
      const output = await detectImage(selected, controller.signal);
      if (requestSequence.current === current && !controller.signal.aborted) {setResult(output);setScreen('result');}
    } catch(e) {
      if (requestSequence.current === current && !controller.signal.aborted) {
        setError(e instanceof Error ? e.message : 'The image could not be analyzed.');setScreen('error');
      }
    } finally {
      if (activeController.current === controller)activeController.current = null;
    }
  }, [cancelActive, selected]);

  const toHome = useCallback(() => { reset(); }, [reset]);
  const back = useCallback(() => {
    if (screen === 'loading') { cancelActive(); setScreen('preview'); }
    else if (screen === 'welcome') { setScreen('home'); }
    else if (screen === 'preview' || screen === 'about') { setScreen('home'); }
    else if (screen === 'result' || screen === 'error') { setScreen('preview'); }
    else { return false; }
    return true;
  }, [screen, cancelActive]);

  useEffect(() => {
    if (Platform.OS !== 'android') return;
    const sub = BackHandler.addEventListener('hardwareBackPress', back);
    return () => sub.remove();
  }, [back]);
  useEffect(() => () => { requestSequence.current++; activeController.current?.abort(); }, []);

  const showNav = screen !== 'welcome';
  return <SafeAreaView style={styles.safe} edges={['top','bottom']}>
    <StatusBar style="light"/>
    <Glow />
    <View style={{ flex: 1 }}>
      {screen === 'welcome' && <Welcome onStart={() => setScreen('home')}/>}
      {screen === 'home' && <Home onGallery={() => pick('library')} onCamera={() => pick('camera')}/>}
      {screen === 'preview' && selected && <Preview image={selected} onAnalyze={analyze} onChange={() => pick('library')} onBack={toHome}/>}
      {screen === 'loading' && <Loading onCancel={() => { cancelActive(); setScreen('preview'); }}/>}
      {screen === 'result' && selected && result && <Result image={selected} result={result} onBack={() => setScreen('preview')} onReset={reset}/>}
      {screen === 'about' && <About/>}
      {screen === 'error' && <Failure error={error} onBack={() => setScreen('preview')} onRetry={analyze} onChange={() => pick('library')}/>}
    </View>
    {showNav && <BottomNav active={screen==='about'?'about':'detector'} onDetector={toHome} onAbout={() => { cancelActive(); setScreen('about'); }}/>}
  </SafeAreaView>;
}
export default function App() { return <SafeAreaProvider><VeriPixel/></SafeAreaProvider>; }
const styles = StyleSheet.create({safe:{flex:1,backgroundColor:colors.bg}});

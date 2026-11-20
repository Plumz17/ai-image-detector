import React from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { Body, Card, Caption, Header, PrimaryButton, Tag } from '../components/UI';
import { colors } from '../theme';

export function Home({ onGallery, onCamera }: { onGallery: () => void; onCamera: () => void }) {
  return <Body>
    <Header title="AI Image Detector" />
    <View style={{ marginTop: 24 }}><Tag>DIGITAL AUTHENTICITY CHECK</Tag></View>
    <Text style={styles.head}>Is it real</Text><Text style={styles.headAccent}>or AI?</Text>
    <Caption style={styles.subtitle}>See what may be behind the pixels. Upload an image and let our model analyze it.</Caption>
    <Card style={styles.uploadCard}>
      <View style={styles.uploadIcon}><Text style={{ fontSize: 52, color: colors.purpleLight, marginTop: -6 }}>↑</Text></View>
      <Text style={styles.uploadTitle}>Upload an image</Text>
      <Caption>JPG or PNG · Up to 10 MB</Caption>
      <View style={{ alignSelf: 'stretch', marginTop: 23 }}><PrimaryButton title="Choose Image" icon="→" onPress={onGallery} /></View>
      <Pressable accessibilityRole="button" onPress={onCamera} style={styles.camera}><Text style={styles.cameraText}>◎  Or take a photo</Text></Pressable>
    </Card>
    <View style={styles.note}><View style={styles.noteIcon}><Text style={{ color: colors.cyan, fontSize: 23 }}>◇</Text></View>
      <View style={{ flex: 1 }}><Text style={styles.noteTitle}>Simple and focused</Text><Caption>Your image is analyzed in memory and never stored.</Caption></View>
    </View>
  </Body>;
}
const styles=StyleSheet.create({
  head: { fontSize: 37, fontWeight: '800', color: colors.text, letterSpacing: -1.3, marginTop: 27 },
  headAccent: { fontSize: 41, fontWeight: '800', color: colors.purple, letterSpacing: -1.4, marginTop: -5 },
  subtitle: { fontSize: 15, lineHeight: 23, marginTop: 14, marginBottom: 26, maxWidth: 330 },
  uploadCard: { paddingVertical: 29, paddingHorizontal: 20, alignItems: 'center' },
  uploadIcon: { backgroundColor: '#242148', borderRadius: 50, width: 92, height: 92, justifyContent: 'center', alignItems: 'center', marginBottom: 13 },
  uploadTitle: { fontSize: 20, fontWeight: '700', color: colors.text, marginBottom: 7 },
  camera: { alignItems: 'center', padding: 13, marginTop: 8 },
  cameraText: { color: colors.purpleLight, fontSize: 13.5, fontWeight: '600' },
  note: { backgroundColor: colors.elevated, borderRadius: 17, flexDirection: 'row', gap: 13, alignItems: 'center', padding: 17, marginTop: 20 },
  noteIcon: { width: 33, height: 37, justifyContent: 'center', alignItems: 'center' },
  noteTitle: { color: colors.text, fontWeight: '700', fontSize: 14.5, marginBottom: 4 },
});

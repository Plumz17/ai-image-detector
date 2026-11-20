import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Body, PrimaryButton, Tag } from '../components/UI';
import { colors } from '../theme';

export function Welcome({ onStart }: { onStart: () => void }) {
  return <Body scroll={false} style={styles.body}>
    <View style={styles.hero}>
      <View style={styles.haloLarge}/><View style={styles.haloSmall}/>
      <LinearGradient colors={['#252344', '#172A47']} style={styles.iconBox}>
        <Text style={styles.sparkle}>✦</Text>
      </LinearGradient>
      <View style={styles.floatTop}><Text style={styles.floatGlyph}>✧</Text></View>
      <View style={styles.floatBottom}><Text style={styles.floatGlyph}>◇</Text></View>
    </View>
    <Tag>YOUR IMAGE, VERIFIED</Tag>
    <Text style={styles.title}>See beyond</Text><Text style={styles.titleAccent}>the pixels.</Text>
    <Text style={styles.description}>Explore whether an image may be AI-generated, in just a few taps.</Text>
    <View style={styles.spacer}/>
    <PrimaryButton title="Get Started" icon="→" onPress={onStart}/>
    <Text style={styles.footnote}>Designed for curiosity. Built for clarity.</Text>
  </Body>;
}
const styles = StyleSheet.create({
  body: { paddingTop: 10, paddingBottom: 20 },
  hero: { height: '45%', minHeight: 245, maxHeight: 370, alignItems: 'center', justifyContent: 'center', position: 'relative' },
  haloLarge: { position: 'absolute', width: 290, height: 290, borderRadius: 200, backgroundColor: '#241F4C', borderWidth: 1, borderColor: '#49407D' },
  haloSmall: { position: 'absolute', width: 207, height: 207, borderRadius: 120, backgroundColor: '#322965', opacity: .68 },
  iconBox: { height: 110, width: 110, borderRadius: 30, justifyContent: 'center', alignItems: 'center', borderColor: '#6D66AD', borderWidth: 1 },
  sparkle: { fontSize: 73, color: colors.purpleLight },
  floatTop: { width: 51, height: 51, borderRadius: 18, backgroundColor: colors.surface, justifyContent: 'center', alignItems: 'center', position: 'absolute', top: 45, right: 30, borderWidth: 1, borderColor: colors.line },
  floatBottom: { width: 41, height: 41, borderRadius: 14, backgroundColor: colors.surface, justifyContent: 'center', alignItems: 'center', position: 'absolute', bottom: 31, left: 24, borderWidth: 1, borderColor: colors.line },
  floatGlyph: { fontSize: 26, color: colors.cyan },
  title: { color: colors.text, fontSize: 41, fontWeight: '800', marginTop: 23, letterSpacing: -1.6 },
  titleAccent: { color: colors.purple, fontSize: 42, fontWeight: '800', letterSpacing: -1.6 },
  description: { color: colors.muted, fontSize: 16, lineHeight: 25, marginTop: 15, maxWidth: 295 },
  spacer: { flex: 1, minHeight: 18 },
  footnote: { color: colors.dim, fontSize: 11.5, alignSelf: 'center', marginTop: 23, marginBottom: 10 },
});

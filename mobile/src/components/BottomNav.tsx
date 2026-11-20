import React from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { colors } from '../theme';

export function BottomNav({ active, onDetector, onAbout }: { active: 'detector' | 'about'; onDetector: () => void; onAbout: () => void }) {
  return <View style={styles.root}>
    <Pressable accessibilityRole="tab" accessibilityState={{ selected: active === 'detector' }} onPress={onDetector} style={[styles.tab, active === 'detector' && styles.active]}>
      <Text style={[styles.glyph, active === 'detector' && styles.highlight]}>✦</Text><Text style={[styles.text, active === 'detector' && styles.white]}>Detector</Text>
    </Pressable>
    <Pressable accessibilityRole="tab" accessibilityState={{ selected: active === 'about' }} onPress={onAbout} style={[styles.tab, active === 'about' && styles.active]}>
      <Text style={[styles.glyph, active === 'about' && styles.highlight]}>ⓘ</Text><Text style={[styles.text, active === 'about' && styles.white]}>About</Text>
    </Pressable>
  </View>;
}

const styles = StyleSheet.create({
  root: { flexDirection: 'row', gap: 16, paddingHorizontal: 24, paddingTop: 13, paddingBottom: 8, borderTopColor: colors.line, borderTopWidth: 1, backgroundColor: colors.bg },
  tab: { height: 56, borderRadius: 16, flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 9, backgroundColor: colors.surface },
  active: { backgroundColor: '#252347', borderWidth: 1, borderColor: '#49417E' },
  glyph: { fontSize: 22, color: colors.dim },
  highlight: { color: colors.purpleLight },
  text: { fontSize: 14, fontWeight: '700', color: colors.muted },
  white: { color: colors.text },
});

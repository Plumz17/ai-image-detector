import React from 'react';
import { ActivityIndicator, Pressable, ScrollView, StyleSheet, Text, View, type StyleProp, type ViewStyle, type TextStyle } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { colors } from '../theme';

export function Body({ children, style, scroll = true }: { children: React.ReactNode; style?: StyleProp<ViewStyle>; scroll?: boolean }) {
  const content = <View style={[styles.body, style]}>{children}</View>;
  return scroll ? <ScrollView style={styles.scroller} contentContainerStyle={{ flexGrow: 1 }} showsVerticalScrollIndicator={false} keyboardShouldPersistTaps="handled">{content}</ScrollView> : <View style={[styles.scroller, { flex: 1 }]}>{content}</View>;
}

export function Brand({ compact = false }: { compact?: boolean }) {
  return <View style={styles.brandRow}>
    <View style={styles.brandGlyph}><Text style={styles.brandStar}>✦</Text></View>
    <Text style={[styles.brandTitle, compact && { fontSize: 19 }]}>AI Image Detector</Text>
  </View>;
}

export function Header({ title, onBack }: { title: string; onBack?: () => void }) {
  if (!onBack) return <View style={styles.header}><Brand /><View style={styles.headerBubble}><Text style={{ fontSize: 17, color: colors.muted }}>✧</Text></View></View>;
  return <View style={styles.header}>
    <Pressable accessibilityRole="button" accessibilityLabel="Go back" onPress={onBack} style={styles.backCircle}><Text style={styles.backText}>‹</Text></Pressable>
    <Text style={styles.headerTitle}>{title}</Text>
    <View style={{ width: 38 }} />
  </View>;
}

export function Tag({ children, tone = 'cyan' }: { children: React.ReactNode; tone?: 'cyan' | 'purple' | 'mint' | 'red' | 'amber' }) {
  const color = colors[tone];
  return <View style={[styles.tag, { backgroundColor: `${color}20` }]}><Text style={[styles.tagText, { color }]}>{children}</Text></View>;
}

export function PrimaryButton({ title, onPress, disabled = false, secondary = false, icon, busy = false }: { title: string; onPress: () => void; disabled?: boolean; secondary?: boolean; icon?: string; busy?: boolean }) {
  return <Pressable accessibilityRole="button" accessibilityLabel={title} disabled={disabled || busy} onPress={onPress} style={({ pressed }) => [{ opacity: disabled || busy ? 0.55 : pressed ? 0.86 : 1 }, styles.buttonOuter]}>
    {secondary ? <View style={[styles.buttonInner, styles.secondaryButton]}>{busy ? <ActivityIndicator color={colors.text} /> : <><Text style={styles.buttonText}>{title}</Text>{icon ? <Text style={styles.buttonArrow}>{icon}</Text> : null}</>}</View>
      : <LinearGradient colors={[colors.purple, colors.purpleDeep]} start={{ x: 0, y: 0 }} end={{ x: 1, y: 1 }} style={styles.buttonInner}>{busy ? <ActivityIndicator color={colors.text} /> : <><Text style={styles.buttonText}>{title}</Text>{icon ? <Text style={styles.buttonArrow}>{icon}</Text> : null}</>}</LinearGradient>}
  </Pressable>;
}

export function Card({ children, style }: { children: React.ReactNode; style?: StyleProp<ViewStyle> }) {
  return <View style={[styles.card, style]}>{children}</View>;
}

export function Caption({ children, style }: { children: React.ReactNode; style?: StyleProp<TextStyle> }) {
  return <Text style={[styles.caption, style]}>{children}</Text>;
}

export function Glow() {
  return <View pointerEvents="none" style={StyleSheet.absoluteFill}>
    <View style={styles.glowTop}/><View style={styles.glowLeft}/>
  </View>;
}

export function StepLabel({ number }: { number: number }) {
  return <Tag>STEP {number} OF 3</Tag>;
}

const styles = StyleSheet.create({
  scroller: { flex: 1 },
  body: { flexGrow: 1, paddingHorizontal: 24, paddingTop: 16, paddingBottom: 30 },
  brandRow: { flexDirection: 'row', gap: 9, alignItems: 'center' },
  brandGlyph: { width: 31, height: 31, borderRadius: 11, backgroundColor: '#28224C', alignItems: 'center', justifyContent: 'center' },
  brandStar: { fontSize: 21, color: colors.purpleLight },
  brandTitle: { fontSize: 20, fontWeight: '800', color: colors.text, letterSpacing: -0.5 },
  header: { height: 63, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  headerBubble: { borderRadius: 15, width: 35, height: 35, alignItems: 'center', justifyContent: 'center', backgroundColor: colors.elevated },
  backCircle: { width: 38, height: 38, borderRadius: 12, backgroundColor: colors.surface, justifyContent: 'center', alignItems: 'center', borderWidth: 1, borderColor: colors.line },
  backText: { color: colors.text, fontSize: 33, lineHeight: 36, marginTop: -4 },
  headerTitle: { color: colors.text, fontSize: 18, fontWeight: '700' },
  tag: { borderRadius: 40, paddingHorizontal: 13, paddingVertical: 8, alignSelf: 'flex-start' },
  tagText: { fontWeight: '700', fontSize: 10.5, letterSpacing: 1 },
  buttonOuter: { width: '100%', marginTop: 10 },
  buttonInner: { minHeight: 54, borderRadius: 15, justifyContent: 'center', flexDirection: 'row', alignItems: 'center', gap: 9, paddingHorizontal: 20 },
  secondaryButton: { backgroundColor: colors.elevated, borderWidth: 1, borderColor: colors.line },
  buttonText: { color: colors.text, fontWeight: '700', fontSize: 15.5 },
  buttonArrow: { color: colors.text, fontWeight: '700', fontSize: 19 },
  card: { backgroundColor: colors.surface, borderColor: colors.line, borderWidth: 1, borderRadius: 21, overflow: 'hidden' },
  caption: { color: colors.muted, fontSize: 13, lineHeight: 20 },
  glowTop: { position: 'absolute', height: 250, width: 250, right: -115, top: -148, backgroundColor: '#342B63', opacity: .23, borderRadius: 200 },
  glowLeft: { position: 'absolute', height: 290, width: 290, left: -220, top: 420, backgroundColor: '#1D4973', opacity: .12, borderRadius: 200 },
});

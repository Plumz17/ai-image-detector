import React, { useEffect, useRef } from 'react';
import { ActivityIndicator, Animated, StyleSheet, Text, View } from 'react-native';
import { Body, Caption, Header, PrimaryButton, StepLabel } from '../components/UI';
import { colors } from '../theme';

export function Loading({ onCancel }: { onCancel: () => void }) {
  const pulse = useRef(new Animated.Value(.6)).current;
  useEffect(() => {
    const loop=Animated.loop(Animated.sequence([
      Animated.timing(pulse,{toValue:1,duration:850,useNativeDriver:true}),
      Animated.timing(pulse,{toValue:.6,duration:850,useNativeDriver:true}),
    ]));loop.start();return()=>loop.stop();
  },[pulse]);
  return <Body scroll={false}>
    <Header title="Scanning image" onBack={onCancel}/>
    <View style={{ marginTop: 19 }}><StepLabel number={2}/></View>
    <View style={styles.main}>
      <Animated.View style={[styles.outer,{opacity:pulse}]}><View style={styles.mid}><View style={styles.inner}><Text style={{fontSize:53,color:colors.purpleLight}}>✦</Text></View></View></Animated.View>
      <Text style={styles.title}>Looking closer...</Text>
      <Text style={styles.sub}>Sending the image to the detection server and waiting for its prediction.</Text>
      <View style={styles.indicator}><ActivityIndicator size="small" color={colors.purple}/><Text style={styles.indicatorText}>Analysis in progress</Text></View>
    </View>
    <Caption style={{ textAlign:'center',marginBottom:15 }}>Processing time depends on the model and connection.</Caption>
    <PrimaryButton title="Cancel Analysis" onPress={onCancel} secondary/>
  </Body>;
}
const styles=StyleSheet.create({main:{flex:1,justifyContent:'center',alignItems:'center',minHeight:340},outer:{height:240,width:240,borderRadius:150,backgroundColor:'#211C4D',justifyContent:'center',alignItems:'center'},mid:{height:171,width:171,borderRadius:105,backgroundColor:'#30265F',justifyContent:'center',alignItems:'center'},inner:{height:96,width:96,borderRadius:56,backgroundColor:'#43357A',justifyContent:'center',alignItems:'center'},title:{fontSize:26,color:colors.text,fontWeight:'800',marginTop:38,letterSpacing:-.7},sub:{color:colors.muted,fontSize:14,lineHeight:22,textAlign:'center',marginTop:12,maxWidth:275},indicator:{marginTop:30,flexDirection:'row',alignItems:'center',gap:10,paddingVertical:12,paddingHorizontal:16,backgroundColor:colors.surface,borderRadius:30},indicatorText:{color:colors.purpleLight,fontWeight:'600',fontSize:12}});

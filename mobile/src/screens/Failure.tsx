import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { Body, Caption, Header, PrimaryButton, Tag } from '../components/UI';
import { colors } from '../theme';

export function Failure({ error, onRetry, onChange, onBack }: { error: string; onRetry: () => void; onChange: () => void; onBack: () => void }) {
  return <Body>
    <Header title="Analysis failed" onBack={onBack}/>
    <View style={{alignItems:'center',marginTop:70}}><View style={styles.circle}><Text style={styles.icon}>!</Text></View><Tag tone="red">SOMETHING WENT WRONG</Tag></View>
    <Text style={styles.title}>We couldn't finish the scan.</Text>
    <Caption style={{textAlign:'center'}}>Your image is still selected. You can try again or choose a different image.</Caption>
    <View style={styles.errorBox}><Text style={styles.errorTitle}>Error details</Text><Text selectable style={styles.message}>{error}</Text></View>
    <View style={{marginTop:19}}><PrimaryButton title="Try Again" icon="↻" onPress={onRetry}/><PrimaryButton title="Choose Another Image" secondary onPress={onChange}/></View>
  </Body>;
}
const styles=StyleSheet.create({circle:{width:123,height:123,borderRadius:70,alignItems:'center',justifyContent:'center',backgroundColor:'#4A2139',marginBottom:27},icon:{color:colors.red,fontSize:74,fontWeight:'700'},title:{fontSize:27,color:colors.text,fontWeight:'800',textAlign:'center',marginTop:27,marginBottom:14,letterSpacing:-.6},errorBox:{backgroundColor:colors.elevated,borderColor:colors.line,borderWidth:1,borderRadius:14,padding:16,marginTop:27},errorTitle:{fontSize:12,color:colors.amber,fontWeight:'700',marginBottom:10},message:{color:colors.muted,fontSize:12,lineHeight:19}});

import React from 'react';
import { Image, StyleSheet, Text, View } from 'react-native';
import { Body, Card, Header, PrimaryButton, StepLabel } from '../components/UI';
import { describeResult, DISCLAIMER, JPEG_NOTE } from '../describe';
import type { DetectionResult, UploadImage } from '../types';
import { colors } from '../theme';

export function Result({ result, image, onBack, onReset }: { result: DetectionResult; image: UploadImage; onBack: () => void; onReset: () => void }) {
  const ai = result.verdict==='ai';
  const color = ai ? colors.red : colors.mint;
  const { headline, explanation } = describeResult(ai, result.crops, result.flagged);
  return <Body>
    <Header title="Scan result" onBack={onBack}/>
    <View style={styles.step}><StepLabel number={3}/></View>
    <Card style={styles.imageCard}>
      <Image source={{uri:image.uri}} style={styles.image} resizeMode="contain"/>
      <View style={styles.fileBar}><Text style={styles.imageName} numberOfLines={1}>{image.name}</Text><Text style={{color:colors.purpleLight,fontSize:12}}>◉  Analyzed</Text></View>
    </Card>
    <Card style={styles.resultCard}>
      <View style={styles.row}><View style={[styles.badge,{backgroundColor:`${color}22`}]}><Text style={{color,fontSize:23,fontWeight:'700'}}>{ai?'!':'✓'}</Text></View><View style={{flex:1}}><Text style={styles.title}>{headline}</Text></View></View>
      <View style={styles.divider}/>
      <Text style={styles.sub}>{explanation}</Text>
      {image.mimeType==='image/jpeg' ? <Text style={[styles.sub,{marginTop:12}]}>{JPEG_NOTE}</Text> : null}
    </Card>
    <View style={styles.note}><Text style={styles.noteIcon}>ⓘ</Text><Text style={styles.noteText}>{DISCLAIMER}</Text></View>
    <View style={{marginTop:13}}><PrimaryButton title="Scan Another Image" icon="↗" onPress={onReset}/></View>
  </Body>;
}
const styles=StyleSheet.create({
 step:{flexDirection:'row',justifyContent:'space-between',alignItems:'center',marginTop:19},
 imageCard:{marginTop:22,height:240,backgroundColor:'#172944'},
 image:{height:196,width:'100%',backgroundColor:'#1B2C49'},
 fileBar:{flexDirection:'row',alignItems:'center',justifyContent:'space-between',paddingHorizontal:14,height:43,backgroundColor:colors.surface},
 imageName:{fontSize:11.5,color:colors.muted,maxWidth:'58%'},
 resultCard:{marginTop:16,padding:18},
 row:{flexDirection:'row',gap:13,alignItems:'center'},
 badge:{width:45,height:45,borderRadius:15,alignItems:'center',justifyContent:'center'},
 title:{color:colors.text,fontSize:19,fontWeight:'800',marginBottom:5},
 sub:{color:colors.muted,fontSize:12.3,lineHeight:19,flexShrink:1},
 divider:{height:1,backgroundColor:colors.line,marginVertical:19},
 note:{flexDirection:'row',gap:12,alignItems:'center',backgroundColor:colors.elevated,borderRadius:15,padding:15,marginTop:16},
 noteIcon:{color:colors.cyan,fontSize:21},
 noteText:{color:colors.muted,fontSize:12,lineHeight:18,flex:1},
});

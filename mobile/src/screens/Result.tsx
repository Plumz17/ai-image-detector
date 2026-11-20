import React from 'react';
import { Image, StyleSheet, Text, View } from 'react-native';
import { Body, Caption, Card, Header, PrimaryButton, StepLabel, Tag } from '../components/UI';
import type { DetectionResult, UploadImage } from '../types';
import { colors } from '../theme';

export function Result({ result, image, onBack, onReset }: { result: DetectionResult; image: UploadImage; onBack: () => void; onReset: () => void }) {
  const ai = result.verdict==='ai';
  const unknown = result.verdict==='uncertain';
  const color = unknown ? colors.amber : ai ? colors.red : colors.mint;
  const title = unknown ? 'Uncertain result' : ai ? 'Likely AI-generated' : 'Likely authentic';
  const subtitle = unknown ? 'The model could not make a confident classification.' : ai ? 'The model flagged this image as potentially AI-generated.' : 'The model found fewer signs of AI generation.';
  return <Body>
    <Header title="Scan result" onBack={onBack}/>
    <View style={styles.step}><StepLabel number={3}/>{result.isDemo ? <Tag tone="amber">DEMO RESULT</Tag> : null}</View>
    <Card style={styles.imageCard}>
      <Image source={{uri:image.uri}} style={styles.image} resizeMode="contain"/>
      <View style={styles.fileBar}><Text style={styles.imageName} numberOfLines={1}>{image.name}</Text><Text style={{color:colors.purpleLight,fontSize:12}}>◉  Analyzed</Text></View>
    </Card>
    <Card style={styles.resultCard}>
      <View style={styles.row}><View style={[styles.badge,{backgroundColor:`${color}22`}]}><Text style={{color,fontSize:23,fontWeight:'700'}}>{unknown?'?':ai?'!':'✓'}</Text></View><View style={{flex:1}}><Text style={styles.title}>{title}</Text><Text style={styles.sub}>{subtitle}</Text></View></View>
      {result.confidence!==null?<>
        <View style={styles.divider}/>
        <View style={styles.confRow}><Text style={styles.confLabel}>MODEL CONFIDENCE</Text><Text style={[styles.confNumber,{color}]}>{`${result.confidence.toFixed(1).replace('.0','')}%`}</Text></View>
        <View style={styles.bar}><View style={[styles.barInner,{backgroundColor:color,width:`${result.confidence}%`}]} /></View>
      </>:null}
      {result.model ? <Text style={styles.model}>Model: {result.model}</Text> : null}
    </Card>
    {result.explanation ? <Card style={styles.explain}><Text style={styles.explainTitle}>Model details</Text><Caption>{result.explanation}</Caption></Card> : null}
    <View style={styles.note}><Text style={styles.noteIcon}>ⓘ</Text><Text style={styles.noteText}>{result.isDemo?'This is a simulated example, not an actual detection.':'This result can be wrong, especially for photos taken with a phone or sent through chat apps. It is not proof of where an image came from.'}</Text></View>
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
 confRow:{flexDirection:'row',alignItems:'center',justifyContent:'space-between'},
 confLabel:{color:colors.muted,fontSize:11,fontWeight:'700',letterSpacing:.7},
 confNumber:{fontSize:20,fontWeight:'800'},
 bar:{height:9,borderRadius:9,backgroundColor:colors.line,overflow:'hidden',marginTop:12},
 barInner:{height:'100%',borderRadius:9},
 model:{color:colors.dim,fontSize:11,marginTop:12},
 note:{flexDirection:'row',gap:12,alignItems:'center',backgroundColor:colors.elevated,borderRadius:15,padding:15,marginTop:16},
 noteIcon:{color:colors.cyan,fontSize:21},
 noteText:{color:colors.muted,fontSize:12,lineHeight:18,flex:1},
 explain:{padding:15,marginTop:13},explainTitle:{color:colors.text,fontWeight:'700',marginBottom:8,fontSize:13}
});

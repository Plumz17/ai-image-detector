import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { Body, Caption, Card, Header, Tag } from '../components/UI';
import { colors } from '../theme';

const steps = [
  ['01', 'Select an image', 'Choose a photo from your device or take a new one.'],
  ['02', 'Analyze patterns', 'The image is sent to the connected detection model.'],
  ['03', 'Review the result', 'See whether the model found signs of AI generation.'],
];
export function About() {
  return <Body>
    <Header title="About"/>
    <View style={{marginTop:20}}><Tag>OUR MISSION</Tag></View>
    <Text style={styles.title}>Clarity in</Text><Text style={styles.accent}>every pixel.</Text>
    <Caption style={styles.intro}>VeriPixel helps people explore whether an image might have been generated using AI, one scan at a time.</Caption>
    <Text style={styles.sectionTitle}>HOW IT WORKS</Text>
    {steps.map(([id,title,desc])=><Card key={id} style={styles.step}>
      <View style={styles.num}><Text style={styles.numText}>{id}</Text></View>
      <View style={{flex:1}}><Text style={styles.stepTitle}>{title}</Text><Caption>{desc}</Caption></View>
    </Card>)}
    <View style={styles.important}><Text style={styles.importantTitle}>IMPORTANT TO KNOW</Text><Caption>Predictions are estimates, not definitive evidence. Your image is sent to the configured backend for processing; storage and retention depend on that server.</Caption></View>
    <Text style={styles.footer}>VeriPixel · Mobile frontend · v1.0</Text>
  </Body>;
}
const styles=StyleSheet.create({title:{color:colors.text,fontSize:36,fontWeight:'800',letterSpacing:-1.1,marginTop:23},accent:{color:colors.purple,fontSize:37,fontWeight:'800',letterSpacing:-1.1,marginTop:-6},intro:{fontSize:15,lineHeight:23,marginTop:18,marginBottom:30},sectionTitle:{fontSize:11,color:colors.cyan,fontWeight:'800',letterSpacing:1,marginBottom:17},step:{padding:15,flexDirection:'row',alignItems:'center',gap:15,marginBottom:12},num:{width:46,height:46,backgroundColor:'#2B2453',borderRadius:14,alignItems:'center',justifyContent:'center'},numText:{color:colors.purpleLight,fontSize:15,fontWeight:'800'},stepTitle:{color:colors.text,fontWeight:'700',fontSize:15,marginBottom:4},important:{backgroundColor:colors.elevated,padding:18,borderRadius:16,marginTop:11},importantTitle:{color:colors.amber,fontWeight:'800',letterSpacing:.6,fontSize:10,marginBottom:9},footer:{alignSelf:'center',marginTop:28,fontSize:11,color:colors.dim}});

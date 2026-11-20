import React from 'react';
import { Linking, StyleSheet, Text, View } from 'react-native';
import { Body, Caption, Card, Header, Tag } from '../components/UI';
import { colors } from '../theme';

// Wording follows the web app's About page (web/src/pages/About.jsx).
const steps = [
  ['01', 'Upload', 'Choose a supported image and submit it for analysis.'],
  ['02', 'Analyze', 'The detector examines image texture patterns through the PatchCraft feature-extraction pipeline.'],
  ['03', 'Get Results', 'The classifier aggregates crop-level predictions and returns an estimate: real or AI-generated.'],
];
const tags = ['PatchCraft', 'High-pass filters', 'CNN features', 'SVM classifier', 'Multi-crop inference'];
const PAPER = 'https://www.icicelb.org/ellb/contents/2026/12/elb-17-12-10.pdf';

export function About() {
  return <Body>
    <Header title="About"/>
    <View style={{marginTop:20}}><Tag>HOW IT WORKS</Tag></View>
    <Text style={styles.title}>Behind the</Text><Text style={styles.accent}>Detector.</Text>
    <Caption style={styles.intro}>Understand the technology behind identifying AI-generated images and explore how our tool helps distinguish artificial creations from real-world visuals.</Caption>

    <Text style={styles.sectionTitle}>WHAT DOES IT DO?</Text>
    <Caption style={styles.para}>Our AI Image Detector analyzes uploaded images to estimate whether they were created using generative AI or captured in the real world. It uses PatchCraft, a method that focuses on fine-grained image texture patterns, to provide an additional signal when assessing digital content.</Caption>

    <Text style={styles.sectionTitle}>HOW DOES IT WORK?</Text>
    {steps.map(([id,title,desc])=><Card key={id} style={styles.step}>
      <View style={styles.num}><Text style={styles.numText}>{id}</Text></View>
      <View style={{flex:1}}><Text style={styles.stepTitle}>{title}</Text><Caption>{desc}</Caption></View>
    </Card>)}

    <Text style={[styles.sectionTitle,{marginTop:18}]}>INSIDE THE MODEL</Text>
    <Caption style={styles.para}>The pipeline creates texture-rich and texture-poor patch reconstructions, applies high-pass filters, and extracts features with a convolutional neural network. A support vector machine (SVM) then classifies the extracted features. Images are evaluated using multiple crops, with their predictions combined into a final label.</Caption>
    <View style={styles.tags}>{tags.map(t=><Tag key={t} tone="purple">{t}</Tag>)}</View>
    <Caption style={styles.para}>Source: the PatchCraft model was implemented and trained by the model's author.{' '}
      <Text style={styles.link} onPress={() => Linking.openURL(PAPER)}>Read the published paper</Text>.</Caption>

    <View style={styles.important}><Text style={styles.importantTitle}>IMPORTANT DISCLAIMER</Text><Caption>Predictions are estimates, not guarantees. Detection can be affected by compression, image processing, and the types of images the model has encountered. Always consider additional context when evaluating an image’s authenticity.</Caption></View>
    <Text style={styles.footer}>AI Image Detector · A tool for image authenticity assessment</Text>
  </Body>;
}
const styles=StyleSheet.create({title:{color:colors.text,fontSize:36,fontWeight:'800',letterSpacing:-1.1,marginTop:23},accent:{color:colors.purple,fontSize:37,fontWeight:'800',letterSpacing:-1.1,marginTop:-6},intro:{fontSize:15,lineHeight:23,marginTop:18,marginBottom:30},sectionTitle:{fontSize:11,color:colors.cyan,fontWeight:'800',letterSpacing:1,marginBottom:14},para:{fontSize:14,lineHeight:22,marginBottom:22},tags:{flexDirection:'row',flexWrap:'wrap',gap:8,marginBottom:20},link:{color:colors.purpleLight,textDecorationLine:'underline'},step:{padding:15,flexDirection:'row',alignItems:'center',gap:15,marginBottom:12},num:{width:46,height:46,backgroundColor:'#2B2453',borderRadius:14,alignItems:'center',justifyContent:'center'},numText:{color:colors.purpleLight,fontSize:15,fontWeight:'800'},stepTitle:{color:colors.text,fontWeight:'700',fontSize:15,marginBottom:4},important:{backgroundColor:colors.elevated,padding:18,borderRadius:16,marginTop:11},importantTitle:{color:colors.amber,fontWeight:'800',letterSpacing:.6,fontSize:10,marginBottom:9},footer:{alignSelf:'center',textAlign:'center',marginTop:28,fontSize:11,color:colors.dim}});

import React from 'react';
import { Image, StyleSheet, Text, View } from 'react-native';
import { Body, Caption, Card, Header, PrimaryButton, StepLabel } from '../components/UI';
import type { UploadImage } from '../types';
import { colors } from '../theme';

export function Preview({ image, onAnalyze, onChange, onBack }: { image: UploadImage; onAnalyze: () => void; onChange: () => void; onBack: () => void }) {
  const prettySize = typeof image.size === 'number' ? image.size >= 1048576 ? `${(image.size/1048576).toFixed(2)} MB` : `${(image.size/1024).toFixed(0)} KB` : 'Size unknown';
  return <Body>
    <Header title="Image ready" onBack={onBack}/>
    <View style={{ marginTop: 19 }}><StepLabel number={1}/></View>
    <Text style={styles.title}>Ready to analyze</Text><Caption>Review your image before scanning.</Caption>
    <Card style={styles.imageBox}><Image source={{ uri: image.uri }} style={styles.image} resizeMode="contain"/></Card>
    <Card style={styles.info}><View style={styles.fileIcon}><Text style={{ color: colors.cyan, fontSize: 24 }}>▧</Text></View><View style={{ flex: 1 }}>
      <Text numberOfLines={1} style={styles.fileName}>{image.name}</Text><Caption>{image.mimeType.toUpperCase().replace('IMAGE/', '')} image · {prettySize}</Caption>
    </View><Text style={{ color: colors.mint, fontSize: 22 }}>✓</Text></Card>
    <View style={{ marginTop: 14 }}><PrimaryButton title="Analyze Image" icon="→" onPress={onAnalyze}/><PrimaryButton title="Change Image" onPress={onChange} secondary/></View>
  </Body>;
}
const styles=StyleSheet.create({
 title:{fontSize:27,fontWeight:'800',color:colors.text,marginTop:22,marginBottom:7,letterSpacing:-.7},
 imageBox:{height:280,marginTop:23,backgroundColor:'#182844',padding:7},image:{width:'100%',height:'100%',borderRadius:14},
 info:{marginTop:16,flexDirection:'row',alignItems:'center',padding:14,gap:12},
 fileIcon:{backgroundColor:'#223759',borderRadius:12,width:47,height:47,alignItems:'center',justifyContent:'center'},
 fileName:{color:colors.text,fontSize:14.5,fontWeight:'700',marginBottom:5},
});

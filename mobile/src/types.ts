export type Screen = 'welcome' | 'home' | 'preview' | 'loading' | 'result' | 'about' | 'error';
export type Verdict = 'ai' | 'real';
export type UploadImage = {
  uri: string;
  name: string;
  mimeType: string;
  size?: number | null;
  width?: number;
  height?: number;
};
export type DetectionResult = {
  verdict: Verdict;
  crops: number;   // how many parts of the image were checked
  flagged: number; // how many of them looked AI-generated
};

export type Screen = 'welcome' | 'home' | 'preview' | 'loading' | 'result' | 'about' | 'error';
export type Verdict = 'ai' | 'real' | 'uncertain';
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
  confidence: number | null;
  aiProbability: number | null;
  explanation: string | null;
  model: string | null;
  isDemo: boolean;
};

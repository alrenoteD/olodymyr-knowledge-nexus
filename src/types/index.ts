
export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface Session {
  id: string;
  name: string;
  description: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
}

export interface LearningSession {
  id: string;
  name: string;
  description: string;
  content: string;
  source?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface ModelType {
  id: string;
  name: string;
  description: string;
}

export interface UserSettings {
  theme: 'light' | 'dark' | 'system';
  preferredModel: string;
  useEmojis: boolean;
  enableWebScraping: boolean;
  enableFileUpload: boolean;
}

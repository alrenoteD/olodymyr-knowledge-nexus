
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Message, Session, LearningSession, UserSettings } from '@/types';
import { v4 as uuidv4 } from 'uuid';

interface AppState {
  sessions: Session[];
  currentSessionId: string | null;
  learningData: LearningSession[];
  isLoading: boolean;
  userSettings: UserSettings;
  
  // Session actions
  createNewSession: (name: string, description: string) => void;
  setCurrentSession: (sessionId: string) => void;
  deleteSession: (sessionId: string) => void;
  renameSession: (sessionId: string, name: string, description?: string) => void;
  
  // Message actions
  addMessage: (content: string, role: 'user' | 'assistant') => void;
  clearMessages: (sessionId: string) => void;
  
  // Learning actions
  addLearningSession: (name: string, content: string, description: string, source?: string) => void;
  deleteLearningSession: (id: string) => void;
  updateLearningSession: (id: string, updates: Partial<Omit<LearningSession, 'id' | 'createdAt'>>) => void;
  
  // UI actions
  setLoading: (isLoading: boolean) => void;
  updateUserSettings: (settings: Partial<UserSettings>) => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      sessions: [],
      currentSessionId: null,
      learningData: [],
      isLoading: false,
      userSettings: {
        theme: 'system',
        preferredModel: 'claude-haiku',
        useEmojis: true,
        enableWebScraping: true,
        enableFileUpload: true
      },
      
      // Session actions
      createNewSession: (name, description) => {
        const newSessionId = uuidv4();
        set((state) => ({
          sessions: [
            ...state.sessions,
            {
              id: newSessionId,
              name,
              description,
              messages: [],
              createdAt: new Date(),
              updatedAt: new Date()
            }
          ],
          currentSessionId: newSessionId
        }));
      },
      
      setCurrentSession: (sessionId) => set({ currentSessionId: sessionId }),
      
      deleteSession: (sessionId) => 
        set((state) => ({
          sessions: state.sessions.filter(session => session.id !== sessionId),
          currentSessionId: state.currentSessionId === sessionId ? 
            (state.sessions.length > 1 ? 
              state.sessions.find(s => s.id !== sessionId)?.id || null : null) 
            : state.currentSessionId
        })),
      
      renameSession: (sessionId, name, description) => 
        set((state) => ({
          sessions: state.sessions.map(session => 
            session.id === sessionId ? 
              { 
                ...session, 
                name, 
                description: description || session.description,
                updatedAt: new Date() 
              } : session
          )
        })),
      
      // Message actions
      addMessage: (content, role) => 
        set((state) => {
          if (!state.currentSessionId) {
            const newSessionId = uuidv4();
            return {
              sessions: [
                {
                  id: newSessionId,
                  name: "Nova conversa",
                  description: "Conversa iniciada automaticamente",
                  messages: [{
                    id: uuidv4(),
                    role,
                    content,
                    timestamp: new Date()
                  }],
                  createdAt: new Date(),
                  updatedAt: new Date()
                },
                ...state.sessions
              ],
              currentSessionId: newSessionId
            };
          }
          
          return {
            sessions: state.sessions.map(session => 
              session.id === state.currentSessionId ? 
                {
                  ...session,
                  messages: [
                    ...session.messages,
                    {
                      id: uuidv4(),
                      role,
                      content,
                      timestamp: new Date()
                    }
                  ],
                  updatedAt: new Date()
                } : session
            )
          };
        }),
      
      clearMessages: (sessionId) => 
        set((state) => ({
          sessions: state.sessions.map(session => 
            session.id === sessionId ? 
              { ...session, messages: [], updatedAt: new Date() } : session
          )
        })),
      
      // Learning actions
      addLearningSession: (name, content, description, source) => 
        set((state) => ({
          learningData: [
            ...state.learningData,
            {
              id: uuidv4(),
              name,
              description,
              content,
              source,
              createdAt: new Date(),
              updatedAt: new Date()
            }
          ]
        })),
      
      deleteLearningSession: (id) => 
        set((state) => ({
          learningData: state.learningData.filter(session => session.id !== id)
        })),
      
      updateLearningSession: (id, updates) => 
        set((state) => ({
          learningData: state.learningData.map(session => 
            session.id === id ? 
              { ...session, ...updates, updatedAt: new Date() } : session
          )
        })),
      
      // UI actions
      setLoading: (isLoading) => set({ isLoading }),
      
      updateUserSettings: (settings) => 
        set((state) => ({
          userSettings: { ...state.userSettings, ...settings }
        })),
    }),
    {
      name: 'olodymyr-store',
    }
  )
);

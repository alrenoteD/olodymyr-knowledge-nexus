
import { useEffect, useRef } from "react";
import { useAppStore } from "@/lib/store";
import { ChatMessage } from "./ChatMessage";
import { ChatInput } from "./ChatInput";
import { Bot } from "lucide-react";

export function ChatContainer() {
  const { sessions, currentSessionId } = useAppStore();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const currentSession = sessions.find(s => s.id === currentSessionId);
  const messages = currentSession?.messages || [];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center">
            <div className="bg-olodymyr-500 rounded-full p-6 mb-6">
              <Bot className="h-10 w-10 text-white" />
            </div>
            <h2 className="text-2xl font-bold mb-2">Olodymyr</h2>
            <p className="text-center text-muted-foreground max-w-sm">
              Seu assistente de IA pessoal com conhecimento personalizado.
              Comece enviando uma mensagem abaixo.
            </p>
          </div>
        ) : (
          messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))
        )}
        <div ref={messagesEndRef} />
      </div>
      
      <ChatInput />
    </div>
  );
}

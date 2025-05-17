
import { Message } from '@/types';
import { cn } from '@/lib/utils';
import { User, Bot } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  return (
    <div 
      className={cn(
        "py-6 flex",
        message.role === "user" ? "bg-accent/30" : "bg-background"
      )}
      data-testid={`message-${message.role}`}
    >
      <div className="container flex gap-4 max-w-3xl">
        <div className="w-8 h-8 rounded-full flex items-center justify-center shrink-0">
          {message.role === "user" ? (
            <div className="bg-primary rounded-full p-1">
              <User className="h-5 w-5 text-primary-foreground" />
            </div>
          ) : (
            <div className="bg-olodymyr-500 rounded-full p-1">
              <Bot className="h-5 w-5 text-white" />
            </div>
          )}
        </div>
        <div className="flex-1 space-y-2 overflow-hidden">
          <p className="font-medium">
            {message.role === "user" ? "Você" : "Olodymyr"}
          </p>
          <div className="message-content prose prose-sm dark:prose-invert max-w-full">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
          <div className="text-xs text-muted-foreground">
            {new Date(message.timestamp).toLocaleTimeString()}
          </div>
        </div>
      </div>
    </div>
  );
}


import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { SendHorizonal, Loader2, Link } from 'lucide-react';
import { useAppStore } from '@/lib/store';
import { getChatCompletion, scrapeWebContent } from '@/lib/api';
import { 
  Dialog,
  DialogTrigger,
  DialogContent, 
  DialogHeader,
  DialogTitle,
  DialogFooter
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from '@/components/ui/use-toast';

export function ChatInput() {
  const [inputValue, setInputValue] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [urlDialogOpen, setUrlDialogOpen] = useState(false);
  const [url, setUrl] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const { 
    addMessage, 
    userSettings, 
    sessions, 
    currentSessionId,
    addLearningSession
  } = useAppStore();

  // Resize textarea based on content
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [inputValue]);

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputValue(e.target.value);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (inputValue.trim()) {
        handleSubmit();
      }
    }
  };

  const handleSubmit = async () => {
    if (!inputValue.trim() || isSubmitting) return;

    const userInput = inputValue.trim();
    setInputValue('');
    setIsSubmitting(true);
    
    try {
      addMessage(userInput, 'user');
      
      // Check if this is a learning request
      if (userInput.toLowerCase().includes('aprenda isso') || 
          userInput.toLowerCase().includes('guarde isso')) {
        // Get the content to learn - everything after the command
        const content = userInput.replace(/aprenda isso|guarde isso/i, '').trim();
        
        if (content) {
          addLearningSession(
            `Aprendizado ${new Date().toLocaleDateString()}`, 
            content,
            "Conteúdo aprendido por comando direto"
          );
        }
      }
      
      // Get AI response
      const currentMessages = sessions.find(s => s.id === currentSessionId)?.messages || [];
      const response = await getChatCompletion(
        [...currentMessages, { id: 'temp', role: 'user', content: userInput, timestamp: new Date() }],
        userSettings.preferredModel
      );
      
      addMessage(response, 'assistant');
    } catch (error) {
      toast({
        title: "Erro",
        description: "Não foi possível processar sua mensagem. Tente novamente.",
        variant: "destructive"
      });
      console.error("Error in chat submission:", error);
    } finally {
      setIsSubmitting(false);
    }
  };
  
  const handleWebScrape = async () => {
    if (!url.trim()) return;
    
    try {
      setIsSubmitting(true);
      setUrlDialogOpen(false);
      
      // Add user message about scraping
      addMessage(`Analisar e aprender conteúdo de: ${url}`, 'user');
      
      // Scrape content
      const content = await scrapeWebContent(url);
      
      // Store the scraped content
      addLearningSession(
        `Web: ${new URL(url).hostname}`,
        content,
        "Conteúdo extraído de scraping web",
        url
      );
      
      // Get AI response
      const response = `✅ Conteúdo extraído e armazenado com sucesso da URL: ${url}\n\nO conhecimento foi adicionado à sua biblioteca. Você pode consultar ou pedir explicações sobre este conteúdo quando desejar.`;
      addMessage(response, 'assistant');
      
      // Clear URL field
      setUrl('');
    } catch (error) {
      toast({
        title: "Erro no scraping",
        description: error instanceof Error ? error.message : "Não foi possível extrair o conteúdo da URL",
        variant: "destructive"
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="border-t p-4">
      <div className="container max-w-3xl">
        <div className="relative">
          <Textarea
            ref={textareaRef}
            value={inputValue}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder="Envie uma mensagem..."
            className="pr-24 resize-none min-h-[60px] max-h-[200px] overflow-y-auto"
            disabled={isSubmitting}
          />
          <div className="absolute right-2 bottom-2 flex space-x-2">
            {userSettings.enableWebScraping && (
              <Dialog open={urlDialogOpen} onOpenChange={setUrlDialogOpen}>
                <DialogTrigger asChild>
                  <Button 
                    size="icon" 
                    variant="ghost"
                    disabled={isSubmitting}
                    aria-label="Adicionar URL para scraping"
                  >
                    <Link className="h-5 w-5" />
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Extrair conteúdo de URL</DialogTitle>
                  </DialogHeader>
                  <div className="grid gap-4 py-4">
                    <div className="grid gap-2">
                      <Label htmlFor="url">URL para analisar</Label>
                      <Input 
                        id="url" 
                        placeholder="https://exemplo.com/artigo"
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        autoFocus
                      />
                      <p className="text-sm text-muted-foreground">
                        O conteúdo será extraído e armazenado na memória do Olodymyr.
                      </p>
                    </div>
                  </div>
                  <DialogFooter>
                    <Button variant="outline" onClick={() => setUrlDialogOpen(false)}>
                      Cancelar
                    </Button>
                    <Button onClick={handleWebScrape} disabled={!url.trim()}>
                      Extrair Conteúdo
                    </Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            )}
            
            <Button 
              size="icon"
              onClick={handleSubmit}
              disabled={!inputValue.trim() || isSubmitting}
              aria-label="Enviar mensagem"
            >
              {isSubmitting ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                <SendHorizonal className="h-5 w-5" />
              )}
            </Button>
          </div>
        </div>
        <p className="text-xs text-center text-muted-foreground mt-2">
          O Olodymyr está em fase de desenvolvimento. As respostas são simuladas.
        </p>
      </div>
    </div>
  );
}

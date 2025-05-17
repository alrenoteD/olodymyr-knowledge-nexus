
import { useToast } from '@/components/ui/use-toast';
import { Message } from '@/types';

// Mock API for now - would be replaced with actual API calls

const MODELS = {
  'claude-haiku': {
    name: 'Claude Haiku',
    maxTokens: 4000,
    provider: 'Anthropic'
  },
  'mistral-small': {
    name: 'Mistral Small',
    maxTokens: 8000,
    provider: 'Mistral'
  }
};

// Mock chat completion function
export const getChatCompletion = async (
  messages: Message[],
  modelId: string = 'claude-haiku'
): Promise<string> => {
  // This is a mockup - in a real implementation, this would make API calls to OpenRouter
  const { toast } = useToast();
  
  try {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Simulate responses
    const lastMessage = messages[messages.length - 1];
    
    if (lastMessage.content.toLowerCase().includes('aprenda isso') || 
        lastMessage.content.toLowerCase().includes('guarde isso')) {
      return `✅ Conteúdo armazenado com sucesso na memória! 🧠\n\nPosso explicar esse conhecimento para você quando precisar. Você pode acessá-lo a qualquer momento nos seus dados de aprendizado.`;
    }
    
    if (lastMessage.content.toLowerCase().includes('olá') || 
        lastMessage.content.toLowerCase().includes('oi')) {
      return `Olá! 👋 Eu sou o Olodymyr, seu assistente de IA pessoal.\n\nPosso ajudá-lo com:\n- Responder perguntas 🤔\n- Aprender e armazenar conhecimento 🧠\n- Explicar conceitos como um professor 👨‍🏫\n- Fazer scraping de conteúdo da web 🌐\n\nComo posso ajudá-lo hoje?`;
    }
    
    return `Estou processando sua solicitação como um assistente inteligente. 🤖\n\nEste é um exemplo de resposta simulada do ${MODELS[modelId].name}. Em uma implementação real, a resposta viria da API do OpenRouter conectada ao modelo escolhido.\n\nPosso ajudar você com pesquisas, explicações como um professor, e guardar conhecimentos importantes para você. O que mais gostaria de saber? 📚`;
  } catch (error) {
    toast({
      title: "Erro na API",
      description: "Não foi possível obter resposta do modelo. Tente novamente.",
      variant: "destructive",
    });
    
    throw new Error("Falha na comunicação com a API");
  }
};

// Mock web scraping function
export const scrapeWebContent = async (url: string): Promise<string> => {
  // This is a mockup - in a real implementation, this would call a backend API
  // that uses BeautifulSoup or a similar tool to extract content
  
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  if (!url.startsWith('http')) {
    throw new Error('URL inválida. A URL deve começar com http:// ou https://');
  }
  
  return `Este é um conteúdo de exemplo extraído da URL ${url}.\n\nEm uma implementação real, este texto seria o conteúdo real da página web, processado e formatado de forma legível. O sistema usaria BeautifulSoup para extrair o conteúdo relevante, removendo elementos de navegação e anúncios.\n\nO conteúdo seria então transformado em texto simples ou HTML simplificado para armazenamento na memória do agente.`;
};

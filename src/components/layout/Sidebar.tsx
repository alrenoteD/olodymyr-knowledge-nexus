
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useAppStore } from "@/lib/store";
import { PlusCircle, MessagesSquare, BookOpen, Settings, ChevronLeft, ChevronRight, Trash2 } from "lucide-react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import { useIsMobile } from "@/hooks/use-mobile";
import { formatDistanceToNow } from "date-fns";
import { ptBR } from "date-fns/locale";

export function Sidebar() {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [newSessionName, setNewSessionName] = useState("");
  const [newSessionDesc, setNewSessionDesc] = useState("");
  const [dialogOpen, setDialogOpen] = useState(false);
  const isMobile = useIsMobile();
  
  const { 
    sessions, 
    currentSessionId, 
    createNewSession, 
    setCurrentSession,
    deleteSession
  } = useAppStore();

  const handleCreateSession = () => {
    if (newSessionName.trim()) {
      createNewSession(newSessionName, newSessionDesc);
      setNewSessionName("");
      setNewSessionDesc("");
      setDialogOpen(false);
    }
  };
  
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleCreateSession();
    }
  };

  if (isCollapsed) {
    return (
      <div className="h-full bg-sidebar border-r border-sidebar-border flex flex-col w-[60px]">
        <div className="p-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsCollapsed(false)}
            className="mb-4"
            aria-label="Expandir barra lateral"
          >
            <ChevronRight className="h-5 w-5" />
          </Button>
        </div>
        <div className="flex-1 flex flex-col items-center gap-2 p-2">
          <Button variant="ghost" size="icon">
            <MessagesSquare className="h-5 w-5" />
          </Button>
          <Button variant="ghost" size="icon">
            <BookOpen className="h-5 w-5" />
          </Button>
          <Button variant="ghost" size="icon">
            <Settings className="h-5 w-5" />
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className={cn(
      "h-full bg-sidebar border-r border-sidebar-border flex flex-col",
      isMobile ? "w-full absolute z-10" : "w-[280px]"
    )}>
      <div className="p-4 flex items-center justify-between border-b border-sidebar-border">
        <h2 className="text-lg font-semibold text-sidebar-foreground flex items-center">
          <span className="text-olodymyr-500 mr-2">◆</span> Olodymyr
        </h2>
        {!isMobile && (
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsCollapsed(true)}
            className="h-8 w-8"
            aria-label="Recolher barra lateral"
          >
            <ChevronLeft className="h-5 w-5" />
          </Button>
        )}
        {isMobile && (
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsCollapsed(true)}
            className="h-8 w-8"
            aria-label="Fechar barra lateral"
          >
            <ChevronLeft className="h-5 w-5" />
          </Button>
        )}
      </div>
      
      <div className="p-4 border-b border-sidebar-border">
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button className="w-full" size="sm">
              <PlusCircle className="mr-2 h-4 w-4" />
              Nova Conversa
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Nova Conversa</DialogTitle>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <label htmlFor="name" className="text-sm font-medium">
                  Nome
                </label>
                <Input
                  id="name"
                  value={newSessionName}
                  onChange={(e) => setNewSessionName(e.target.value)}
                  placeholder="Nova conversa"
                  onKeyDown={handleKeyPress}
                  autoFocus
                />
              </div>
              <div className="grid gap-2">
                <label htmlFor="description" className="text-sm font-medium">
                  Descrição (opcional)
                </label>
                <Textarea
                  id="description"
                  value={newSessionDesc}
                  onChange={(e) => setNewSessionDesc(e.target.value)}
                  placeholder="Sobre o que é esta conversa?"
                  rows={3}
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setDialogOpen(false)}>
                Cancelar
              </Button>
              <Button onClick={handleCreateSession} disabled={!newSessionName.trim()}>
                Criar
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
      
      <div className="p-4 border-b border-sidebar-border">
        <nav className="grid gap-2">
          <Button variant="ghost" className="justify-start">
            <MessagesSquare className="mr-2 h-5 w-5" />
            Conversas
          </Button>
          <Button variant="ghost" className="justify-start">
            <BookOpen className="mr-2 h-5 w-5" />
            Conhecimento
          </Button>
          <Button variant="ghost" className="justify-start">
            <Settings className="mr-2 h-5 w-5" />
            Configurações
          </Button>
        </nav>
      </div>
      
      <ScrollArea className="flex-1 p-4">
        <div className="grid gap-2">
          {sessions.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-4">
              Nenhuma conversa ainda.
            </p>
          ) : (
            sessions.map((session) => (
              <div
                key={session.id}
                className={cn(
                  "group flex items-center justify-between p-2 rounded-md cursor-pointer hover:bg-sidebar-accent",
                  currentSessionId === session.id && "bg-sidebar-accent"
                )}
                onClick={() => setCurrentSession(session.id)}
              >
                <div className="flex-1 truncate">
                  <h3 className="font-medium truncate">{session.name}</h3>
                  <p className="text-xs text-muted-foreground truncate">
                    {formatDistanceToNow(new Date(session.updatedAt), { 
                      addSuffix: true,
                      locale: ptBR
                    })}
                  </p>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8 opacity-0 group-hover:opacity-100"
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteSession(session.id);
                  }}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            ))
          )}
        </div>
      </ScrollArea>
    </div>
  );
}

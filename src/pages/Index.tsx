
import { useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";
import { ChatContainer } from "@/components/chat/ChatContainer";
import { cn } from "@/lib/utils";
import { useIsMobile } from "@/hooks/use-mobile";

const Index = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const isMobile = useIsMobile();
  
  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      {(sidebarOpen || !isMobile) && <Sidebar />}
      
      {/* Main Content */}
      <div className={cn("flex flex-col flex-1 h-full")}>
        <Header onMenuClick={toggleSidebar} />
        <main className="flex-1 overflow-y-auto">
          <ChatContainer />
        </main>
      </div>
    </div>
  );
};

export default Index;

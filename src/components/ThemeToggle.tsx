
import { Moon, Sun } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useAppStore } from "@/lib/store";
import { useEffect } from "react";

export function ThemeToggle() {
  const { userSettings, updateUserSettings } = useAppStore();

  useEffect(() => {
    const root = window.document.documentElement;
    
    root.classList.remove("light", "dark");
    
    if (userSettings.theme === "system") {
      const systemTheme = window.matchMedia("(prefers-color-scheme: dark)")
        .matches
        ? "dark"
        : "light";
      root.classList.add(systemTheme);
    } else {
      root.classList.add(userSettings.theme);
    }
  }, [userSettings.theme]);

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="icon" className="rounded-full">
          <Sun className="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
          <Moon className="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
          <span className="sr-only">Toggle theme</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem 
          onClick={() => updateUserSettings({ theme: "light" })}
          className={userSettings.theme === "light" ? "bg-accent" : ""}
        >
          Light
        </DropdownMenuItem>
        <DropdownMenuItem 
          onClick={() => updateUserSettings({ theme: "dark" })}
          className={userSettings.theme === "dark" ? "bg-accent" : ""}
        >
          Dark
        </DropdownMenuItem>
        <DropdownMenuItem 
          onClick={() => updateUserSettings({ theme: "system" })}
          className={userSettings.theme === "system" ? "bg-accent" : ""}
        >
          System
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

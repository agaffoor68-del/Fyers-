"use client";

import { Sun, Moon, User, Bell, Wallet, Activity } from "lucide-react";
import { useEffect, useState } from "react";

export function TopBar() {
  const [time, setTime] = useState(new Date());
  const [theme, setTheme] = useState("dark");

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const toggleTheme = () => {
    setTheme(theme === "dark" ? "light" : "dark");
    document.documentElement.classList.toggle("dark");
  };

  return (
    <header className="h-16 bg-dark-800 border-b border-border flex items-center justify-between px-6 z-40 sticky top-0">
      <div className="flex items-center gap-4">
        <button className="p-2 hover:bg-accent rounded text-muted-foreground transition-colors">
          <div className="w-5 h-5 flex items-center justify-center">
            <div className="w-3 h-3 rounded-full bg-neon-green animate-pulse" />
          </div>
        </button>
        <div className="hidden md:flex items-center gap-2 text-muted-foreground text-sm">
          <span className="font-medium">LIVE MARKET</span>
          <div className="w-1 h-1 rounded-full bg-neon-blue animate-pulse" />
          <span>NSE:SBIN-EQ ₹2,847.50 ▲ +1.2%</span>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="hidden md:flex items-center gap-3 px-4 py-2 bg-dark-900 border border-border rounded-xl">
          <Wallet className="w-4 h-4 text-neon-green" />
          <span className="font-medium text-sm">₹1,05,420.50</span>
          <span className="text-xs text-neon-green">+2.4%</span>
        </div>

        <div className="hidden md:flex items-center gap-3 px-4 py-2 bg-dark-900 border border-border rounded-xl">
          <Activity className="w-4 h-4 text-neon-blue" />
          <span className="font-medium text-sm">68.5%</span>
          <span className="text-xs text-muted-foreground">Win Rate</span>
        </div>

        <button
          onClick={toggleTheme}
          className="p-2 hover:bg-accent rounded text-muted-foreground transition-colors"
        >
          {theme === "dark" ? (
            <Sun className="w-5 h-5" />
          ) : (
            <Moon className="w-5 h-5" />
          )}
        </button>

        <button className="relative p-2 hover:bg-accent rounded text-muted-foreground transition-colors">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-neon-pink rounded-full" />
        </button>

        <div className="flex items-center gap-2 pl-4 border-l border-border">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-neon-purple to-neon-pink flex items-center justify-center text-xs font-bold text-white">
            U
          </div>
          <span className={theme === "dark" ? "text-sm font-medium text-foreground" : "text-sm font-medium text-foreground"}>
            Trader
          </span>
        </div>
      </div>
    </header>
  );
}

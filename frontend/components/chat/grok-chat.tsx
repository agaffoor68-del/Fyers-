"use client";

import { useState, useEffect, useRef } from "react";
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area";
import { Send, StopCircle, Bot } from "lucide-react";

interface Message {
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: string;
}

export function GrokChat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Hello! I'm Grok AI, your trading assistant. I have access to memory of past failures and can help you generate optimized strategies. What would you like to discuss?",
      timestamp: new Date().toLocaleTimeString(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      role: "user",
      content: input,
      timestamp: new Date().toLocaleTimeString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"}/api/grok/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input, session_id: "default" }),
      });

      const data = await response.json();
      setMessages(prev => [
        ...prev,
        { role: "assistant", content: data.response, timestamp: new Date().toLocaleTimeString() },
      ]);
    } catch (error) {
      setMessages(prev => [
        ...prev,
        { role: "assistant", content: "Error connecting to Grok AI. Please check the backend connection.", timestamp: new Date().toLocaleTimeString() },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex flex-col h-full bg-dark-900/50 border border-border rounded-xl overflow-hidden">
      <div className="bg-dark-800/50 border-b border-border p-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-neon-purple to-neon-pink flex items-center justify-center text-xs font-bold text-white">
            G
          </div>
          <div>
            <div className="text-sm font-bold text-foreground">Grok AI</div>
            <div className="text-xs text-muted-foreground">Memory-enabled</div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-neon-green animate-pulse" />
          <span className="text-xs text-neon-green font-medium">Online</span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4" ref={scrollRef}>
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex gap-3 max-w-[85%] ${msg.role === "user" ? "ml-auto flex-row-reverse" : "mr-auto"}`}
          >
            {msg.role !== "user" && (
              <div className="w-8 h-8 rounded-full bg-dark-800 flex shrink-0 items-center justify-center text-xs font-bold text-neon-purple">
                G
              </div>
            )}
            <div className={`
              px-4 py-3 rounded-2xl text-sm leading-relaxed break-words ${
                msg.role === "user"
                  ? "bg-primary text-primary-foreground rounded-tr-none"
                  : "bg-dark-800 border border-border text-foreground rounded-tl-none"
              }
            `}>
              {msg.content}
            </div>
            {msg.role === "user" && (
              <div className="w-8 h-8 rounded-full bg-dark-800 flex shrink-0 items-center justify-center text-xs font-bold text-neon-blue">
                U
              </div>
            )}
            <div className={`text-[10px] text-muted-foreground mt-1 ${msg.role === "user" ? "ml-auto" : "ml-9"}`}>
              {msg.timestamp}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex gap-3 mr-auto">
            <div className="w-8 h-8 rounded-full bg-dark-800 flex items-center justify-center text-xs font-bold text-neon-purple">G</div>
            <div className="bg-dark-800 border border-border rounded-2xl text-sm p-4 text-foreground rounded-tl-none animate-pulse">
              <div className="h-4 bg-border/30 rounded w-3/4 mb-2" />
              <div className="h-4 bg-border/30 rounded w-1/2" />
            </div>
          </div>
        )}
      </div>

      <div className="bg-dark-800/50 border-t border-border p-3">
        <div className="flex gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={1}
            className="flex-1 bg-transparent border-none text-sm text-foreground placeholder:text-muted-foreground resize-none focus:ring-0 min-h-[40px]"
            placeholder="Ask Grok about strategies, market analysis, or optimizations..."
          />
          <button
            onClick={sendMessage}
            disabled={isLoading || !input.trim()}
            className={`p-2 rounded-lg transition-colors ${
              isLoading || !input.trim()
                ? "bg-dark-800 text-muted-foreground cursor-not-allowed"
                : "bg-primary text-primary-foreground hover:bg-primary/90"
            }`}
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}

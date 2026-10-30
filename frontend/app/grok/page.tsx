"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Bot,
  MessageSquare,
  Zap,
  Brain,
  Activity,
  Send,
  Copy,
  TrendingUp,
  AlertTriangle,
  Code,
} from "lucide-react";

interface AIMessage {
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: string;
}

interface StrategyJSON {
  strategy_name: string;
  description: string;
  indicators: Array<{ name: string; [key: string]: any }>;
  rules: string;
  stop_loss_pct: number;
  take_profit_pct: number;
}

export default function GrokPage() {
  const [messages, setMessages] = useState<AIMessage[]>([
    {
      role: "assistant",
      content:
        "Hello! I'm Grok AI, your trading assistant with access to 100+ technical indicators. Ask me to analyze any symbol or generate a strategy.",
      timestamp: new Date().toLocaleTimeString(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [generatedStrategy, setGeneratedStrategy] = useState<StrategyJSON | null>(null);
  const [showStrategyPanel, setShowStrategyPanel] = useState(false);

  const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMsg: AIMessage = {
      role: "user",
      content: input,
      timestamp: new Date().toLocaleTimeString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);

    try {
      const res = await fetch(`${BACKEND_URL}/api/grok/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input, session_id: "default" }),
      });
      const data = await res.json();

      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.response, timestamp: new Date().toLocaleTimeString() },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Error connecting to Grok AI. Please check backend connection.",
          timestamp: new Date().toLocaleTimeString(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const generateStrategy = async () => {
    setIsLoading(true);
    try {
      const res = await fetch(`${BACKEND_URL}/api/grok/generate-strategy`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_request: input || "Generate a multi-indicator trading strategy",
          symbol: "NSE:SBIN-EQ",
          days: 30,
          resolution: "5",
        }),
      });
      const data = await res.json();

      if (data.success && data.strategy) {
        setGeneratedStrategy(data.strategy as StrategyJSON);
        setShowStrategyPanel(true);

        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: `I've generated a new strategy: "${data.strategy.strategy_name}". Check the strategy panel on the right for full details including indicators, rules, and risk parameters.`,
            timestamp: new Date().toLocaleTimeString(),
          },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: `Failed to generate strategy: ${data.error || "Unknown error"}`,
            timestamp: new Date().toLocaleTimeString(),
          },
        ]);
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Error generating strategy. Please try again.",
          timestamp: new Date().toLocaleTimeString(),
        },
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
    <div className="flex flex-col h-full gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Grok AI</h1>
          <p className="text-muted-foreground">
            AI-powered strategy generation with 100+ technical indicators
          </p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1 rounded bg-dark-900 border border-border text-xs">
          <div className="w-2 h-2 rounded-full bg-neon-green animate-pulse" />
          <span className="text-neon-green font-medium">Online</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-200px)] min-h-[600px]">
        {/* Chat Panel */}
        <Card className="lg:col-span-2 glass flex flex-col h-full">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2">
              <Bot className="w-5 h-5" />
              AI Conversation
            </CardTitle>
          </CardHeader>
          <CardContent className="flex-1 flex flex-col p-0">
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex gap-3 max-w-[85%] ${
                    msg.role === "user" ? "ml-auto flex-row-reverse" : "mr-auto"
                  }`}
                >
                  {msg.role !== "user" && (
                    <div className="w-8 h-8 rounded-full bg-dark-800 flex shrink-0 items-center justify-center text-xs font-bold text-neon-purple">
                      G
                    </div>
                  )}
                  <div className={`px-4 py-3 rounded-2xl text-sm leading-relaxed break-words ${
                    msg.role === "user"
                      ? "bg-primary text-primary-foreground rounded-tr-none"
                      : "bg-dark-800 border border-border text-foreground rounded-tl-none"
                  }`}>
                    {msg.content}
                  </div>
                  {msg.role === "user" && (
                    <div className="w-8 h-8 rounded-full bg-dark-800 flex shrink-0 items-center justify-center text-xs font-bold text-neon-blue">
                      U
                    </div>
                  )}
                </div>
              ))}
              {isLoading && (
                <div className="flex gap-3 mr-auto">
                  <div className="w-8 h-8 rounded-full bg-dark-800 flex items-center justify-center text-xs font-bold text-neon-purple">
                    G
                  </div>
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
                  placeholder="Ask Grok: 'Analyze NIFTY with RSI and S&R' or 'Generate a scalping strategy'"
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
              <div className="flex gap-2 mt-2">
                <button
                  onClick={generateStrategy}
                  disabled={isLoading}
                  className="flex-1 py-2 bg-gradient-to-r from-neon-purple to-neon-pink text-white rounded-lg hover:opacity-90 transition-all text-sm font-medium flex items-center justify-center gap-2"
                >
                  <TrendingUp className="w-4 h-4" />
                  Generate Strategy
                </button>
                <button
                  onClick={() => setInput("Analyze NIFTY with RSI and S&R levels")}
                  className="w-10 py-2 bg-dark-900 rounded hover:bg-dark-800 transition-colors text-muted-foreground"
                  title="Quick Example"
                >
                  <Code className="w-4 h-4" />
                </button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Strategy Panel */}
        <Card className="glass flex flex-col h-full">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2">
              <Brain className="w-5 h-5" />
              Generated Strategy
            </CardTitle>
            <button
              onClick={() => setShowStrategyPanel(false)}
              className="p-1 hover:bg-dark-700 rounded text-muted-foreground"
            >
              <span className="text-sm font-bold">✕</span>
            </button>
          </CardHeader>
          <CardContent className="flex-1 overflow-y-auto p-4">
            {!generatedStrategy ? (
              <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
                <Brain className="w-12 h-12 opacity-20 mb-4" />
                <p>No strategy generated yet</p>
                <p className="text-xs mt-2">Click "Generate Strategy" to create one</p>
              </div>
            ) : (
              <div className="space-y-4">
                <div>
                  <h3 className="text-lg font-bold text-foreground">{generatedStrategy.strategy_name}</h3>
                  <p className="text-sm text-muted-foreground">{generatedStrategy.description}</p>
                </div>

                <div className="p-3 rounded bg-dark-800 border border-border">
                  <h4 className="text-xs font-bold text-neon-blue uppercase mb-2">Indicators Used</h4>
                  <div className="flex flex-wrap gap-2">
                    {generatedStrategy.indicators.map((ind, idx) => (
                      <span
                        key={idx}
                        className="px-2 py-1 rounded bg-dark-900 border border-border/50 text-xs text-neon-green"
                      >
                        {ind.name} {Object.entries(ind).filter(([k]) => k !== "name").map(([k, v]) => `${k}=${v}`).join(", ")}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="p-3 rounded bg-dark-800 border border-border">
                  <h4 className="text-xs font-bold text-neon-purple uppercase mb-2">Trading Rules</h4>
                  <div className="font-mono text-xs text-foreground bg-dark-900 p-3 rounded border border-border/30">
                    {generatedStrategy.rules}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 rounded bg-dark-900 border border-border">
                    <p className="text-xs text-muted-foreground">Stop Loss</p>
                    <p className="text-sm font-bold text-destructive">{generatedStrategy.stop_loss_pct}%</p>
                  </div>
                  <div className="p-3 rounded bg-dark-900 border border-border">
                    <p className="text-xs text-muted-foreground">Take Profit</p>
                    <p className="text-sm font-bold text-neon-green">{generatedStrategy.take_profit_pct}%</p>
                  </div>
                </div>

                <div className="pt-3 border-t border-border/50">
                  <button
                    className="w-full py-2 bg-neon-green text-dark-900 rounded-lg hover:bg-neon-green/90 transition-colors text-sm font-medium flex items-center justify-center gap-2"
                  >
                    <Zap className="w-4 h-4" />
                    Deploy to Paper Trading
                  </button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[
          {
            title: "Multi-Indicator Optimizer",
            desc: "Run Grok with 100+ indicators to generate optimized strategies",
            icon: TrendingUp,
            color: "bg-gradient-to-r from-neon-purple to-neon-pink",
          },
          {
            title: "S&R Analysis",
            desc: "View Support & Resistance levels for any symbol",
            icon: AlertTriangle,
            color: "bg-gradient-to-r from-neon-blue to-neon-purple",
          },
          {
            title: "AI Memory",
            desc: "Review Grok's past failures and lessons learned",
            icon: Brain,
            color: "bg-gradient-to-r from-neon-pink to-neon-green",
          },
        ].map((item) => (
          <Card key={item.title} className="glass p-6 cursor-pointer hover:border-border/50 transition-colors">
            <div className="flex items-center justify-between mb-4">
              <item.icon className={`w-6 h-6 ${item.color.split(" ")[0] === "bg-gradient" ? "text-white" : "text-neon-blue"}`} />
            </div>
            <h3 className="font-semibold text-lg">{item.title}</h3>
            <p className="text-sm text-muted-foreground">{item.desc}</p>
          </Card>
        ))}
      </div>
    </div>
  );
}

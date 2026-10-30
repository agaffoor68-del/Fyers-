"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Brain,
  AlertTriangle,
  Clock,
  RefreshCw,
  Search,
  TrendingDown,
} from "lucide-react";

interface AILearningLog {
  id: number;
  strategy_used: string;
  reason_failed: string;
  mistake_context: string;
  lesson_learned: string;
  timestamp: string;
}

export default function BrainPage() {
  const [failures, setFailures] = useState<AILearningLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");

  const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

  useEffect(() => {
    fetchFailures();
  }, []);

  const fetchFailures = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${BACKEND_URL}/api/grok/memory`);
      const data = await res.json();
      setFailures(data.failures || []);
    } catch (err) {
      console.error("Failed to fetch AI memory:", err);
    } finally {
      setLoading(false);
    }
  };

  const reasonColors: Record<string, string> = {
    "High Slippage": "bg-orange-500/20 text-orange-400 border-orange-500/30",
    "False Breakout": "bg-red-500/20 text-red-400 border-red-500/30",
    "Stop Loss Hit": "bg-red-500/20 text-red-400 border-red-500/30",
    "Low Volatility Expansion": "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
  };

  const filtered = failures.filter(
    (f) =>
      f.strategy_used.toLowerCase().includes(searchQuery.toLowerCase()) ||
      f.reason_failed.toLowerCase().includes(searchQuery.toLowerCase()) ||
      f.mistake_context.toLowerCase().includes(searchQuery.toLowerCase()) ||
      f.lesson_learned.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-neon-green"></div>
        <p className="mt-4 text-muted-foreground">Loading AI memory...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Grok Brain</h1>
          <p className="text-muted-foreground">
            AI Memory & Learning System - Transparency into Grok's failures and improvements
          </p>
        </div>
        <button
          onClick={fetchFailures}
          className="flex items-center gap-2 px-3 py-1.5 rounded bg-dark-900 border border-border hover:bg-dark-800 transition-colors text-sm"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <Card className="glass">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-muted-foreground uppercase tracking-wider">Total Failures</p>
                <p className="text-2xl font-bold">{failures.length}</p>
              </div>
              <Brain className="w-8 h-8 text-neon-purple opacity-20" />
            </div>
          </CardContent>
        </Card>
        <Card className="glass">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-muted-foreground uppercase tracking-wider">Lessons Learned</p>
                <p className="text-2xl font-bold">{failures.length}</p>
              </div>
              <AlertTriangle className="w-8 h-8 text-neon-orange opacity-20" />
            </div>
          </CardContent>
        </Card>
        <Card className="glass">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-muted-foreground uppercase tracking-wider">Improvement Rate</p>
                <p className="text-2xl font-bold text-neon-green">+12%</p>
              </div>
              <Clock className="w-8 h-8 text-neon-blue opacity-20" />
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="glass">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="w-5 h-5" />
            Failed Strategies & Lessons
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-4">
            <div className="relative">
              <Search className="absolute left-3 top-3 w-4 h-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search failures by strategy, reason, or lesson..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-3 py-2 rounded bg-dark-800 border border-border text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-border text-xs uppercase text-muted-foreground">
                  <th className="pb-3 font-semibold">Strategy</th>
                  <th className="pb-3 font-semibold">Reason Failed</th>
                  <th className="pb-3 font-semibold">Mistake Context</th>
                  <th className="pb-3 font-semibold">Lesson Learned</th>
                  <th className="pb-3 font-semibold">Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/50">
                {filtered.map((failure) => (
                  <tr key={failure.id} className="hover:bg-dark-800/50 transition-colors group">
                    <td className="py-3 text-sm font-medium">
                      {failure.strategy_used}
                    </td>
                    <td className="py-3 text-sm">
                      <span className={`px-2 py-1 rounded text-xs font-bold border ${reasonColors[failure.reason_failed] || "bg-muted/20 text-muted-foreground border-border/30"}`}>
                        {failure.reason_failed}
                      </span>
                    </td>
                    <td className="py-3 text-sm text-muted-foreground max-w-xs truncate">
                      {failure.mistake_context}
                    </td>
                    <td className="py-3 text-sm text-neon-green/90 max-w-xs truncate">
                      {failure.lesson_learned}
                    </td>
                    <td className="py-3 text-xs text-muted-foreground">
                      {new Date(failure.timestamp).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
                {filtered.length === 0 && (
                  <tr>
                    <td colSpan={5} className="py-8 text-center text-muted-foreground">
                      No failures recorded yet. Grok is learning from first principles.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="glass p-6">
          <div className="flex items-center gap-3 mb-4">
            <Code className="w-5 h-5 text-neon-blue" />
            <h3 className="font-semibold text-lg">How Memory Works</h3>
          </div>
          <ul className="space-y-3 text-sm text-muted-foreground">
            <li className="flex items-center gap-2">
              <span className="text-neon-green">✓</span>
              Grok saves every failed paper trade to AILearningLog
            </li>
            <li className="flex items-center gap-2">
              <span className="text-neon-green">✓</span>
              Before generating new strategies, Grok reads the last 5 failures
            </li>
            <li className="flex items-center gap-2">
              <span className="text-neon-green">✓</span>
              Failures are injected into the System Prompt as "DO NOT REPEAT" warnings
            </li>
            <li className="flex items-center gap-2">
              <span className="text-neon-green">✓</span>
              Each failure includes market conditions, strategy used, and lesson learned
            </li>
          </ul>
        </Card>

        <Card className="glass p-6">
          <div className="flex items-center gap-3 mb-4">
            <AlertTriangle className="w-5 h-5 text-neon-orange" />
            <h3 className="font-semibold text-lg">Feedback Loop</h3>
          </div>
          <div className="space-y-4">
            {[
              { num: 1, title: "Trade Fails", desc: "Paper trade hits stop-loss or generates negative PnL" },
              { num: 2, title: "Log to Memory", desc: "AILearningLog captures mistake context and reason" },
              { num: 3, title: "Inject into Prompt", desc: "Grok reads failures before generating new strategies" },
              { num: 4, title: "Improve", desc: "New strategies avoid past mistakes" },
            ].map((step) => (
              <div key={step.num} className="flex items-start gap-3">
                <div className="w-8 h-8 rounded bg-dark-900 flex shrink-0 items-center justify-center text-xs font-bold text-red-400">
                  {step.num}
                </div>
                <div>
                  <h4 className="font-medium text-sm">{step.title}</h4>
                  <p className="text-xs text-muted-foreground">{step.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}

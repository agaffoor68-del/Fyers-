"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  HardHat,
  Play,
  Deployed,
  Monitor,
  Bot,
  TrendingUp,
  TrendingDown,
  MoreHorizontal,
  Search,
  Code,
  AlertTriangle,
  Info,
} from "lucide-react";

interface StrategyIndicator {
  name: string;
  params: Record<string, any>;
}

interface Strategy {
  id: number;
  name: string;
  type: string;
  winRate: number;
  totalTrades: number;
  status: "Paper" | "Live" | "Draft";
  pnl: number;
  description: string;
  indicators?: StrategyIndicator[];
  entryLogic?: string;
  exitLogic?: string;
  aiGenerated?: boolean;
}

const strategies: Strategy[] = [
  {
    id: 1,
    name: "EMA Crossover 9/21",
    type: "Trend Following",
    winRate: 68.5,
    totalTrades: 142,
    status: "Live",
    pnl: 12450.50,
    description: "Fast EMA crossover strategy for intraday trend following",
    indicators: [
      { name: "EMA", params: { length: 9 } },
      { name: "EMA", params: { length: 21 } },
    ],
    entryLogic: "EMA_9 > EMA_21",
    exitLogic: "EMA_9 < EMA_21",
    aiGenerated: false,
  },
  {
    id: 2,
    name: "RSI Mean Reversion",
    type: "Mean Reversion",
    winRate: 54.2,
    totalTrades: 89,
    status: "Paper",
    pnl: -2340.30,
    description: "Buys oversold, sells overbought with Bollinger Band confirmation",
    indicators: [
      { name: "RSI", params: { length: 14 } },
      { name: "BBANDS", params: { length: 20, std: 2.0 } },
    ],
    entryLogic: "RSI_14 < 30 AND close < BBL_20_2.0",
    exitLogic: "RSI_14 > 70 OR close > BBU_20_2.0",
    aiGenerated: false,
  },
  {
    id: 3,
    name: "Bollinger Squeeze",
    type: "Volatility Breakout",
    winRate: 61.8,
    totalTrades: 67,
    status: "Draft",
    pnl: 0,
    description: "Breakout entries on low volatility expansion",
    indicators: [
      { name: "BBANDS", params: { length: 20, std: 2.0 } },
      { name: "ATR", params: { length: 14 } },
    ],
    entryLogic: "close > BBU_20_2.0 AND ATR_14 > ATR_14.shift(1)",
    exitLogic: "close < BBM_20_2.0",
    aiGenerated: false,
  },
  {
    id: 4,
    name: "Grok AI Optimized",
    type: "AI-Generated",
    winRate: 72.1,
    totalTrades: 203,
    status: "Paper",
    pnl: 8950.75,
    description: "AI-generated strategy with memory-injected learning",
    indicators: [
      { name: "RSI", params: { length: 14 } },
      { name: "MACD", params: { fast: 12, slow: 26, signal: 9 } },
      { name: "EMA", params: { length: 50 } },
      { name: "ATR", params: { length: 14 } },
    ],
    entryLogic: "RSI_14 < 35 AND MACD_12_26_9 > MACDs_12_26_9 AND close > EMA_50",
    exitLogic: "RSI_14 > 65 OR MACD_12_26_9 < MACDs_12_26_9",
    stopLossPct: 2.0,
    takeProfitPct: 4.0,
    aiGenerated: true,
  },
];

const indicatorDescriptions: Record<string, string> = {
  RSI: "Relative Strength Index - Momentum oscillator measuring overbought/oversold conditions",
  EMA: "Exponential Moving Average - Trend-following indicator with more weight on recent prices",
  SMA: "Simple Moving Average - Arithmetic mean of prices over a period",
  MACD: "Moving Average Convergence Divergence - Trend-following momentum indicator",
  BBANDS: "Bollinger Bands - Volatility bands placed above and below a moving average",
  ATR: "Average True Range - Volatility indicator measuring market volatility",
  STOCH: "Stochastic Oscillator - Momentum indicator comparing close to price range",
  ADX: "Average Directional Index - Trend strength indicator",
  OBV: "On-Balance Volume - Volume-based indicator measuring buying/selling pressure",
  VWAP: "Volume Weighted Average Price - Average price weighted by volume",
};

export default function StrategiesPage() {
  const [viewMode, setViewMode] = useState<"grid" | "table">("grid");
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedStrategy, setSelectedStrategy] = useState<Strategy | null>(null);

  const statusColors: Record<string, string> = {
    Paper: "bg-neon-blue/20 text-neon-blue border-neon-blue/30",
    Live: "bg-neon-green/20 text-neon-green border-neon-green/30",
    Draft: "bg-muted/20 text-muted-foreground border-border/30",
  };

  const openModal = (strategy: Strategy) => {
    setSelectedStrategy(strategy);
    setModalOpen(true);
  };

  const closeModal = () => {
    setModalOpen(false);
    setSelectedStrategy(null);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Strategy Lab</h1>
          <p className="text-muted-foreground">
            Manage, backtest, and deploy your trading strategies
          </p>
        </div>
        <div className="flex gap-1">
          <button
            onClick={() => setViewMode("grid")}
            className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${viewMode === "grid" ? "bg-primary text-primary-foreground" : "bg-dark-900 text-muted-foreground border border-border"}`}
          >
            Grid
          </button>
          <button
            onClick={() => setViewMode("table")}
            className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${viewMode === "table" ? "bg-primary text-primary-foreground" : "bg-dark-900 text-muted-foreground border border-border"}`}
          >
            Table
          </button>
        </div>
      </div>

      {viewMode === "grid" ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {strategies.map((strategy) => (
            <Card
              key={strategy.id}
              className="glass hover:border-neon-green/30 transition-all group cursor-pointer"
              onClick={() => strategy.aiGenerated ? openModal(strategy) : undefined}
            >
              <CardContent className="p-5">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <div className="w-10 h-10 rounded-lg bg-dark-800 flex items-center justify-center">
                      {strategy.aiGenerated ? (
                        <Bot className="w-5 h-5 text-neon-purple" />
                      ) : (
                        <HardHat className="w-5 h-5 text-neon-blue" />
                      )}
                    </div>
                    <span className={`text-xs font-bold uppercase tracking-wider ${statusColors[strategy.status]}`}>
                      {strategy.status}
                    </span>
                    {strategy.aiGenerated && (
                      <span className="px-2 py-0.5 rounded bg-neon-purple/20 text-neon-purple text-[10px] font-bold border border-neon-purple/30">
                        AI
                      </span>
                    )}
                  </div>
                  <MoreHorizontal className="w-4 h-4 text-muted-foreground hover:text-foreground" />
                </div>

                <h3 className="text-lg font-bold mb-1">{strategy.name}</h3>
                <p className="text-xs text-muted-foreground mb-4">
                  {strategy.type} · {strategy.description}
                </p>

                {strategy.indicators && strategy.indicators.length > 0 && (
                  <div className="flex flex-wrap gap-1 mb-3">
                    {strategy.indicators.map((ind, idx) => (
                      <span
                        key={idx}
                        className="px-2 py-1 rounded bg-dark-800 border border-border/50 text-xs text-muted-foreground"
                      >
                        {ind.name}{ind.params.length ? `(${ind.params.length})` : ""}
                      </span>
                    ))}
                  </div>
                )}

                <div className="grid grid-cols-3 gap-3 mb-4">
                  <div className="p-2 rounded bg-dark-900/50">
                    <div className="text-xs text-muted-foreground">Win Rate</div>
                    <div className="text-sm font-bold text-neon-green">{strategy.winRate}%</div>
                  </div>
                  <div className="p-2 rounded bg-dark-900/50">
                    <div className="text-xs text-muted-foreground">Trades</div>
                    <div className="text-sm font-bold">{strategy.totalTrades}</div>
                  </div>
                  <div className="p-2 rounded bg-dark-900/50">
                    <div className="text-xs text-muted-foreground">PnL</div>
                    <div className={`text-sm font-bold ${strategy.pnl >= 0 ? "text-neon-green" : "text-destructive"}`}>
                      {strategy.pnl >= 0 ? "+" : ""}₹{strategy.pnl.toLocaleString()}
                    </div>
                  </div>
                </div>

                <div className="flex gap-2">
                  {strategy.status === "Draft" ? (
                    <button className="flex-1 py-2 bg-primary text-primary-foreground rounded hover:bg-primary/90 transition-colors text-sm font-medium">
                      Deploy Paper
                    </button>
                  ) : (
                    <button className="flex-1 py-2 bg-neon-green text-dark-900 rounded hover:bg-neon-green/90 transition-colors text-sm font-medium">
                      {strategy.status === "Live" ? "Monitor" : "Trade Paper"}
                    </button>
                  )}
                  <button className="w-10 py-2 bg-dark-900 rounded hover:bg-dark-800 transition-colors text-muted-foreground">
                    <Play className="w-4 h-4" />
                  </button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card className="glass">
          <CardHeader>
            <CardTitle>Strategy Overview</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-border text-xs uppercase text-muted-foreground">
                    <th className="pb-3 font-semibold">Strategy</th>
                    <th className="pb-3 font-semibold">Type</th>
                    <th className="pb-3 font-semibold">Indicators</th>
                    <th className="pb-3 font-semibold">Win Rate</th>
                    <th className="pb-3 font-semibold">Trades</th>
                    <th className="pb-3 font-semibold">PnL</th>
                    <th className="pb-3 font-semibold">Status</th>
                    <th className="pb-3 font-semibold text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/50">
                  {strategies.map((strategy) => (
                    <tr
                      key={strategy.id}
                      className="hover:bg-dark-800/50 transition-colors cursor-pointer"
                      onClick={() => strategy.aiGenerated ? openModal(strategy) : undefined}
                    >
                      <td className="py-3 font-medium">{strategy.name}</td>
                      <td className="py-3 text-sm text-muted-foreground">{strategy.type}</td>
                      <td className="py-3 text-sm">
                        {strategy.indicators?.map((ind, idx) => (
                          <span key={idx} className="block text-xs text-neon-blue/80">{ind.name}</span>
                        )) || <span className="text-xs text-muted-foreground">-</span>}
                      </td>
                      <td className="py-3 text-sm">
                        <span className={`font-bold ${strategy.winRate >= 60 ? "text-neon-green" : "text-muted-foreground"}`}>
                          {strategy.winRate}%
                        </span>
                      </td>
                      <td className="py-3 text-sm">{strategy.totalTrades}</td>
                      <td className="py-3 text-sm">
                        <span className={`font-bold ${strategy.pnl >= 0 ? "text-neon-green" : "text-destructive"}`}>
                          {strategy.pnl >= 0 ? "+" : ""}₹{strategy.pnl.toLocaleString()}
                        </span>
                      </td>
                      <td className="py-3 text-sm">
                        <span className={`px-2 py-1 rounded text-xs font-bold border ${statusColors[strategy.status]}`}>
                          {strategy.status}
                        </span>
                      </td>
                      <td className="py-3 text-right">
                        <div className="flex items-center gap-1">
                          <button
                            className="p-1.5 hover:bg-dark-800 rounded text-muted-foreground"
                            title="Deploy Paper"
                            onClick={(e) => e.stopPropagation()}
                          >
                            <Deployed className="w-4 h-4" />
                          </button>
                          <button
                            className="p-1.5 hover:bg-dark-800 rounded text-muted-foreground"
                            title="Deploy Live"
                            onClick={(e) => e.stopPropagation()}
                          >
                            <Monitor className="w-4 h-4" />
                          </button>
                          {strategy.aiGenerated && (
                            <button
                              className="p-1.5 hover:bg-dark-800 rounded text-neon-purple"
                              title="View Details"
                              onClick={(e) => {
                                e.stopPropagation();
                                openModal(strategy);
                              }}
                            >
                              <Info className="w-4 h-4" />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2 glass p-6">
          <h3 className="font-semibold text-lg mb-4">AI Strategy Generator</h3>
          <div className="space-y-4">
            <div className="p-4 rounded bg-dark-900 border border-border">
              <p className="text-sm text-muted-foreground mb-3">
                Ask Grok to generate a new strategy based on your requirements:
              </p>
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="e.g., 'Generate a scalping strategy for NIFTY 50'"
                  className="flex-1 px-3 py-2 rounded bg-dark-800 border border-border text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                />
                <button className="px-4 py-2 bg-primary text-primary-foreground rounded hover:bg-primary/90 transition-colors text-sm font-medium">
                  Generate
                </button>
              </div>
            </div>
            <div className="p-4 rounded bg-dark-900/50 border border-border/30">
              <h4 className="text-sm font-semibold mb-2">Recent AI Suggestions</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex justify-between">
                  <span>Momentum Breakout (NIFTY)</span>
                  <span className="text-neon-green">Win Rate: 74%</span>
                </li>
                <li className="flex justify-between">
                  <span>Mean Reversion (BANKNIFTY)</span>
                  <span className="text-neon-green">Win Rate: 69%</span>
                </li>
              </ul>
            </div>
          </div>
        </Card>

        <Card className="glass p-6">
          <h3 className="font-semibold text-lg mb-4">Quick Deploy</h3>
          <div className="space-y-3">
            <button className="w-full py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors font-medium flex items-center justify-center gap-2">
              <Play className="w-4 h-4" />
              Deploy Selected to Paper
            </button>
            <button className="w-full py-3 bg-dark-900 border border-border text-muted-foreground rounded-lg hover:bg-dark-800 transition-colors font-medium flex items-center justify-center gap-2">
              <Deployed className="w-4 h-4" />
              Deploy Selected to Live
            </button>
            <button className="w-full py-3 bg-dark-900 border border-border text-muted-foreground rounded-lg hover:bg-dark-800 transition-colors font-medium flex items-center justify-center gap-2">
              <TrendingUp className="w-4 h-4" />
              Backtest All Strategies
            </button>
          </div>
        </Card>
      </div>

      {/* Strategy Details Modal */}
      {modalOpen && selectedStrategy && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <div className="bg-dark-900 border border-border rounded-xl w-full max-w-2xl p-6 shadow-2xl animate-in fade-in slide-in-from-top-4 duration-300">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-2xl font-bold text-foreground">
                  {selectedStrategy.name}
                </h2>
                <p className="text-sm text-muted-foreground">
                  {selectedStrategy.aiGenerated ? "AI-Generated Strategy" : "Manual Strategy"}
                </p>
              </div>
              <button
                onClick={closeModal}
                className="w-8 h-8 rounded-full bg-dark-800 hover:bg-dark-700 flex items-center justify-center text-muted-foreground hover:text-foreground transition-colors"
              >
                <span className="text-sm font-bold">✕</span>
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div className="p-4 rounded bg-dark-800 border border-border">
                  <h4 className="text-sm font-semibold text-neon-blue mb-3 flex items-center gap-2">
                    <Code className="w-4 h-4" /> Strategy Logic
                  </h4>
                  <div className="font-mono text-xs text-muted-foreground bg-dark-900 p-3 rounded border border-border/30">
                    <p className="mb-2"><strong>Entry:</strong> {selectedStrategy.entryLogic || "N/A"}</p>
                    <p><strong>Exit:</strong> {selectedStrategy.exitLogic || "N/A"}</p>
                  </div>
                  {selectedStrategy.stopLossPct !== undefined && (
                    <div className="mt-3 flex gap-4 text-xs text-muted-foreground">
                      <span>Stop Loss: {selectedStrategy.stopLossPct}%</span>
                      <span>Take Profit: {selectedStrategy.takeProfitPct}%</span>
                    </div>
                  )}
                </div>

                <div className="p-4 rounded bg-dark-800 border border-border">
                  <h4 className="text-sm font-semibold text-neon-purple mb-3 flex items-center gap-2">
                    <Info className="w-4 h-4" /> Strategy Metrics
                  </h4>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Win Rate</span>
                      <span className="text-neon-green font-medium">{selectedStrategy.winRate}%</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Total Trades</span>
                      <span className="text-foreground font-medium">{selectedStrategy.totalTrades}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">PnL</span>
                      <span className={`font-medium ${selectedStrategy.pnl >= 0 ? "text-neon-green" : "text-destructive"}`}>
                        {selectedStrategy.pnl >= 0 ? "+" : ""}₹{selectedStrategy.pnl.toLocaleString()}
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Status</span>
                      <span className={`px-2 py-0.5 rounded text-xs font-bold border ${statusColors[selectedStrategy.status]}`}>
                        {selectedStrategy.status}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <div className="p-4 rounded bg-dark-800 border border-border">
                  <h4 className="text-sm font-semibold text-neon-green mb-3 flex items-center gap-2">
                    <Search className="w-4 h-4" /> Indicators Used
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {selectedStrategy.indicators?.map((ind, idx) => (
                      <div key={idx} className="p-3 rounded bg-dark-900/50 border border-border/50">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-xs font-bold text-neon-green">{ind.name}</span>
                          <span className="text-[10px] text-muted-foreground">pandas_ta</span>
                        </div>
                        <div className="text-xs text-muted-foreground">
                          {Object.entries(ind.params).map(([key, val]) => (
                            <div key={key} className="flex justify-between">
                              <span>{key}</span>
                              <span className="text-foreground font-medium">{val}</span>
                            </div>
                          ))}
                        </div>
                        <div className="mt-1">
                          <span className="text-[10px] text-muted-foreground italic">
                            {indicatorDescriptions[ind.name] || "Technical indicator"}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {selectedStrategy.aiGenerated && (
                  <div className="p-4 rounded bg-dark-800 border border-border">
                    <h4 className="text-sm font-semibold text-neon-pink mb-3 flex items-center gap-2">
                      <AlertTriangle className="w-4 h-4" /> AI Notes
                    </h4>
                    <p className="text-sm text-muted-foreground">
                      This strategy was generated by Grok AI using memory from
                      past failures. The indicator parameters were selected
                      based on historical performance and market conditions.
                    </p>
                    <div className="mt-3 pt-3 border-t border-border/50">
                      <button className="w-full py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors text-sm font-medium flex items-center justify-center gap-2">
                        <Play className="w-4 h-4" />
                        Deploy to Paper Trading
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>

            <div className="mt-6 flex justify-end gap-2">
              <button
                onClick={closeModal}
                className="px-4 py-2 bg-dark-800 border border-border rounded-lg hover:bg-dark-700 transition-colors text-sm"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

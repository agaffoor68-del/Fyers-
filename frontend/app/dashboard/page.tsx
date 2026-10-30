"use client";

import { useEffect, useState, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Line,
  LineChart,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from "recharts";
import {
  Search,
  Check,
  ChevronDown,
  Plus,
  TrendingUp,
  TrendingDown,
  Activity,
  Bot,
  Brain,
  HardHat,
  Monitor,
  Cpu,
  LayoutGrid,
  Candle,
} from "lucide-react";

interface IndicatorItem {
  name: string;
  category: string;
  default_params: Record<string, any>;
  overlay: boolean;
  description: string;
}

interface CandleData {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  [key: string]: any;
}

interface SRLevel {
  price: number;
  type: "support" | "resistance";
  strength: number;
}

interface SRElevels {
  pivot_points: Record<string, any>;
  fibonacci: Record<string, any>;
  local_resistance: SRLevel[];
  local_support: SRLevel[];
}

const INDICATOR_CATEGORIES: Record<string, string[]> = {
  Trend: ["sma", "ema", "macd", "adx", "supertrend", "vwap"],
  Momentum: ["rsi", "stoch", "cci", "mfi", "tsi"],
  Volatility: ["bbands", "atr", "kc", "donchian"],
  Volume: ["obv", "vwap", "mfi", "adosc"],
  "Support_Resistance": ["pivot_points", "fibonacci", "local_pivots"],
  Candlestick: ["cdl_doji", "cdl_hammer", "cdl_engulfing"],
};

export default function DashboardPage() {
  const [indicators, setIndicators] = useState<IndicatorItem[]>([]);
  const [selectedIndicators, setSelectedIndicators] = useState<string[]>([]);
  const [candles, setCandles] = useState<CandleData[]>([]);
  const [srLevels, setSRLevels] = useState<SRElevels>({
    pivot_points: {},
    fibonacci: {},
    local_resistance: [],
    local_support: [],
  });
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedSymbol, setSelectedSymbol] = useState("NSE:SBIN-EQ");

  // Fetch available indicators
  useEffect(() => {
    fetchIndicators();
  }, []);

  // Fetch chart data when indicators or symbol change
  useEffect(() => {
    fetchChartData();
  }, [selectedIndicators, selectedSymbol]);

  const fetchIndicators = async () => {
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"}/api/indicators/list`
      );
      const data = await res.json();
      const allIndicators: IndicatorItem[] = [];
      Object.entries(data.categories || {}).forEach(([category, items]) => {
        (items as IndicatorItem[]).forEach((item) => {
          allIndicators.push({ ...item, category });
        });
      });
      setIndicators(allIndicators);
    } catch (err) {
      console.error("Failed to fetch indicators:", err);
    }
  };

  const fetchChartData = async () => {
    setLoading(true);
    try {
      const indParams = indicators
        .filter((i) => selectedIndicators.includes(i.name))
        .map((i) => ({ name: i.name, params: i.default_params }));

      const res = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"}/api/indicators/chart-data`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            symbol: selectedSymbol,
            resolution: "5",
            days: 30,
            indicators: indParams,
          }),
        }
      );
      const data = await res.json();
      setCandles(data.candles || []);
      setSRLevels(data.sr_levels || {
        pivot_points: {},
        fibonacci: {},
        local_resistance: [],
        local_support: [],
      });
    } catch (err) {
      console.error("Failed to fetch chart data:", err);
    } finally {
      setLoading(false);
    }
  };

  const toggleIndicator = (name: string) => {
    setSelectedIndicators((prev) =>
      prev.includes(name) ? prev.filter((n) => n !== n) : [...prev, name]
    );
  };

  const filteredIndicators = indicators.filter(
    (ind) =>
      ind.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      ind.category.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const overlayIndicators = selectedIndicators.filter(
    (name) => indicators.find((i) => i.name === name)?.overlay
  );
  const subChartIndicators = selectedIndicators.filter(
    (name) => !indicators.find((i) => i.name === name)?.overlay
  );

  // Extract S&R price levels for chart lines
  const supportPrices: number[] = [
    ...Object.values(srLevels.pivot_points || {}).filter(
      (v): v is number => typeof v === "number" && v.toString().startsWith("S")
    ),
    ...(srLevels.local_support || []).map((l) => l.price),
  ];
  const resistancePrices: number[] = [
    ...Object.values(srLevels.pivot_points || {}).filter(
      (v): v is number => typeof v === "number" && v.toString().startsWith("R")
    ),
    ...(srLevels.local_resistance || []).map((l) => l.price),
  ];

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-neon-green"></div>
        <p className="mt-4 text-muted-foreground">Loading market data...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground">
            Professional trading terminal with S&R levels and indicator overlays
          </p>
        </div>
        <div className="flex gap-2">
          <select
            value={selectedSymbol}
            onChange={(e) => setSelectedSymbol(e.target.value)}
            className="px-3 py-2 rounded bg-dark-800 border border-border text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option>NSE:SBIN-EQ</option>
            <option>NSE:RELIANCE-EQ</option>
            <option>NSE:TCS-EQ</option>
            <option>NSE:INFY-EQ</option>
            <option>NSE:HDFCBANK-EQ</option>
          </select>
        </div>
      </div>

      {/* Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="glass p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-muted-foreground uppercase">Total PnL</p>
              <p className="text-xl font-bold text-neon-green">+₹12,450.50</p>
            </div>
            <TrendingUp className="w-6 h-6 text-neon-green" />
          </div>
        </Card>
        <Card className="glass p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-muted-foreground uppercase">Win Rate</p>
              <p className="text-xl font-bold text-neon-blue">68.5%</p>
            </div>
            <Activity className="w-6 h-6 text-neon-blue" />
          </div>
        </Card>
        <Card className="glass p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-muted-foreground uppercase">Active Strategies</p>
              <p className="text-xl font-bold text-neon-purple">4</p>
            </div>
            <HardHat className="w-6 h-6 text-neon-purple" />
          </div>
        </Card>
        <Card className="glass p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-muted-foreground uppercase">AI Status</p>
              <p className="text-xl font-bold text-neon-pink">Grok Online</p>
            </div>
            <Bot className="w-6 h-6 text-neon-pink" />
          </div>
        </Card>
      </div>

      {/* Main Layout: Chart + Indicator Selector */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-[calc(100vh-320px)] min-h-[600px]">
        {/* Indicator Selector Sidebar */}
        <div className="lg:col-span-3 flex flex-col gap-4">
          <Card className="glass p-4 flex flex-col h-full">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Search className="w-4 h-4" />
                Indicator Selector
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <div className="p-3">
                <div className="relative mb-4">
                  <Search className="absolute left-3 top-3 w-4 h-4 text-muted-foreground" />
                  <input
                    type="text"
                    placeholder="Search indicators..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-9 pr-3 py-2 rounded bg-dark-800 border border-border text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>

                <div className="space-y-3 max-h-[500px] overflow-y-auto pr-2">
                  {Object.entries(INDICATOR_CATEGORIES).map(
                    ([category, indicatorNames]) => {
                      const catIndicators = filteredIndicators.filter(
                        (i) => i.category === category
                      );
                      if (catIndicators.length === 0) return null;
                      return (
                        <div key={category} className="mb-3">
                          <div className="flex items-center justify-between mb-2 cursor-pointer" onClick={() => {}}>
                            <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                              {category.replace("_", " ")}
                            </span>
                            <ChevronDown className="w-3 h-3 text-muted-foreground" />
                          </div>
                          <div className="space-y-1">
                            {catIndicators.map((ind) => (
                              <div
                                key={ind.name}
                                className="flex items-center justify-between p-2 rounded hover:bg-dark-800 transition-colors group cursor-pointer"
                                onClick={() => toggleIndicator(ind.name)}
                              >
                                <div className="flex items-center gap-2">
                                  <input
                                    type="checkbox"
                                    checked={selectedIndicators.includes(ind.name)}
                                    onChange={() => toggleIndicator(ind.name)}
                                    className="rounded text-neon-green focus:ring-neon-green"
                                  />
                                  <span className="text-xs text-foreground group-hover:text-neon-green transition-colors">
                                    {ind.name}
                                  </span>
                                </div>
                                <span className="text-[10px] text-muted-foreground">
                                  {ind.overlay ? "Overlay" : "Sub"}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      );
                    }
                  )}
                </div>

                <div className="mt-4 p-3 rounded bg-dark-800 border border-border/50">
                  <p className="text-xs text-muted-foreground mb-2">
                    <strong>{selectedIndicators.length}</strong> indicators active
                  </p>
                  <div className="flex gap-2">
                    {overlayIndicators.map((name) => (
                      <span key={name} className="px-2 py-1 rounded bg-neon-green/20 text-neon-green text-xs border border-neon-green/30">
                        {name}
                      </span>
                    ))}
                  </div>
                  {subChartIndicators.length > 0 && (
                    <div className="mt-2 flex gap-2">
                      {subChartIndicators.map((name) => (
                        <span key={name} className="px-2 py-1 rounded bg-neon-blue/20 text-neon-blue text-xs border border-neon-blue/30">
                          {name}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Chart Area */}
        <div className="lg:col-span-9 glass flex flex-col h-full">
          <div className="flex items-center justify-between p-4 border-b border-border bg-dark-800/50">
            <div>
              <h2 className="text-lg font-bold">{selectedSymbol}</h2>
              <p className="text-xs text-muted-foreground">
                5min · {candles.length} candles · S&R levels active
              </p>
            </div>
            <div className="flex gap-2">
              <button className="p-2 hover:bg-dark-700 rounded text-muted-foreground transition-colors" title="Zoom In">
                <Plus className="w-4 h-4" />
              </button>
              <button className="p-2 hover:bg-dark-700 rounded text-muted-foreground transition-colors" title="Full Screen">
                <Monitor className="w-4 h-4" />
              </button>
            </div>
          </div>

          <div className="flex-1 relative p-4 overflow-hidden">
            {/* S&R Horizontal Lines */}
            {supportPrices.map((price, i) => (
              <div
                key={`support-${i}`}
                className="absolute left-0 right-0 h-[1px] bg-neon-green/40 z-10"
                style={{
                  top: `calc(50% - ${((price - 2400) / 400) * 100}%)`,
                }}
              />
            ))}
            {resistancePrices.map((price, i) => (
              <div
                key={`resistance-${i}`}
                className="absolute left-0 right-0 h-[1px] bg-neon-red/40 z-10"
                style={{
                  top: `calc(50% - ${((price - 2400) / 400) * 100}%)`,
                }}
              />
            ))}

            {/* Main Candlestick Chart (Line approximation with recharts) */}
            <div className="h-[60%] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={candles}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#1a1a1a" />
                  <XAxis dataKey="time" axisLine={false} tickLine={false} textStyle={{ fill: "#666", fontSize: 10 }} />
                  <YAxis axisLine={false} tickLine={false} textStyle={{ fill: "#666", fontSize: 10 }} />
                  <Tooltip />
                  <Line
                    type="monotone"
                    dataKey="close"
                    stroke="#00ff88"
                    strokeWidth={2}
                    dot={false}
                    name="Close"
                  />
                  {/* Overlay Indicators */}
                  {overlayIndicators.map((indName) => {
                    const ind = indicators.find((i) => i.name === indName);
                    if (!ind) return null;
                    const col = Object.keys(candles[0] || {}).find(
                      (k) => k.toLowerCase().includes(indName.toUpperCase())
                    );
                    if (!col) return null;
                    return (
                      <Line
                        key={indName}
                        type="monotone"
                        dataKey={col}
                        stroke={ind.overlay ? "#bc13fe" : "#00d4ff"}
                        strokeWidth={1.5}
                        dot={false}
                        name={indName}
                        strokeDasharray="4 4"
                      />
                    );
                  })}
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Sub-charts for non-overlay indicators */}
            {subChartIndicators.length > 0 && (
              <div className="h-[35%] w-full mt-4 space-y-3">
                {subChartIndicators.map((indName) => (
                  <div key={indName} className="h-[calc(33%_-_10px)]">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={candles}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#1a1a1a" />
                        <XAxis dataKey="time" axisLine={false} tickLine={false} textStyle={{ fill: "#666", fontSize: 10 }} />
                        <YAxis axisLine={false} tickLine={false} textStyle={{ fill: "#666", fontSize: 10 }} />
                        <Tooltip />
                        <Line
                          type="monotone"
                          dataKey={Object.keys(candles[0] || {}).find((k) => k.toLowerCase().includes(indName.toUpperCase())) || "close"}
                          stroke="#00d4ff"
                          strokeWidth={1.5}
                          dot={false}
                          name={indName}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* S&R Levels Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="glass p-4">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingDown className="w-4 h-4 text-neon-green" />
              Support Levels
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {srLevels.local_support.map((level) => (
                <div key={level.timestamp} className="flex justify-between p-2 rounded bg-dark-800/50 text-sm">
                  <span className="text-neon-green font-medium">₹{level.price}</span>
                  <span className="text-muted-foreground">Strength: {level.strength}</span>
                </div>
              ))}
              {srLevels.local_support.length === 0 && (
                <p className="text-xs text-muted-foreground">No support levels detected</p>
              )}
            </div>
          </CardContent>
        </Card>
        <Card className="glass p-4">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-neon-red" />
              Resistance Levels
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {srLevels.local_resistance.map((level) => (
                <div key={level.timestamp} className="flex justify-between p-2 rounded bg-dark-800/50 text-sm">
                  <span className="text-destructive font-medium">₹{level.price}</span>
                  <span className="text-muted-foreground">Strength: {level.strength}</span>
                </div>
              ))}
              {srLevels.local_resistance.length === 0 && (
                <p className="text-xs text-muted-foreground">No resistance levels detected</p>
              )}
            </div>
          </CardContent>
        </Card>
        <Card className="glass p-4">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Cpu className="w-4 h-4 text-neon-purple" />
              Pivot Points
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {Object.entries(srLevels.pivot_points || {}).map(([key, val]) => {
                if (key === "method" || typeof val !== "number") return null;
                return (
                  <div key={key} className="flex justify-between p-2 rounded bg-dark-800/50 text-sm">
                    <span className="text-muted-foreground">{key}</span>
                    <span className="text-foreground font-medium">₹{val}</span>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

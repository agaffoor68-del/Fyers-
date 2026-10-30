"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Terminal,
  Activity,
  Buy,
  Sell,
  Wallet,
  RefreshCw,
  UpdateCircle,
} from "lucide-react";

interface Tick {
  symbol: string;
  price: number;
  change: number;
  time: string;
}

const mockSymbols = ["NSE:SBIN-EQ", "NSE:RELIANCE-EQ", "NSE:TCS-EQ", "NSE:INFY-EQ", "NSE:HDFCBANK-EQ"];

export default function TerminalPage() {
  const [ticks, setTicks] = useState<Tick[]>(mockSymbols.map((s, i) => ({
    symbol: s,
    price: 2500 + i * 500 + Math.random() * 100,
    change: (Math.random() - 0.5) * 4,
    time: new Date().toLocaleTimeString(),
  })));
  const [selectedSymbol, setSelectedSymbol] = useState("NSE:SBIN-EQ");
  const [qty, setQty] = useState(1);
  const [orderType, setOrderType] = useState("MARKET");
  const [price, setPrice] = useState("");

  useEffect(() => {
    const timer = setInterval(() => {
      setTicks(prev => prev.map(t => ({
        ...t,
        price: t.price * (1 + (Math.random() - 0.5) * 0.002),
        change: (Math.random() - 0.5) * 4,
        time: new Date().toLocaleTimeString(),
      })));
    }, 2000);
    return () => clearInterval(timer);
  }, []);

  const currentTick = ticks.find(t => t.symbol === selectedSymbol);

  const handleBuy = () => {
    console.log("BUY", selectedSymbol, qty, orderType, price);
  };

  const handleSell = () => {
    console.log("SELL", selectedSymbol, qty, orderType, price);
  };

  return (
    <div className="flex flex-col h-full gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Live Terminal</h1>
          <p className="text-muted-foreground">
            Order execution panel with live market data
          </p>
        </div>
        <button className="flex items-center gap-2 px-3 py-1.5 rounded bg-dark-900 border border-border hover:bg-dark-800 transition-colors text-sm">
          <RefreshCw className="w-4 h-4" />
          Reconnect
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-200px)] min-h-[500px]">
        {/* Live Ticks */}
        <Card className="glass flex flex-col h-full">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2">
              <Terminal className="w-5 h-5" />
              Live Market Data
            </CardTitle>
          </CardHeader>
          <CardContent className="flex-1 overflow-hidden flex flex-col">
            <div className="flex items-center gap-4 px-3 py-2 border-b border-border bg-dark-900/50">
              <div className="flex-2 text-xs font-bold text-muted-foreground">Symbol</div>
              <div className="flex-1 text-right text-xs font-bold text-muted-foreground">Price</div>
              <div className="text-right text-xs font-bold text-muted-foreground">Change</div>
              <div className="text-right text-xs font-bold text-muted-foreground">Time</div>
            </div>
            <div className="flex-1 overflow-y-auto">
              <div className="space-y-1">
                {ticks.map((tick) => (
                  <div
                    key={tick.symbol}
                    onClick={() => setSelectedSymbol(tick.symbol)}
                    className={`flex items-center justify-between px-3 py-2 cursor-pointer rounded transition-colors ${
                      selectedSymbol === tick.symbol ? "bg-primary/10 border border-primary/50" : "hover:bg-dark-800/50"
                    }`}
                  >
                    <div className="flex-2 font-mono text-sm">{tick.symbol}</div>
                    <div className="flex-1 text-right font-mono text-sm font-bold">
                      ₹{tick.price.toFixed(2)}
                    </div>
                    <div className="text-right font-mono text-sm">
                      <span className={tick.change >= 0 ? "text-neon-green" : "text-destructive"}>
                        {tick.change >= 0 ? "+" : ""}{tick.change.toFixed(2)}%
                      </span>
                    </div>
                    <div className="text-right text-[10px] text-muted-foreground">
                      {tick.time}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Buy/Sell Panel */}
        <Card className="glass flex flex-col h-full">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2">
              <Activity className="w-5 h-5" />
              Order Entry
            </CardTitle>
          </CardHeader>
          <CardContent className="flex-1 p-4">
            <div className="text-center mb-6">
              <div className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                {selectedSymbol.split(":")[1]}
              </div>
              <div className="text-3xl font-bold mt-1">
                ₹{currentTick?.price.toFixed(2) || "--"}
              </div>
              <div className={currentTick?.change >= 0 ? "text-neon-green" : "text-destructive"} className="text-sm mt-1">
                {currentTick?.change >= 0 ? "+" : ""}{currentTick?.change.toFixed(2)}%
              </div>
            </div>

            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <button
                  onClick={handleBuy}
                  className="py-3 bg-neon-green text-dark-900 rounded-xl font-bold hover:bg-neon-green/90 transition-all transform active:scale-95 flex items-center justify-center gap-2 shadow-[0_0_20px_rgba(0,255,136,0.3)]"
                >
                  <Buy className="w-5 h-5" />
                  BUY
                </button>
                <button
                  onClick={handleSell}
                  className="py-3 bg-destructive text-white rounded-xl font-bold hover:bg-destructive/90 transition-all transform active:scale-95 flex items-center justify-center gap-2 shadow-[0_0_20px_rgba(239,68,68,0.3)]"
                >
                  <Sell className="w-5 h-5" />
                  SELL
                </button>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs text-muted-foreground mb-1">Quantity</label>
                  <input
                    type="number"
                    value={qty}
                    onChange={(e) => setQty(Number(e.target.value))}
                    className="w-full px-3 py-2 rounded bg-dark-800 border border-border text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
                <div>
                  <label className="block text-xs text-muted-foreground mb-1">Type</label>
                  <select
                    value={orderType}
                    onChange={(e) => setOrderType(e.target.value)}
                    className="w-full px-3 py-2 rounded bg-dark-800 border border-border text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option>MARKET</option>
                    <option>LIMIT</option>
                    <option>SL</option>
                    <option>SL-M</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs text-muted-foreground mb-1">Price</label>
                  <input
                    type="number"
                    value={price}
                    onChange={(e) => setPrice(e.target.value)}
                    placeholder="0"
                    className="w-full px-3 py-2 rounded bg-dark-800 border border-border text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
              </div>

              <div className="pt-4 border-t border-border/50">
                <button
                  onClick={handleBuy}
                  className="w-full py-2 bg-dark-800 border border-border rounded-lg hover:bg-dark-700 transition-colors text-sm text-muted-foreground"
                >
                  <Wallet className="w-4 h-4 mr-2" />
                  Available Margin: ₹1,05,420.50
                </button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Order History */}
        <Card className="glass flex flex-col h-full">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2">
              <UpdateCircle className="w-5 h-5" />
              Recent Orders
            </CardTitle>
          </CardHeader>
          <CardContent className="flex-1 overflow-y-auto p-3">
            <div className="space-y-2">
              {[
                { symbol: "NSE:SBIN-EQ", side: "BUY", qty: 10, price: "₹645.20", status: "FILLED", time: "10:30:15" },
                { symbol: "NSE:RELIANCE-EQ", side: "SELL", qty: 5, price: "₹2,450.00", status: "FILLED", time: "10:15:32" },
                { symbol: "NSE:TCS-EQ", side: "BUY", qty: 2, price: "₹3,580.40", status: "PENDING", time: "09:45:10" },
              ].map((order) => (
                <div key={`${order.time}-${order.symbol}`} className="flex items-center justify-between p-2 rounded bg-dark-800/50 border border-border/30">
                  <div className="flex items-center gap-2">
                    <div className={`w-6 h-6 rounded flex items-center justify-center text-xs font-bold ${order.side === "BUY" ? "bg-neon-green/20 text-neon-green" : "bg-destructive/20 text-destructive"}`}>
                      {order.side[0]}
                    </div>
                    <div className="flex flex-col">
                      <div className="text-xs font-medium">{order.symbol}</div>
                      <div className="text-[10px] text-muted-foreground">{order.time}</div>
                    </div>
                  </div>
                  <div className="text-right hidden md:block">
                    <div className="text-xs font-mono">{order.qty} @ {order.price}</div>
                    <div className={`text-[10px] font-bold ${order.status === "FILLED" ? "text-neon-green" : "text-muted-foreground"}`}>
                      {order.status}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

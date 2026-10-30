"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  TrendingUp,
  TrendingDown,
  Activity,
  Monitor,
  Bot,
  Brain,
} from "lucide-react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

const stats = [
  {
    title: "Total PnL",
    value: "+₹12,450.50",
    change: "+3.2%",
    positive: true,
    icon: TrendingUp,
    color: "text-neon-green",
  },
  {
    title: "Win Rate",
    value: "68.5%",
    change: "+2.1%",
    positive: true,
    icon: Activity,
    color: "text-neon-blue",
  },
  {
    title: "Active Strategies",
    value: "4",
    change: "2 live",
    positive: true,
    icon: Monitor,
    color: "text-neon-purple",
  },
  {
    title: "AI Models",
    value: "Grok-1",
    change: "Memory enabled",
    positive: true,
    icon: Bot,
    color: "text-neon-pink",
  },
];

const equityData = [
  { name: "Mon", value: 100000 },
  { name: "Tue", value: 102300 },
  { name: "Wed", value: 99800 },
  { name: "Thu", value: 104500 },
  { name: "Fri", value: 108200 },
  { name: "Mon", value: 112500 },
  { name: "Tue", value: 115800 },
];

export default function Dashboard() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground">
            Overview of your trading performance and AI insights
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="flex items-center gap-1 px-2 py-1 rounded bg-dark-900 border border-border text-xs">
            <span className="w-2 h-2 rounded-full bg-neon-green" />
            <span className="text-neon-green font-medium">System Live</span>
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <Card key={stat.title} className="glass hover:border-border/50 transition-colors">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {stat.title}
              </CardTitle>
              <stat.icon className={`w-5 h-5 ${stat.color}`} />
            </CardHeader>
            <CardContent>
              <div className="flex items-baseline gap-1">
                <span className="text-xl font-bold">{stat.value}</span>
              </div>
              <div className={stat.positive ? "text-neon-green" : "text-destructive"} className="text-xs mt-1 flex items-center gap-1">
                <span className={stat.positive ? "↑" : "↓"} />
                {stat.change}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2 glass">
          <CardHeader>
            <CardTitle className="text-lg font-semibold">Equity Curve</CardTitle>
            <p className="text-xs text-muted-foreground">
              Portfolio value over time
            </p>
          </CardHeader>
          <CardContent className="h-80">
            <div className="chart-grid h-full w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={equityData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#1a1a1a" />
                  <XAxis dataKey="name" axisLine={false} tickLine={false} textStyle={{ fill: "#666", fontSize: 12 }} />
                  <YAxis axisLine={false} tickLine={false} textStyle={{ fill: "#666", fontSize: 12 }} />
                  <Tooltip />
                  <Line type="monotone" dataKey="value" stroke="#00ff88" strokeWidth={2} dot={false} activeDot={{ r: 4 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card className="glass">
          <CardHeader>
            <CardTitle className="text-lg font-semibold">Recent Signals</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {[
                { symbol: "NSE:RELIANCE-EQ", signal: "BUY", price: "₹2,450.20", time: "10:30 AM", type: "ai" },
                { symbol: "NSE:TCS-EQ", signal: "SELL", price: "₹3,580.40", time: "10:15 AM", type: "manual" },
                { symbol: "NSE:INFY-EQ", signal: "BUY", price: "₹1,420.10", time: "09:45 AM", type: "ai" },
                { symbol: "NSE:HDFCBANK-EQ", signal: "HOLD", price: "₹1,560.80", time: "09:30 AM", type: "watch" },
              ].map((item) => (
                <div key={item.symbol} className="flex items-center justify-between p-3 rounded bg-dark-800 border border-border/50">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded bg-dark-900 flex items-center justify-center text-xs font-bold text-neon-blue">
                      {item.symbol.split(":")[1].charAt(0)}
                    </div>
                    <div>
                      <div className="text-sm font-medium">{item.symbol.split(":")[1]}</div>
                      <div className="text-xs text-muted-foreground">{item.time}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-1 rounded text-xs font-bold ${
                      item.signal === "BUY" ? "bg-neon-green/20 text-neon-green" :
                      item.signal === "SELL" ? "bg-destructive/20 text-destructive" :
                      "bg-muted/20 text-muted-foreground"
                    }`}>
                      {item.signal}
                    </span>
                    <span className="text-sm font-medium">{item.price}</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
        <Card className="glass p-6">
          <div className="flex items-center gap-3 mb-4">
            <Brain className="w-6 h-6 text-neon-purple" />
            <h3 className="font-semibold text-lg">Grok AI Status</h3>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Memory Enabled</span>
              <span className="text-neon-green font-medium">✓ Active</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Last Learning</span>
              <span className="text-muted-foreground">2h ago</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Failures Logged</span>
              <span className="text-muted-foreground">3</span>
            </div>
          </div>
        </Card>

        <Card className="glass p-6">
          <div className="flex items-center gap-3 mb-4">
            <Bot className="w-6 h-6 text-neon-blue" />
            <h3 className="font-semibold text-lg">AI Optimizer</h3>
          </div>
          <button className="w-full py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors font-medium">
            Run Auto-Optimize
          </button>
        </Card>

        <Card className="glass p-6">
          <div className="flex items-center gap-3 mb-4">
            <Terminal className="w-6 h-6 text-neon-pink" />
            <h3 className="font-semibold text-lg">Live Connection</h3>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Fyers API</span>
              <span className="text-neon-green font-medium">● Connected</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">WebSocket</span>
              <span className="text-neon-green font-medium">● Live</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Paper Trading</span>
              <span className="text-neon-green font-medium">● Enabled</span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}

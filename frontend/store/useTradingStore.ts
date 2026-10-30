import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface Trade {
  id: string;
  symbol: string;
  side: "BUY" | "SELL";
  quantity: number;
  price: number;
  pnl: number;
  status: "OPEN" | "CLOSED" | "PENDING";
  timestamp: string;
}

export interface Strategy {
  id: string;
  name: string;
  type: string;
  winRate: number;
  totalTrades: number;
  status: "Paper" | "Live" | "Draft";
  pnl: number;
  description: string;
}

export interface Tick {
  symbol: string;
  price: number;
  change: number;
  time: string;
}

export interface AIMessage {
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: string;
}

interface TradingStore {
  // UI
  sidebarOpen: boolean;
  theme: "light" | "dark";
  setSidebarOpen: (open: boolean) => void;
  toggleTheme: () => void;

  // Market
  ticks: Tick[];
  selectedSymbol: string;
  setTicks: (ticks: Tick[]) => void;
  setSelectedSymbol: (symbol: string) => void;

  // Orders
  trades: Trade[];
  addTrade: (trade: Trade) => void;

  // Strategies
  strategies: Strategy[];
  addStrategy: (strategy: Strategy) => void;

  // AI
  messages: AIMessage[];
  addMessage: (message: AIMessage) => void;
}

export const useTradingStore = create<TradingStore>()(
  persist(
    (set) => ({
      sidebarOpen: true,
      theme: "dark",
      setSidebarOpen: (open) => set({ sidebarOpen: open }),
      toggleTheme: () =>
        set((state) => ({ theme: state.theme === "dark" ? "light" : "dark" })),

      ticks: [],
      selectedSymbol: "NSE:SBIN-EQ",
      setTicks: (ticks) => set({ ticks }),
      setSelectedSymbol: (symbol) => set({ selectedSymbol: symbol }),

      trades: [],
      addTrade: (trade) =>
        set((state) => ({ trades: [...state.trades, trade] })),

      strategies: [],
      addStrategy: (strategy) =>
        set((state) => ({ strategies: [...state.strategies, strategy] })),

      messages: [],
      addMessage: (message) =>
        set((state) => ({ messages: [...state.messages, message] })),
    }),
    {
      name: "trading-storage",
    }
  )
);

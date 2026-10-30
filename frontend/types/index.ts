export interface TradeLog {
  id: number;
  symbol: string;
  side: string;
  quantity: number;
  entry_price: number;
  exit_price?: number;
  pnl?: number;
  strategy_name?: string;
  status: string;
  timestamp: string;
}

export interface Strategy {
  id: number;
  name: string;
  description?: string;
  rules?: Record<string, unknown>;
  indicators?: string[];
  win_rate?: number;
  total_trades?: number;
  is_active?: boolean;
  is_paper?: boolean;
  created_at: string;
}

export interface PaperTrade {
  id: number;
  symbol: string;
  side: string;
  quantity: number;
  entry_price: number;
  stop_loss?: number;
  take_profit?: number;
  status: string;
  pnl?: number;
  strategy_id?: number;
  timestamp: string;
}

export interface AILearningLog {
  id: number;
  mistake_context: string;
  strategy_used: string;
  reason_failed: string;
  market_conditions?: Record<string, unknown>;
  lesson_learned?: string;
  timestamp: string;
}

export interface AIChatRequest {
  message: string;
  session_id?: string;
}

export interface AIChatResponse {
  response: string;
  session_id: string;
}

export interface DashboardStats {
  total_trades: number;
  total_paper_trades: number;
  active_strategies: number;
  total_ai_failures: number;
  win_rate: number;
}

export interface Tick {
  symbol: string;
  price: number;
  change: number;
  time: string;
}

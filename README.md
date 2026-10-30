# Grok AI Algorithmic Trading Platform

An institutional-grade algorithmic trading platform with integrated Grok AI (xAI), featuring a Next.js frontend, FastAPI backend, SQLAlchemy database, and Fyers API integration.

## Features

### 🧠 Grok AI Integration
- **xAI API Integration**: Connects to Grok via OpenAI SDK with `base_url="https://api.x.ai/v1"`
- **Strategy Generation**: AI-generated trading strategies with risk management
- **Auto-Optimizer**: Automatically optimizes strategies based on market conditions
- **Memory System**: Learns from past failures via `AILearningLog` table
- **Memory Injection**: Before generating new strategies, Grok reads past failures to avoid repeating mistakes

### 📊 Trading Features
- **Paper Trading**: Simulated order execution with stop-loss/take-profit
- **Live Trading**: Fyers API integration for live order placement
- **Portfolio Management**: Track PnL, win rate, and active positions
- **Real-time Data**: WebSocket live ticks and historical candle data
- **Trade Logging**: Complete audit trail of all trades

### 🖥️ Frontend (Next.js + Tailwind + shadcn/ui)
- **Dashboard**: Equity curve, PnL cards, win rate, active strategies
- **Grok AI**: Split-screen chat interface with auto-optimizer
- **Grok Brain**: View AI failures, lessons, and learning history
- **Strategy Lab**: Strategy management with deploy to paper/live
- **Live Terminal**: Buy/sell panel with live WebSocket ticker
- **Dark Theme**: Glassmorphism with neon accents

## Project Structure

```
Fyers-/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # API routes (grok, trading, fyers)
│   │   ├── core/            # Core configuration
│   │   ├── db/
│   │   │   ├── models/      # SQLAlchemy models
│   │   │   ├── session.py   # Database session
│   │   │   └── init_db.py   # DB initialization
│   │   ├── grok_ai/
│   │   │   └── agent.py     # Grok AI agent with memory
│   │   ├── services/
│   │   │   ├── fyers_service.py
│   │   │   └── paper_trade_service.py
│   │   ├── schemas/         # Pydantic schemas
│   │   └── main.py          # FastAPI app entrypoint
│   ├── alembic/             # DB migrations
│   ├── requirements.txt
│   ├── Dockerfile
│   └── venv/
├── frontend/
│   ├── app/
│   │   ├── brain/           # AI memory page
│   │   ├── dashboard/       # Dashboard page
│   │   ├── grok/            # Grok AI chat page
│   │   ├── strategies/      # Strategy management
│   │   └── terminal/        # Live trading terminal
│   ├── components/
│   │   ├── ui/              # shadcn/ui components
│   │   ├── layout/          # Sidebar, TopBar
│   │   └── chat/            # Grok chat component
│   ├── lib/                 # API client, utils
│   ├── store/               # Zustand state management
│   ├── types/               # TypeScript types
│   ├── package.json
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── Dockerfile
├── .env.example             # Environment variables template
├── docker-compose.yml       # Full stack deployment
├── setup.sh                 # Initial setup script
├── start.sh                 # Start both servers
└── README.md
```

## Quick Start

### Option 1: Using Setup Script

```bash
# Clone the repository
cd Fyers-

# Make scripts executable
chmod +x setup.sh start.sh

# Run setup (installs dependencies, initializes DB)
./setup.sh

# Edit .env with your API keys
nano .env

# Start the platform
./start.sh
```

### Option 2: Manual Setup

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env
# Edit .env with your keys
python -c "from app.db.init_db import init_db; init_db()"
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Docker Deployment

```bash
docker-compose up -d
```

## Environment Variables

Create a `.env` file in the root directory:

```env
XAI_API_KEY=your_xai_api_key
FYERS_CLIENT_ID=your_fyers_client_id
FYERS_ACCESS_TOKEN=your_fyers_access_token
FYERS_CLIENT_SECRET=your_fyers_client_secret
DATABASE_URL=sqlite:///./grok_trading.db
SECRET_KEY=your_secret_key
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

## API Endpoints

### Grok AI
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/grok/chat` | Chat with Grok AI |
| POST | `/api/grok/auto-optimize` | Auto-optimize strategies |
| GET | `/api/grok/memory` | Get AI learning memory |

### Trading
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/trading/dashboard/stats` | Dashboard statistics |
| GET/POST | `/api/trading/tradelogs` | Trade logs |
| GET/POST | `/api/trading/strategies` | Strategies |
| GET/POST | `/api/trading/paper-trades` | Paper trades |
| POST | `/api/trading/paper-trades/{id}/check-sl-tp` | Check SL/TP |
| GET | `/api/trading/ai-learning-log` | AI learning log |

### Fyers
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/fyers/profile` | User profile |
| GET | `/api/fyers/quotes` | Live quotes |
| GET/POST | `/api/fyers/candles` | Historical candles |
| POST | `/api/fyers/orders` | Place order |
| GET | `/api/fyers/orders` | Order book |
| GET | `/api/fyers/positions` | Positions |
| GET | `/api/fyers/funds` | Funds/Margin |

### WebSocket
| Endpoint | Description |
|----------|-------------|
| `ws://localhost:8000/ws/live-ticks` | Live market data ticks |

## Database Models

### TradeLog
Records all executed trades with symbol, side, quantity, prices, PnL, and strategy.

### Strategy
Stores strategy definitions, rules, indicators, win rate, and active status.

### PaperTrade
Simulated trades with stop-loss/take-profit tracking and auto-close logic.

### AIConversation
Chat history between user and Grok AI.

### AILearningLog
**Critical for AI memory**: Records failed trades with context, reason, and lessons learned.

## Grok AI Memory System

The platform includes a learning feedback loop:

1. **Trade Fails**: A paper trade hits stop-loss or generates negative PnL
2. **Log to Memory**: The failure is recorded in `AILearningLog` with:
   - Strategy used
   - Mistake context (what happened)
   - Reason failed (e.g., "High Slippage", "False Breakout")
   - Market conditions at the time
   - Lesson learned
3. **Inject into Prompt**: Before generating new strategies, Grok reads the last 5 failures
4. **Improve**: New strategies are generated with explicit instructions to avoid past mistakes

## Screenshots

- **Dashboard**: Portfolio overview with equity curve
- **Grok AI**: Chat interface with strategy generation
- **Grok Brain**: Transparent view of AI learning
- **Strategy Lab**: Deploy strategies to paper/live
- **Live Terminal**: Real-time order execution

## License

MIT License

## Disclaimer

Trading in financial markets involves substantial risk of loss. This software is for educational and research purposes only. Use at your own risk. The authors are not responsible for any financial losses incurred.

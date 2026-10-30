from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import grok, trading, fyers, indicators

app = FastAPI(
    title="Grok AI Trading Platform",
    description="Institutional-grade Algo Trading Platform with Grok AI",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    from app.db.init_db import init_db
    init_db()

# API Routes
app.include_router(grok.router, prefix="/api/grok", tags=["grok-ai"])
app.include_router(trading.router, prefix="/api/trading", tags=["trading"])
app.include_router(fyers.router, prefix="/api/fyers", tags=["fyers"])
app.include_router(indicators.router, prefix="/api/indicators", tags=["indicators"])

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass


manager = ConnectionManager()


@app.websocket("/ws/live-ticks")
async def live_ticks(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/")
def root():
    return {"message": "Grok AI Trading Platform API", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

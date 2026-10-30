class RiskManager:
    def __init__(self, max_daily_loss_percent=2.0):
        self.max_loss = max_daily_loss_percent

    def approve_order(self, signal, current_price, capital):
        if signal in ["BUY", "SELL"]:
            return True
        return False

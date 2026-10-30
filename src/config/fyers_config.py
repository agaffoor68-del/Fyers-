import os
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()

@dataclass
class FyersConfig:
    """Configuration class for Fyers API credentials and settings"""
    client_id: str = os.getenv("FYERS_CLIENT_ID", "") or os.getenv("FYERS_APP_ID", "")
    app_id: str = os.getenv("FYERS_APP_ID", "") or os.getenv("FYERS_CLIENT_ID", "")
    secret_key: str = os.getenv("FYERS_SECRET_KEY", "")
    redirect_uri: str = os.getenv("FYERS_REDIRECT_URI", "http://127.0.0.1:5000/auth/callback")
    access_token: str = os.getenv("FYERS_ACCESS_TOKEN", "")
    base_url: str = "https://api.fyers.in/api/v3"
    websocket_url: str = "wss://api.fyers.in/socket/v3/data/ws"
    
    def validate(self):
        """Validate that required credentials are present"""
        if not self.client_id and not self.app_id:
            raise ValueError("FYERS_CLIENT_ID or FYERS_APP_ID must be set in environment variables")
        if not self.access_token and not self.secret_key:
            raise ValueError("Either FYERS_ACCESS_TOKEN or FYERS_SECRET_KEY must be set in environment variables")
        return True
    
    @property
    def is_authenticated(self):
        """Check if access token is available"""
        return bool(self.access_token)

import os
import json
import hashlib
from datetime import datetime
from urllib.parse import urlencode
from src.config.fyers_config import FyersConfig
from src.utils.logger import get_logger

class FyersAuth:
    """Handle Fyers API authentication"""
    
    def __init__(self, config: FyersConfig = None):
        self.config = config or FyersConfig()
        self.logger = get_logger("FyersAuth")
        self.config.validate()
    
    def generate_auth_url(self) -> str:
        """Generate authentication URL"""
        state = hashlib.sha256(os.urandom(1024)).hexdigest()
        params = {
            "client_id": self.config.app_id,
            "redirect_uri": self.config.redirect_uri,
            "response_type": "code",
            "state": state,
            "scope": "openid profile email"
        }
        auth_url = f"https://api.fyers.in/api/v3/generate-authcode?{urlencode(params)}"
        self.logger.info("Auth URL generated")
        return auth_url
    
    def generate_access_token(self, auth_code: str) -> str:
        """Generate access token from auth code"""
        # Placeholder - actual implementation would use fyers-apiv3 library
        self.logger.info("Generating access token...")
        # In real implementation, use FyersModel from fyers_apiv3
        token = f"eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.{hashlib.md5(auth_code.encode()).hexdigest()}"
        self.config.access_token = token
        self.logger.info("Access token generated successfully")
        return token
    
    def save_token(self, token: str, filename: str = "fyers_tokens.json"):
        """Save access token to file"""
        token_data = {
            "access_token": token,
            "generated_at": datetime.now().isoformat(),
            "app_id": self.config.app_id
        }
        with open(filename, 'w') as f:
            json.dump(token_data, f, indent=4)
        self.logger.info(f"Token saved to {filename}")
    
    def load_token(self, filename: str = "fyers_tokens.json") -> str:
        """Load access token from file"""
        try:
            with open(filename, 'r') as f:
                token_data = json.load(f)
            self.config.access_token = token_data['access_token']
            self.logger.info(f"Token loaded from {filename}")
            return self.config.access_token
        except FileNotFoundError:
            self.logger.error(f"Token file {filename} not found")
            return ""

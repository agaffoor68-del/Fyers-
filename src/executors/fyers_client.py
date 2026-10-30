import os
from fyers_apiv3 import fyersModel
from dotenv import load_dotenv
from src.config.fyers_config import FyersConfig

load_dotenv()


def get_fyers_client(config: FyersConfig = None):
    if config is None:
        config = FyersConfig()
    
    client_id = config.client_id or config.app_id
    access_token = config.access_token
    
    if not client_id or not access_token:
        raise ValueError("Fyers Credentials missing in .env file!")
        
    fyers = fyersModel.FyersModel(
        client_id=client_id, 
        token=access_token, 
        is_async=False, 
        log_path="" 
    )
    return fyers

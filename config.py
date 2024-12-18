from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # API Settings
    API_URL: str = "http://ds.opmentis.xyz:8000"
    TASK_POLL_INTERVAL: int = 100  # seconds
    
    # Model Settings
    MODEL_PARAMS_DIR: str = "./alphafold/data/"
    USE_GPU: bool = False
    
    # GPU Settings
    TF_FORCE_UNIFIED_MEMORY: int = 1
    XLA_PYTHON_CLIENT_MEM_FRACTION: float = 4.0
    
    # Validator Settings
    WALLET_ADDRESS: Optional[str] = None
    
    def setup_gpu_env(self):
        """Setup GPU environment variables if GPU is enabled"""
        if self.USE_GPU:
            os.environ['TF_FORCE_UNIFIED_MEMORY'] = str(self.TF_FORCE_UNIFIED_MEMORY)
            os.environ['XLA_PYTHON_CLIENT_MEM_FRACTION'] = str(self.XLA_PYTHON_CLIENT_MEM_FRACTION)
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 
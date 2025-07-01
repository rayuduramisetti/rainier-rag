import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class Config:
    """Configuration class for Mount Rainier RAG System"""
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    NPS_API_KEY: Optional[str] = os.getenv("NPS_API_KEY")
    WEATHER_API_KEY: Optional[str] = os.getenv("WEATHER_API_KEY")
    STRAVA_CLIENT_ID: Optional[str] = os.getenv("STRAVA_CLIENT_ID")
    STRAVA_CLIENT_SECRET: Optional[str] = os.getenv("STRAVA_CLIENT_SECRET")
    
    # Database Configuration
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "./data/mount_rainier.db")
    VECTOR_DB_PATH: str = os.getenv("VECTOR_DB_PATH", "./data/chroma_db")
    
    # RAG Configuration
    EMBEDDINGS_MODEL: str = os.getenv("EMBEDDINGS_MODEL", "all-MiniLM-L6-v2")
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    TOP_K_RESULTS: int = int(os.getenv("TOP_K_RESULTS", "5"))
    
    # UI Configuration
    GRADIO_THEME: str = "soft"
    GRADIO_TITLE: str = "🏔️ Mount Rainier AI Guide"
    
    # Animation Configuration
    HIKER_SPEED: float = 2.0  # pixels per second
    DAY_NIGHT_CYCLE_DURATION: int = 60  # seconds for full cycle
    
    # Mount Rainier Specific
    MOUNT_RAINIER_ELEVATION: int = 14411  # feet
    PARK_COORDINATES: tuple = (46.8523, -121.7603)  # lat, lng
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required configurations are set"""
        required_keys = ["OPENAI_API_KEY"]
        missing_keys = [key for key in required_keys if not getattr(cls, key)]
        
        if missing_keys:
            print(f"Warning: Missing required configuration keys: {missing_keys}")
            return False
        return True

# Environment template (copy to .env file)
ENV_TEMPLATE = """
# Copy this to .env file and fill in your API keys
OPENAI_API_KEY=your_openai_api_key_here
NPS_API_KEY=your_nps_api_key_here
WEATHER_API_KEY=your_weather_api_key_here
STRAVA_CLIENT_ID=your_strava_client_id
STRAVA_CLIENT_SECRET=your_strava_client_secret
ENVIRONMENT=development
LOG_LEVEL=INFO
DATABASE_PATH=./data/mount_rainier.db
EMBEDDINGS_MODEL=all-MiniLM-L6-v2
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=5
""" 
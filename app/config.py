"""
Configurações da aplicação
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configurações base"""
    APP_NAME = "Equipe Operacional - Sistema Multiagente"
    VERSION = "0.1.0"
    DEBUG = os.getenv("DEBUG", "True") == "True"
    
    # API
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", 8000))
    
    # Caminhos
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
    REPORTS_DIR = os.getenv("REPORTS_DIR", "reports")
    
    # Banco de dados
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./equipe.db")
    
    # IA
    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")
    
    # Qdrant
    QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
    QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "equipe-operacional")
    
    # OpenAI (opcional)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
    
    # CORS
    CORS_ORIGINS = ["http://localhost:3000", "http://localhost:8000"]


config = Config()

"""
Integração com Modelos de IA (Ollama e OpenAI)
"""
from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod
import aiohttp
import json


class AIModelProvider(ABC):
    """
    Interface abstrata para provedores de modelos de IA
    """
    
    @abstractmethod
    async def generate_completion(self, prompt: str, temperature: float = 0.7,
                                 max_tokens: int = 1000) -> str:
        """Gera completion baseado em prompt"""
        pass
    
    @abstractmethod
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Gera embeddings para textos"""
        pass


class OllamaProvider(AIModelProvider):
    """
    Provedor para modelos locais via Ollama
    """
    
    def __init__(self, host: str = "http://localhost:11434", 
                 model: str = "mistral"):
        """
        Inicializa provedor Ollama
        
        Args:
            host: URL do servidor Ollama
            model: Modelo a usar
        """
        self.host = host
        self.model = model
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """
        Obtém ou cria sessão HTTP
        """
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def generate_completion(self, prompt: str, temperature: float = 0.7,
                                 max_tokens: int = 1000) -> str:
        """
        Gera completion via Ollama
        
        Args:
            prompt: Prompt para gerar resposta
            temperature: Temperatura (criatividade)
            max_tokens: Máximo de tokens
            
        Returns:
            Resposta gerada
        """
        try:
            session = await self._get_session()
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "temperature": temperature,
                "num_predict": max_tokens,
                "stream": False
            }
            
            async with session.post(
                f"{self.host}/api/generate",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=300)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("response", "")
                else:
                    return f"Error: {response.status}"
                    
        except Exception as e:
            return f"Error generating completion: {str(e)}"
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Gera embeddings via Ollama
        
        Args:
            texts: Textos para gerar embeddings
            
        Returns:
            Lista de embeddings
        """
        embeddings = []
        
        try:
            session = await self._get_session()
            
            for text in texts:
                payload = {
                    "model": self.model,
                    "prompt": text
                }
                
                async with session.post(
                    f"{self.host}/api/embeddings",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        embedding = result.get("embedding", [])
                        embeddings.append(embedding)
                    else:
                        embeddings.append([0.0] * 384)  # Default
                        
        except Exception as e:
            print(f"Error generating embeddings: {str(e)}")
            embeddings = [[0.0] * 384 for _ in texts]  # Fallback
        
        return embeddings
    
    async def close(self):
        """
        Fecha a sessão HTTP
        """
        if self.session:
            await self.session.close()


class OpenAIProvider(AIModelProvider):
    """
    Provedor para modelos OpenAI
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        """
        Inicializa provedor OpenAI
        
        Args:
            api_key: Chave da API
            model: Modelo a usar
        """
        self.api_key = api_key
        self.model = model
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """
        Obtém ou cria sessão HTTP
        """
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def generate_completion(self, prompt: str, temperature: float = 0.7,
                                 max_tokens: int = 1000) -> str:
        """
        Gera completion via OpenAI
        
        Args:
            prompt: Prompt para gerar resposta
            temperature: Temperatura
            max_tokens: Máximo de tokens
            
        Returns:
            Resposta gerada
        """
        try:
            session = await self._get_session()
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    return f"Error: {response.status}"
                    
        except Exception as e:
            return f"Error generating completion: {str(e)}"
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Gera embeddings via OpenAI
        
        Args:
            texts: Textos para gerar embeddings
            
        Returns:
            Lista de embeddings
        """
        try:
            session = await self._get_session()
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "text-embedding-3-small",
                "input": texts
            }
            
            async with session.post(
                "https://api.openai.com/v1/embeddings",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return [emb["embedding"] for emb in result["data"]]
                else:
                    return [[0.0] * 1536 for _ in texts]
                    
        except Exception as e:
            print(f"Error generating embeddings: {str(e)}")
            return [[0.0] * 1536 for _ in texts]
    
    async def close(self):
        """
        Fecha a sessão HTTP
        """
        if self.session:
            await self.session.close()


class AIModelFactory:
    """
    Factory para criar instâncias de provedores de IA
    """
    
    @staticmethod
    def create_provider(provider_type: str, **kwargs) -> AIModelProvider:
        """
        Cria um provedor de IA
        
        Args:
            provider_type: Tipo de provedor ('ollama' ou 'openai')
            **kwargs: Argumentos adicionais
            
        Returns:
            Instância do provedor
        """
        if provider_type.lower() == "ollama":
            return OllamaProvider(
                host=kwargs.get("host", "http://localhost:11434"),
                model=kwargs.get("model", "mistral")
            )
        elif provider_type.lower() == "openai":
            return OpenAIProvider(
                api_key=kwargs.get("api_key", ""),
                model=kwargs.get("model", "gpt-4")
            )
        else:
            raise ValueError(f"Unknown provider type: {provider_type}")

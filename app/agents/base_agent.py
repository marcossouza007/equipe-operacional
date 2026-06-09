"""
Base Agent Class - Define a estrutura padrão para todos os agentes especializados
"""
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
from datetime import datetime


class AgentSpecialty(Enum):
    """Especialidades de agentes"""
    BACKEND = "backend"
    FRONTEND = "frontend"
    FULLSTACK = "fullstack"
    SENIOR_ENGINEER = "senior_engineer"
    DEVOPS = "devops"
    ALGORITHMS = "algorithms"
    RESEARCH = "research"
    BUSINESS = "business_analyst"
    PROCESSES = "processes"
    NETWORKS_ENTERPRISE = "networks_enterprise"
    NETWORKS_TELECOM = "networks_telecom"
    GRC = "grc"
    CYBERSECURITY = "cybersecurity"
    LEGAL = "legal"
    ML = "ml"
    ANALYTICS = "analytics"
    DATA_ENGINEER = "data_engineer"
    ORCHESTRATOR = "orchestrator"


class AgentArea(Enum):
    """Áreas de negócio"""
    SOFTWARE_DEVELOPMENT = "software_development"
    COMPUTER_SCIENCE = "computer_science"
    BUSINESS = "business"
    NETWORKS = "networks"
    SECURITY = "security"
    LEGAL = "legal"
    DATA = "data"
    ORCHESTRATION = "orchestration"


@dataclass
class AgentResponse:
    """Resposta padrão de um agente"""
    agent_name: str
    specialty: AgentSpecialty
    analysis: str
    recommendations: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    confidence: float = 0.8
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentProfile:
    """Perfil de um agente especializado"""
    name: str
    specialty: AgentSpecialty
    area: AgentArea
    description: str
    expertise_level: int  # 1-10
    keywords: List[str] = field(default_factory=list)


class BaseAgent(ABC):
    """Classe base para todos os agentes especializados"""
    
    def __init__(self, profile: AgentProfile):
        self.profile = profile
        self.conversation_history: List[Dict[str, str]] = []
    
    @abstractmethod
    async def analyze(self, request: str, context: Dict[str, Any]) -> AgentResponse:
        """
        Analisa uma solicitação e retorna resposta estruturada
        
        Args:
            request: Solicitação do usuário
            context: Contexto adicional
            
        Returns:
            AgentResponse: Resposta estruturada do agente
        """
        pass
    
    async def add_to_history(self, role: str, content: str):
        """Adiciona mensagem ao histórico de conversa"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_specialty_relevance(self, keywords: List[str]) -> float:
        """Calcula relevância da especialidade para um conjunto de palavras-chave"""
        matches = sum(1 for kw in keywords if kw.lower() in 
                     [k.lower() for k in self.profile.keywords])
        return min(matches / max(len(keywords), 1), 1.0)

"""
Módulo de Agentes - Agentes especializados
"""
from .base_agent import BaseAgent, AgentProfile, AgentResponse, AgentSpecialty, AgentArea
from .specialized_agents import (
    BackendDeveloper,
    FrontendDeveloper,
    NetworkEngineerEnterprise,
    CybersecuritySpecialist,
    LegalAgent,
    DataScientistML,
    BusinessAnalyst
)

__all__ = [
    "BaseAgent",
    "AgentProfile",
    "AgentResponse",
    "AgentSpecialty",
    "AgentArea",
    "BackendDeveloper",
    "FrontendDeveloper",
    "NetworkEngineerEnterprise",
    "CybersecuritySpecialist",
    "LegalAgent",
    "DataScientistML",
    "BusinessAnalyst"
]

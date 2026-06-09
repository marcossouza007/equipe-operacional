"""
Modelos de dados para requisições e respostas
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class AnalysisRequest(BaseModel):
    """Requisição de análise"""
    request: str = Field(..., description="Descrição da análise solicitada")
    context: Optional[Dict[str, Any]] = Field(default={}, description="Contexto adicional")
    priority: str = Field(default="normal", description="Prioridade: low, normal, high")


class AgentAnalysisResponse(BaseModel):
    """Resposta de um agente individual"""
    agent_name: str
    specialty: str
    analysis: str
    recommendations: List[str] = []
    risks: List[str] = []
    confidence: float
    metadata: Dict[str, Any] = {}


class OrchestratorResponse(BaseModel):
    """Resposta consolidada do orquestrador"""
    status: str
    agents_consulted: int
    analyses: List[Dict[str, str]]
    all_recommendations: List[str]
    all_risks: List[str]
    average_confidence: float
    final_verdict: str


class FileUploadResponse(BaseModel):
    """Resposta de upload de arquivo"""
    success: bool
    filename: str
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    category: Optional[str] = None
    confidence: Optional[float] = None
    content_preview: Optional[str] = None
    content_length: Optional[int] = None
    error: Optional[str] = None


class FileAnalysisRequest(BaseModel):
    """Requisição de análise de arquivo"""
    filename: str
    analysis_type: str = Field(default="full", description="Tipo: quick, full, detailed")


class ReportGenerationRequest(BaseModel):
    """Requisição de geração de relatório"""
    title: str
    report_type: str = Field(..., description="Tipo: executive, technical, action_plan, risk_matrix")
    analysis_data: Dict[str, Any]
    include_recommendations: bool = True
    include_risks: bool = True
    include_timeline: bool = False


class HealthCheckResponse(BaseModel):
    """Resposta de verificação de saúde"""
    status: str
    version: str
    timestamp: datetime
    agents_available: int
    modules: List[str]

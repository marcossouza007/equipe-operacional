"""
Orquestrador Principal - Coordena todos os agentes especializados
"""
from typing import List, Dict, Any
from .agents.base_agent import AgentSpecialty, AgentArea, AgentResponse
from .agents.specialized_agents import (
    BackendDeveloper, FrontendDeveloper, NetworkEngineerEnterprise,
    CybersecuritySpecialist, LegalAgent, DataScientistML, BusinessAnalyst
)
import json


class Orchestrator:
    """Agente Orquestrador Principal"""
    
    def __init__(self):
        self.agents = {
            AgentSpecialty.BACKEND: BackendDeveloper(),
            AgentSpecialty.FRONTEND: FrontendDeveloper(),
            AgentSpecialty.NETWORKS_ENTERPRISE: NetworkEngineerEnterprise(),
            AgentSpecialty.CYBERSECURITY: CybersecuritySpecialist(),
            AgentSpecialty.LEGAL: LegalAgent(),
            AgentSpecialty.ML: DataScientistML(),
            AgentSpecialty.BUSINESS: BusinessAnalyst(),
        }
        self.conversation_history: List[Dict[str, Any]] = []
    
    def classify_request(self, request: str) -> List[AgentSpecialty]:
        """
        Classifica a solicitação e determina quais agentes devem ser acionados
        
        Args:
            request: Solicitação do usuário
            
        Returns:
            Lista de especialidades relevantes
        """
        keywords = request.lower().split()
        relevant_agents = []
        
        # Mapeamento de palavras-chave para agentes
        keyword_mapping = {
            "fortigate": [AgentSpecialty.NETWORKS_ENTERPRISE, AgentSpecialty.CYBERSECURITY],
            "firewall": [AgentSpecialty.NETWORKS_ENTERPRISE, AgentSpecialty.CYBERSECURITY],
            "contrato": [AgentSpecialty.LEGAL],
            "lgpd": [AgentSpecialty.LEGAL],
            "planilha": [AgentSpecialty.ML, AgentSpecialty.BUSINESS],
            "api": [AgentSpecialty.BACKEND],
            "frontend": [AgentSpecialty.FRONTEND],
            "banco": [AgentSpecialty.BACKEND],
            "segurança": [AgentSpecialty.CYBERSECURITY],
            "rede": [AgentSpecialty.NETWORKS_ENTERPRISE],
        }
        
        for keyword, agents in keyword_mapping.items():
            if keyword in keywords:
                relevant_agents.extend(agents)
        
        # Remove duplicatas mantendo ordem
        return list(dict.fromkeys(relevant_agents)) or [AgentSpecialty.BUSINESS]
    
    async def process_request(self, request: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Processa uma solicitação orquestrando os agentes necessários
        
        Args:
            request: Solicitação do usuário
            context: Contexto adicional
            
        Returns:
            Resposta consolidada com análises de múltiplos agentes
        """
        context = context or {}
        
        # Classificar requisição
        relevant_specialties = self.classify_request(request)
        
        # Acionar agentes relevantes
        responses: List[AgentResponse] = []
        for specialty in relevant_specialties:
            if specialty in self.agents:
                agent = self.agents[specialty]
                response = await agent.analyze(request, context)
                responses.append(response)
        
        # Consolidar respostas
        consolidated = self._consolidate_responses(responses)
        
        # Adicionar ao histórico
        self.conversation_history.append({
            "request": request,
            "agents_consulted": [s.value for s in relevant_specialties],
            "consolidated_response": consolidated
        })
        
        return consolidated
    
    def _consolidate_responses(self, responses: List[AgentResponse]) -> Dict[str, Any]:
        """
        Consolida respostas de múltiplos agentes
        
        Args:
            responses: Lista de respostas dos agentes
            
        Returns:
            Resposta consolidada
        """
        all_recommendations = []
        all_risks = []
        analyses = []
        avg_confidence = 0
        
        for response in responses:
            analyses.append({
                "agent": response.agent_name,
                "analysis": response.analysis
            })
            all_recommendations.extend(response.recommendations)
            all_risks.extend(response.risks)
            avg_confidence += response.confidence
        
        if responses:
            avg_confidence /= len(responses)
        
        return {
            "status": "success",
            "agents_consulted": len(responses),
            "analyses": analyses,
            "all_recommendations": list(set(all_recommendations)),  # Remove duplicatas
            "all_risks": list(set(all_risks)),
            "average_confidence": round(avg_confidence, 2),
            "final_verdict": self._generate_verdict(responses)
        }
    
    def _generate_verdict(self, responses: List[AgentResponse]) -> str:
        """
        Gera um veredicto final baseado nas análises
        
        Args:
            responses: Lista de respostas
            
        Returns:
            Veredicto consolidado
        """
        if not responses:
            return "Nenhuma análise disponível"
        
        risks_count = sum(len(r.risks) for r in responses)
        recommendations_count = sum(len(r.recommendations) for r in responses)
        avg_confidence = sum(r.confidence for r in responses) / len(responses)
        
        if risks_count > 2:
            return "⚠️ ALERTA: Múltiplos riscos identificados. Recomenda-se ação imediata."
        elif avg_confidence < 0.7:
            return "❓ INCERTEZA: Análise inconclusiva. Recomenda-se investigação adicional."
        else:
            return "✅ APROVADO: Análise conclui com confiança adequada."
    
    def get_memory(self) -> List[Dict[str, Any]]:
        """Retorna o histórico de conversas (memória)"""
        return self.conversation_history

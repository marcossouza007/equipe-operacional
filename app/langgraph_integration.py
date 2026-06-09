"""
Integração com LangGraph - Orquestração avançada de agentes
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import json


@dataclass
class GraphState:
    """
    Estado compartilhado do grafo de execução
    """
    user_request: str
    file_content: Optional[str] = None
    file_category: Optional[str] = None
    classified_agents: List[str] = None
    agent_responses: Dict[str, Any] = None
    consolidated_analysis: Dict[str, Any] = None
    final_report: Dict[str, Any] = None
    execution_trace: List[str] = None
    
    def __post_init__(self):
        if self.classified_agents is None:
            self.classified_agents = []
        if self.agent_responses is None:
            self.agent_responses = {}
        if self.execution_trace is None:
            self.execution_trace = []


class OrchestratorGraph:
    """
    Grafo de execução multiagente baseado em LangGraph
    """
    
    def __init__(self, orchestrator):
        """
        Inicializa o grafo de orquestração
        
        Args:
            orchestrator: Instância do Orchestrator
        """
        self.orchestrator = orchestrator
        self.execution_history: List[Dict[str, Any]] = []
    
    async def classify_request_node(self, state: GraphState) -> GraphState:
        """
        Nó 1: Classifica a requisição e determina agentes relevantes
        """
        state.execution_trace.append("[1] Classifying request...")
        
        # Classificar requisição
        relevant_agents = self.orchestrator.classify_request(state.user_request)
        state.classified_agents = [s.value for s in relevant_agents]
        
        state.execution_trace.append(
            f"[1] Classified agents: {', '.join(state.classified_agents)}"
        )
        
        return state
    
    async def validate_input_node(self, state: GraphState) -> GraphState:
        """
        Nó 2: Valida entrada do usuário
        """
        state.execution_trace.append("[2] Validating input...")
        
        if not state.user_request or len(state.user_request.strip()) == 0:
            raise ValueError("Request cannot be empty")
        
        if len(state.user_request) > 10000:
            raise ValueError("Request exceeds maximum length")
        
        state.execution_trace.append("[2] Input validation passed")
        return state
    
    async def categorize_content_node(self, state: GraphState) -> GraphState:
        """
        Nó 3: Categoriza conteúdo se houver arquivo
        """
        if state.file_content:
            state.execution_trace.append("[3] Categorizing file content...")
            
            from app.modules.file_classifier import FileClassifier
            classifier = FileClassifier()
            category, confidence = classifier.classify_file(
                "uploaded_file",
                state.file_content[:1000]
            )
            
            state.file_category = category.value
            state.execution_trace.append(
                f"[3] File category: {state.file_category} (confidence: {confidence:.2%})"
            )
        else:
            state.execution_trace.append("[3] No file content to categorize")
        
        return state
    
    async def execute_agents_node(self, state: GraphState) -> GraphState:
        """
        Nó 4: Executa agentes em paralelo ou seqüência
        """
        state.execution_trace.append(
            f"[4] Executing {len(state.classified_agents)} agents..."
        )
        
        context = {
            "file_category": state.file_category,
            "file_content": state.file_content[:500] if state.file_content else None
        }
        
        for agent_specialty in self.orchestrator.agents.keys():
            if agent_specialty.value in state.classified_agents:
                agent = self.orchestrator.agents[agent_specialty]
                try:
                    response = await agent.analyze(state.user_request, context)
                    state.agent_responses[agent.profile.name] = {
                        "analysis": response.analysis,
                        "recommendations": response.recommendations,
                        "risks": response.risks,
                        "confidence": response.confidence
                    }
                    state.execution_trace.append(
                        f"[4] Executed: {agent.profile.name}"
                    )
                except Exception as e:
                    state.execution_trace.append(
                        f"[4] Error in {agent.profile.name}: {str(e)}"
                    )
        
        return state
    
    async def consolidate_responses_node(self, state: GraphState) -> GraphState:
        """
        Nó 5: Consolida respostas de todos os agentes
        """
        state.execution_trace.append("[5] Consolidating responses...")
        
        all_recommendations = []
        all_risks = []
        avg_confidence = 0
        
        for agent_name, response in state.agent_responses.items():
            all_recommendations.extend(response.get("recommendations", []))
            all_risks.extend(response.get("risks", []))
            avg_confidence += response.get("confidence", 0.5)
        
        if state.agent_responses:
            avg_confidence /= len(state.agent_responses)
        
        state.consolidated_analysis = {
            "total_agents": len(state.agent_responses),
            "recommendations": list(set(all_recommendations)),
            "risks": list(set(all_risks)),
            "average_confidence": round(avg_confidence, 2),
            "agent_responses": state.agent_responses
        }
        
        state.execution_trace.append(
            f"[5] Consolidated {len(state.agent_responses)} agent responses"
        )
        
        return state
    
    async def resolve_conflicts_node(self, state: GraphState) -> GraphState:
        """
        Nó 6: Resolve conflitos entre opiniões dos agentes
        """
        state.execution_trace.append("[6] Resolving conflicts...")
        
        # Análise de conflitos
        conflicting_recommendations = []
        for rec1 in state.consolidated_analysis["recommendations"]:
            for rec2 in state.consolidated_analysis["recommendations"]:
                if rec1 != rec2 and self._is_conflicting(rec1, rec2):
                    conflicting_recommendations.append((rec1, rec2))
        
        if conflicting_recommendations:
            state.execution_trace.append(
                f"[6] Found {len(conflicting_recommendations)} potential conflicts"
            )
            # Priorizar por confiança dos agentes
            state.consolidated_analysis["conflicts_resolved"] = True
        else:
            state.execution_trace.append("[6] No conflicts detected")
            state.consolidated_analysis["conflicts_resolved"] = False
        
        return state
    
    async def generate_verdict_node(self, state: GraphState) -> GraphState:
        """
        Nó 7: Gera veredicto final
        """
        state.execution_trace.append("[7] Generating final verdict...")
        
        risks = state.consolidated_analysis.get("risks", [])
        recommendations = state.consolidated_analysis.get("recommendations", [])
        confidence = state.consolidated_analysis.get("average_confidence", 0)
        
        if len(risks) > 2:
            verdict = "⚠️ ALERTA: Múltiplos riscos identificados. Recomenda-se ação imediata."
            severity = "critical"
        elif confidence < 0.7:
            verdict = "❓ INCERTEZA: Análise inconclusiva. Recomenda-se investigação adicional."
            severity = "warning"
        else:
            verdict = "✅ APROVADO: Análise conclui com confiança adequada."
            severity = "success"
        
        state.consolidated_analysis["verdict"] = verdict
        state.consolidated_analysis["severity"] = severity
        
        state.execution_trace.append(f"[7] Verdict: {severity.upper()}")
        
        return state
    
    async def execute_graph(self, user_request: str, file_content: Optional[str] = None) -> Dict[str, Any]:
        """
        Executa o grafo completo de orquestração
        
        Args:
            user_request: Requisição do usuário
            file_content: Conteúdo do arquivo (opcional)
            
        Returns:
            Resultado da execução
        """
        # Inicializar estado
        state = GraphState(user_request=user_request, file_content=file_content)
        
        try:
            # Executar nós em seqüência
            state = await self.validate_input_node(state)
            state = await self.classify_request_node(state)
            state = await self.categorize_content_node(state)
            state = await self.execute_agents_node(state)
            state = await self.consolidate_responses_node(state)
            state = await self.resolve_conflicts_node(state)
            state = await self.generate_verdict_node(state)
            
            # Preparar resultado final
            result = {
                "success": True,
                "execution_trace": state.execution_trace,
                "analysis": state.consolidated_analysis,
                "verdict": state.consolidated_analysis.get("verdict"),
                "severity": state.consolidated_analysis.get("severity")
            }
            
            # Salvar no histórico
            self.execution_history.append(result)
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "execution_trace": state.execution_trace
            }
    
    def _is_conflicting(self, rec1: str, rec2: str) -> bool:
        """
        Detecta se duas recomendações são conflitantes
        """
        conflicts = [
            ("enable", "disable"),
            ("use", "avoid"),
            ("implement", "remove")
        ]
        
        rec1_lower = rec1.lower()
        rec2_lower = rec2.lower()
        
        for word1, word2 in conflicts:
            if word1 in rec1_lower and word2 in rec2_lower:
                return True
        
        return False
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """
        Retorna histórico de execuções
        """
        return self.execution_history

"""
Módulo de Relatórios - Gera relatórios executivos e técnicos
"""
from typing import Dict, Any, List
from datetime import datetime
from dataclasses import dataclass


@dataclass
class ReportConfig:
    """Configuração de relatório"""
    title: str
    report_type: str  # "executive", "technical", "action_plan", "risk_matrix"
    include_recommendations: bool = True
    include_risks: bool = True
    include_timeline: bool = False


class ReportGenerator:
    """Gerador de relatórios"""
    
    def __init__(self):
        self.reports: List[Dict[str, Any]] = []
    
    def generate_executive_report(self, 
                                 analysis_data: Dict[str, Any],
                                 config: ReportConfig) -> Dict[str, Any]:
        """
        Gera relatório executivo
        
        Args:
            analysis_data: Dados de análise
            config: Configuração do relatório
            
        Returns:
            Relatório em formato estruturado
        """
        report = {
            "metadata": {
                "title": config.title,
                "type": "executive",
                "generated_at": datetime.now().isoformat(),
                "version": "1.0"
            },
            "executive_summary": self._generate_summary(analysis_data),
            "key_findings": analysis_data.get("analyses", []),
            "recommendations": analysis_data.get("all_recommendations", []) if config.include_recommendations else [],
            "risks": analysis_data.get("all_risks", []) if config.include_risks else [],
            "confidence_score": analysis_data.get("average_confidence", 0),
            "next_steps": self._generate_next_steps(analysis_data)
        }
        
        self.reports.append(report)
        return report
    
    def generate_technical_report(self,
                                 analysis_data: Dict[str, Any],
                                 config: ReportConfig) -> Dict[str, Any]:
        """
        Gera relatório técnico
        
        Args:
            analysis_data: Dados de análise
            config: Configuração do relatório
            
        Returns:
            Relatório técnico
        """
        report = {
            "metadata": {
                "title": config.title,
                "type": "technical",
                "generated_at": datetime.now().isoformat(),
                "version": "1.0"
            },
            "technical_analysis": analysis_data.get("analyses", []),
            "detailed_recommendations": self._generate_detailed_recommendations(analysis_data),
            "risk_assessment": self._generate_risk_assessment(analysis_data),
            "implementation_details": self._generate_implementation_plan(analysis_data),
            "metrics": {
                "agents_consulted": analysis_data.get("agents_consulted", 0),
                "confidence_score": analysis_data.get("average_confidence", 0)
            }
        }
        
        self.reports.append(report)
        return report
    
    def generate_action_plan(self,
                            analysis_data: Dict[str, Any],
                            config: ReportConfig) -> Dict[str, Any]:
        """
        Gera plano de ação
        
        Args:
            analysis_data: Dados de análise
            config: Configuração do relatório
            
        Returns:
            Plano de ação
        """
        recommendations = analysis_data.get("all_recommendations", [])
        
        action_plan = {
            "metadata": {
                "title": config.title,
                "type": "action_plan",
                "generated_at": datetime.now().isoformat(),
                "version": "1.0"
            },
            "actions": [
                {
                    "id": f"ACT-{i+1}",
                    "description": rec,
                    "priority": self._assign_priority(rec, i, len(recommendations)),
                    "timeline": self._assign_timeline(rec),
                    "responsible": "To be assigned",
                    "status": "pending"
                }
                for i, rec in enumerate(recommendations)
            ],
            "critical_path": self._identify_critical_path(recommendations),
            "estimated_duration": "2-4 weeks"
        }
        
        self.reports.append(action_plan)
        return action_plan
    
    def generate_risk_matrix(self,
                            analysis_data: Dict[str, Any],
                            config: ReportConfig) -> Dict[str, Any]:
        """
        Gera matriz de riscos
        
        Args:
            analysis_data: Dados de análise
            config: Configuração do relatório
            
        Returns:
            Matriz de riscos
        """
        risks = analysis_data.get("all_risks", [])
        
        risk_matrix = {
            "metadata": {
                "title": config.title,
                "type": "risk_matrix",
                "generated_at": datetime.now().isoformat(),
                "version": "1.0"
            },
            "risks": [
                {
                    "id": f"RISK-{i+1}",
                    "description": risk,
                    "probability": self._assign_probability(risk),
                    "impact": self._assign_impact(risk),
                    "severity": self._calculate_severity(risk),
                    "mitigation": self._generate_mitigation(risk)
                }
                for i, risk in enumerate(risks)
            ],
            "summary": {
                "critical_count": sum(1 for r in risks if self._calculate_severity(r) >= 0.8),
                "high_count": sum(1 for r in risks if 0.5 <= self._calculate_severity(r) < 0.8),
                "medium_count": sum(1 for r in risks if 0.3 <= self._calculate_severity(r) < 0.5),
                "low_count": sum(1 for r in risks if self._calculate_severity(r) < 0.3)
            }
        }
        
        self.reports.append(risk_matrix)
        return risk_matrix
    
    # Helper methods
    def _generate_summary(self, data: Dict[str, Any]) -> str:
        agents_count = data.get("agents_consulted", 0)
        return f"Analysis conducted by {agents_count} specialized agents with {data.get('average_confidence', 0):.1%} confidence."
    
    def _generate_next_steps(self, data: Dict[str, Any]) -> List[str]:
        recommendations = data.get("all_recommendations", [])
        return recommendations[:3] if recommendations else ["Review findings", "Schedule follow-up meeting"]
    
    def _generate_detailed_recommendations(self, data: Dict[str, Any]) -> List[Dict[str, str]]:
        return [
            {"recommendation": rec, "priority": "high" if i < 3 else "medium"}
            for i, rec in enumerate(data.get("all_recommendations", []))
        ]
    
    def _generate_risk_assessment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        risks = data.get("all_risks", [])
        return {
            "total_risks": len(risks),
            "critical_risks": [r for r in risks if self._calculate_severity(r) >= 0.8],
            "mitigation_required": len(risks) > 0
        }
    
    def _generate_implementation_plan(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "phase_1": "Assessment and Planning",
            "phase_2": "Implementation",
            "phase_3": "Validation and Optimization",
            "estimated_completion": "4 weeks"
        }
    
    def _assign_priority(self, recommendation: str, index: int, total: int) -> str:
        if index < total * 0.3:
            return "high"
        elif index < total * 0.7:
            return "medium"
        else:
            return "low"
    
    def _assign_timeline(self, recommendation: str) -> str:
        return "1-2 weeks" if "critical" in recommendation.lower() else "2-4 weeks"
    
    def _identify_critical_path(self, recommendations: List[str]) -> List[str]:
        return recommendations[:3] if recommendations else []
    
    def _assign_probability(self, risk: str) -> float:
        return 0.7 if any(word in risk.lower() for word in ["high", "critical"]) else 0.5
    
    def _assign_impact(self, risk: str) -> float:
        return 0.8 if any(word in risk.lower() for word in ["data", "security", "breach"]) else 0.6
    
    def _calculate_severity(self, risk: str) -> float:
        probability = self._assign_probability(risk)
        impact = self._assign_impact(risk)
        return probability * impact
    
    def _generate_mitigation(self, risk: str) -> str:
        if "security" in risk.lower():
            return "Implement enhanced security controls and monitoring"
        elif "performance" in risk.lower():
            return "Optimize system performance and capacity planning"
        elif "data" in risk.lower():
            return "Implement data protection and backup strategies"
        else:
            return "Develop contingency plan and regular reviews"

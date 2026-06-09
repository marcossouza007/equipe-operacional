"""
Testes unitários para o sistema multiagente
"""
import pytest
from app.agents.base_agent import AgentProfile, AgentSpecialty, AgentArea, AgentResponse
from app.agents.specialized_agents import BackendDeveloper, NetworkEngineerEnterprise
from app.modules.file_classifier import FileClassifier, FileCategory
from app.modules.report_generator import ReportGenerator, ReportConfig
from app.modules.memory import Memory, MemoryEntry


class TestAgents:
    """Testes de agentes especializados"""
    
    @pytest.mark.asyncio
    async def test_backend_developer(self):
        """Testa Backend Developer agent"""
        agent = BackendDeveloper()
        
        assert agent.profile.name == "Backend Developer"
        assert agent.profile.specialty == AgentSpecialty.BACKEND
        assert agent.profile.area == AgentArea.SOFTWARE_DEVELOPMENT
        
        response = await agent.analyze("Otimizar API", {})
        assert isinstance(response, AgentResponse)
        assert response.confidence > 0
    
    @pytest.mark.asyncio
    async def test_network_engineer(self):
        """Testa Network Engineer agent"""
        agent = NetworkEngineerEnterprise()
        
        assert agent.profile.name == "Network Engineer Enterprise"
        assert agent.profile.specialty == AgentSpecialty.NETWORKS_ENTERPRISE
        
        response = await agent.analyze("Configurar FortiGate", {})
        assert isinstance(response, AgentResponse)


class TestFileClassifier:
    """Testes de classificador de arquivos"""
    
    def test_classify_by_extension(self):
        """Testa classificação por extensão"""
        classifier = FileClassifier()
        
        assert classifier.classify_by_extension("contrato.pdf") == FileCategory.LEGAL
        assert classifier.classify_by_extension("dados.csv") == FileCategory.DATA
        assert classifier.classify_by_extension("config.conf") == FileCategory.NETWORKS
    
    def test_classify_by_content(self):
        """Testa classificação por conteúdo"""
        classifier = FileClassifier()
        
        legal_content = "Este contrato é regido pela LGPD..."
        assert classifier.classify_by_content(legal_content) == FileCategory.LEGAL
        
        network_content = "FortiGate firewall configuration..."
        assert classifier.classify_by_content(network_content) == FileCategory.NETWORKS


class TestReportGenerator:
    """Testes de gerador de relatórios"""
    
    def test_generate_executive_report(self):
        """Testa geração de relatório executivo"""
        generator = ReportGenerator()
        
        analysis_data = {
            "analyses": [{"agent": "Test", "analysis": "Test analysis"}],
            "all_recommendations": ["Rec 1", "Rec 2"],
            "all_risks": ["Risk 1"],
            "average_confidence": 0.85,
            "agents_consulted": 2
        }
        
        config = ReportConfig(
            title="Test Report",
            report_type="executive"
        )
        
        report = generator.generate_executive_report(analysis_data, config)
        
        assert report["metadata"]["title"] == "Test Report"
        assert report["metadata"]["type"] == "executive"
        assert len(report["recommendations"]) > 0


class TestMemory:
    """Testes do sistema de memória"""
    
    def test_add_entry(self):
        """Testa adição de entradaãão"""
        memory = Memory()
        
        entry = MemoryEntry(
            id="test-1",
            type="analysis",
            content={"result": "test"},
            tags=["backend", "api"]
        )
        
        entry_id = memory.add_entry(entry)
        assert entry_id == "test-1"
        assert "test-1" in memory.entries
    
    def test_retrieve_by_tags(self):
        """Testa recuperação por tags"""
        memory = Memory()
        
        entry1 = MemoryEntry(
            id="entry-1",
            type="analysis",
            content={},
            tags=["backend"]
        )
        entry2 = MemoryEntry(
            id="entry-2",
            type="analysis",
            content={},
            tags=["frontend", "backend"]
        )
        
        memory.add_entry(entry1)
        memory.add_entry(entry2)
        
        results = memory.retrieve_by_tags(["backend"])
        assert len(results) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
Scripts de exemplo para usar o sistema multiagente
"""
import asyncio
from app.orchestrator import Orchestrator
from app.langgraph_integration import OrchestratorGraph
from app.qdrant_integration import QdrantVectorStore


async def example_1_analyze_fortigate():
    """
    Exemplo 1: Analisar configuração FortiGate
    """
    print("\n=== Exemplo 1: Análise de FortiGate ===")
    
    orchestrator = Orchestrator()
    graph = OrchestratorGraph(orchestrator)
    
    request = "Analisar arquivo de configuração FortiGate para riscos de segurança"
    file_content = "FortiGate firewall config...\nallow HTTP\nallow HTTPS..."
    
    result = await graph.execute_graph(request, file_content)
    
    print(f"Status: {result['success']}")
    print(f"Verdict: {result['analysis']['verdict']}")
    print(f"\nExecution trace:")
    for trace in result['execution_trace']:
        print(f"  {trace}")


async def example_2_analyze_contract():
    """
    Exemplo 2: Analisar contrato
    """
    print("\n=== Exemplo 2: Análise de Contrato ===")
    
    orchestrator = Orchestrator()
    graph = OrchestratorGraph(orchestrator)
    
    request = "Revisar contrato de prestação de serviços. Identificar riscos LGPD e cláusulas críticas."
    file_content = "CONTRATO DE PRESTAÇÃO...\nCláusula de confiden...\nPrática de LGPD..."
    
    result = await graph.execute_graph(request, file_content)
    
    print(f"Status: {result['success']}")
    print(f"Severity: {result['analysis']['severity']}")
    print(f"\nRecommendations:")
    for rec in result['analysis'].get('recommendations', [])[:3]:
        print(f"  - {rec}")


async def example_3_financial_analysis():
    """
    Exemplo 3: Analisar planilha financeira
    """
    print("\n=== Exemplo 3: Análise Financeira ===")
    
    orchestrator = Orchestrator()
    graph = OrchestratorGraph(orchestrator)
    
    request = "Analisar planilha de receitas e despesas. Identificar tendências e anomalias."
    file_content = "Q1,100000\nQ2,105000\nQ3,103000\nQ4,110000..."
    
    result = await graph.execute_graph(request, file_content)
    
    print(f"Status: {result['success']}")
    print(f"Agents consulted: {result['analysis']['total_agents']}")
    print(f"Average confidence: {result['analysis']['average_confidence']:.2%}")


async def example_4_vector_search():
    """
    Exemplo 4: Busca vetorial com Qdrant
    """
    print("\n=== Exemplo 4: Busca Vetorial ===")
    
    vector_store = QdrantVectorStore()
    
    # Simular embeddings
    texts = [
        "Configuração de firewall",
        "Política de segurança de rede",
        "Auditoria de compliance LGPD"
    ]
    
    vectors = [
        [0.1, 0.2, 0.3, 0.4, 0.5] * 77 + [0.1] * 4,  # 384 dims
        [0.2, 0.3, 0.4, 0.5, 0.6] * 77 + [0.2] * 4,
        [0.3, 0.4, 0.5, 0.6, 0.7] * 77 + [0.3] * 4
    ]
    
    for text, vector in zip(texts, vectors):
        await vector_store.add_embedding(text, vector, {"category": "security"})
    
    print(f"Collection stats: {vector_store.get_collection_stats()}")
    
    # Buscar similares
    query_vector = [0.15, 0.25, 0.35, 0.45, 0.55] * 77 + [0.15] * 4
    results = await vector_store.search_similar(query_vector, top_k=2)
    
    print(f"\nSearch results:")
    for result in results:
        print(f"  - {result['text']} (similarity: {result['similarity_score']:.2%})")


async def main():
    """
    Executa todos os exemplos
    """
    print("\n" + "="*60)
    print("EXEMPLOS DE USO - SISTEMA MULTIAGENTE")
    print("="*60)
    
    await example_1_analyze_fortigate()
    await example_2_analyze_contract()
    await example_3_financial_analysis()
    await example_4_vector_search()
    
    print("\n" + "="*60)
    print("FIM DOS EXEMPLOS")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())

"""
Integração com Qdrant - Busca vetorial e memória semântica
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import hashlib


@dataclass
class VectorEmbedding:
    """
    Representa um embedding vetorial
    """
    id: str
    text: str
    vector: List[float]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text,
            "vector": self.vector,
            "metadata": self.metadata
        }


class QdrantVectorStore:
    """
    Gerenciador de vetores com Qdrant
    Simula operações de busca vetorial sem dependência externa
    """
    
    def __init__(self, collection_name: str = "equipe-operacional", vector_size: int = 384):
        """
        Inicializa o armazenamento vetorial
        
        Args:
            collection_name: Nome da coleção
            vector_size: Tamanho dos vetores
        """
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.vectors: Dict[str, VectorEmbedding] = {}
        self.similarity_cache: Dict[str, List[tuple]] = {}
    
    async def add_embedding(self, text: str, vector: List[float], 
                          metadata: Dict[str, Any] = None) -> str:
        """
        Adiciona um embedding à coleção
        
        Args:
            text: Texto original
            vector: Vetor do embedding
            metadata: Metadados associados
            
        Returns:
            ID do embedding
        """
        if metadata is None:
            metadata = {}
        
        # Gerar ID
        embedding_id = hashlib.md5(text.encode()).hexdigest()
        
        # Validar tamanho do vetor
        if len(vector) != self.vector_size:
            raise ValueError(
                f"Vector size {len(vector)} does not match collection size {self.vector_size}"
            )
        
        # Criar embedding
        embedding = VectorEmbedding(
            id=embedding_id,
            text=text,
            vector=vector,
            metadata=metadata
        )
        
        self.vectors[embedding_id] = embedding
        self.similarity_cache.clear()  # Invalidar cache
        
        return embedding_id
    
    async def search_similar(self, query_vector: List[float], 
                            top_k: int = 5,
                            threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Busca embeddings similares
        
        Args:
            query_vector: Vetor de query
            top_k: Número de resultados
            threshold: Limiar de similaridade
            
        Returns:
            Lista de embeddings similares
        """
        if not self.vectors:
            return []
        
        # Calcular similaridade com todos os vetores
        similarities = []
        
        for embedding_id, embedding in self.vectors.items():
            similarity = self._cosine_similarity(query_vector, embedding.vector)
            
            if similarity >= threshold:
                similarities.append((
                    similarity,
                    embedding
                ))
        
        # Ordenar por similaridade
        similarities.sort(key=lambda x: x[0], reverse=True)
        
        # Retornar top_k
        results = [
            {
                "similarity_score": score,
                "id": emb.id,
                "text": emb.text,
                "metadata": emb.metadata
            }
            for score, emb in similarities[:top_k]
        ]
        
        return results
    
    async def search_by_metadata(self, metadata_filter: Dict[str, Any],
                                top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Busca embeddings por metadados
        
        Args:
            metadata_filter: Filtro de metadados
            top_k: Número de resultados
            
        Returns:
            Lista de embeddings que correspondem
        """
        results = []
        
        for embedding_id, embedding in self.vectors.items():
            if self._match_metadata(embedding.metadata, metadata_filter):
                results.append({
                    "id": embedding.id,
                    "text": embedding.text,
                    "metadata": embedding.metadata
                })
        
        return results[:top_k]
    
    async def update_embedding(self, embedding_id: str, 
                              metadata: Dict[str, Any]) -> bool:
        """
        Atualiza metadados de um embedding
        
        Args:
            embedding_id: ID do embedding
            metadata: Novos metadados
            
        Returns:
            True se atualizado
        """
        if embedding_id not in self.vectors:
            return False
        
        self.vectors[embedding_id].metadata.update(metadata)
        return True
    
    async def delete_embedding(self, embedding_id: str) -> bool:
        """
        Deleta um embedding
        
        Args:
            embedding_id: ID do embedding
            
        Returns:
            True se deletado
        """
        if embedding_id in self.vectors:
            del self.vectors[embedding_id]
            self.similarity_cache.clear()
            return True
        return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas da coleção
        
        Returns:
            Estatísticas
        """
        return {
            "collection_name": self.collection_name,
            "vector_size": self.vector_size,
            "total_embeddings": len(self.vectors),
            "cache_size": len(self.similarity_cache)
        }
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calcula similaridade de cosseno entre dois vetores
        
        Args:
            vec1: Primeiro vetor
            vec2: Segundo vetor
            
        Returns:
            Similaridade entre 0 e 1
        """
        import math
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a ** 2 for a in vec1))
        magnitude2 = math.sqrt(sum(b ** 2 for b in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def _match_metadata(self, metadata: Dict[str, Any], 
                       filter_criteria: Dict[str, Any]) -> bool:
        """
        Verifica se metadados correspondem aos critérios de filtro
        
        Args:
            metadata: Metadados do embedding
            filter_criteria: Critérios de filtro
            
        Returns:
            True se corresponder
        """
        for key, value in filter_criteria.items():
            if key not in metadata or metadata[key] != value:
                return False
        return True
    
    def export_collection(self) -> Dict[str, Any]:
        """
        Exporta a coleção completa
        
        Returns:
            Coleção em formato dict
        """
        return {
            "collection_name": self.collection_name,
            "vector_size": self.vector_size,
            "embeddings": [
                emb.to_dict() for emb in self.vectors.values()
            ]
        }

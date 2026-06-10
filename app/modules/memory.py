"""
Módulo de Memória - Armazena projetos, decisões e histórico
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class MemoryEntry:
    """Entrada na memória do sistema"""
    id: str
    type: str  # "project", "decision", "analysis", "report"
    content: Dict[str, Any]
    agents_involved: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "content": self.content,
            "agents_involved": self.agents_involved,
            "timestamp": self.timestamp,
            "tags": self.tags
        }


class Memory:
    """Gerenciador de memória do sistema"""
    
    def __init__(self):
        self.entries: Dict[str, MemoryEntry] = {}
        self.knowledge_base: Dict[str, List[str]] = {}  # Tópico -> Lista de insights
    
    def add_entry(self, entry: MemoryEntry) -> str:
        """
        Adiciona entrada à memória
        
        Args:
            entry: Entrada a ser armazenada
            
        Returns:
            ID da entrada
        """
        self.entries[entry.id] = entry
        
        # Atualizar base de conhecimento
        for tag in entry.tags:
            if tag not in self.knowledge_base:
                self.knowledge_base[tag] = []
            self.knowledge_base[tag].append(entry.id)
        
        return entry.id
    
    def retrieve_by_tags(self, tags: List[str]) -> List[MemoryEntry]:
        """
        Recupera entradas por tags
        
        Args:
            tags: Lista de tags para busca
            
        Returns:
            Lista de entradas relevantes
        """
        relevant_ids = set()
        
        for tag in tags:
            if tag in self.knowledge_base:
                relevant_ids.update(self.knowledge_base[tag])
        
        return [self.entries[id] for id in relevant_ids if id in self.entries]
    
    def retrieve_by_type(self, entry_type: str) -> List[MemoryEntry]:
        """
        Recupera entradas por tipo
        
        Args:
            entry_type: Tipo de entrada
            
        Returns:
            Lista de entradas do tipo especificado
        """
        return [e for e in self.entries.values() if e.type == entry_type]
    
    def get_agent_history(self, agent_name: str) -> List[MemoryEntry]:
        """
        Retorna histórico de um agente
        
        Args:
            agent_name: Nome do agente
            
        Returns:
            Lista de entradas envolvendo o agente
        """
        return [e for e in self.entries.values() if agent_name in e.agents_involved]
    
    def export_knowledge_base(self) -> Dict[str, Any]:
        """
        Exporta a base de conhecimento
        
        Returns:
            Base de conhecimento estruturada
        """
        return {
            "total_entries": len(self.entries),
            "knowledge_topics": len(self.knowledge_base),
            "knowledge_base": {
                topic: [self.entries[id].to_dict() for id in ids if id in self.entries]
                for topic, ids in self.knowledge_base.items()
            }
        }

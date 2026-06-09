"""
Módulo de Classificação - Identifica automaticamente tipo de arquivo
"""
from enum import Enum
from typing import Tuple
import mimetypes


class FileCategory(Enum):
    """Categorias de arquivo"""
    LEGAL = "legal"
    NETWORKS = "networks"
    SECURITY = "security"
    DATA = "data"
    BUSINESS = "business"
    DEVELOPMENT = "development"
    UNKNOWN = "unknown"


class FileClassifier:
    """Classifica arquivos automaticamente"""
    
    def __init__(self):
        self.category_keywords = {
            FileCategory.LEGAL: ["contrato", "lgpd", "termos", "legal", "clause"],
            FileCategory.NETWORKS: ["fortigate", "cisco", "router", "config", "network"],
            FileCategory.SECURITY: ["firewall", "ssl", "certificate", "encryption"],
            FileCategory.DATA: ["csv", "json", "database", "analytics", "bi"],
            FileCategory.BUSINESS: ["financeiro", "orçamento", "meta", "kpi"],
            FileCategory.DEVELOPMENT: ["code", "api", "repository", "source"],
        }
    
    def classify_by_extension(self, filename: str) -> FileCategory:
        """
        Classifica arquivo por extensão
        
        Args:
            filename: Nome do arquivo
            
        Returns:
            Categoria do arquivo
        """
        extension_map = {
            ".pdf": FileCategory.LEGAL,
            ".docx": FileCategory.LEGAL,
            ".xlsx": FileCategory.DATA,
            ".csv": FileCategory.DATA,
            ".json": FileCategory.DATA,
            ".xml": FileCategory.DATA,
            ".log": FileCategory.DEVELOPMENT,
            ".conf": FileCategory.NETWORKS,
            ".config": FileCategory.NETWORKS,
        }
        
        for ext, category in extension_map.items():
            if filename.lower().endswith(ext):
                return category
        
        return FileCategory.UNKNOWN
    
    def classify_by_content(self, content: str, filename: str = "") -> FileCategory:
        """
        Classifica arquivo por conteúdo
        
        Args:
            content: Conteúdo do arquivo
            filename: Nome do arquivo (opcional)
            
        Returns:
            Categoria do arquivo
        """
        content_lower = content.lower()
        
        # Primeiro tenta por conteúdo
        for category, keywords in self.category_keywords.items():
            if any(kw in content_lower for kw in keywords):
                return category
        
        # Depois por extensão
        if filename:
            return self.classify_by_extension(filename)
        
        return FileCategory.UNKNOWN
    
    def classify_file(self, filename: str, content: str = "") -> Tuple[FileCategory, float]:
        """
        Classifica arquivo com confiança
        
        Args:
            filename: Nome do arquivo
            content: Conteúdo do arquivo (opcional)
            
        Returns:
            Tuple de (categoria, confiança)
        """
        if content:
            category = self.classify_by_content(content, filename)
            confidence = 0.9 if category != FileCategory.UNKNOWN else 0.3
        else:
            category = self.classify_by_extension(filename)
            confidence = 0.7 if category != FileCategory.UNKNOWN else 0.2
        
        return category, confidence

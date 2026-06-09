"""
Módulos da Plataforma
"""
from .file_classifier import FileClassifier, FileCategory
from .memory import Memory, MemoryEntry
from .report_generator import ReportGenerator, ReportConfig

__all__ = [
    "FileClassifier",
    "FileCategory",
    "Memory",
    "MemoryEntry",
    "ReportGenerator",
    "ReportConfig"
]

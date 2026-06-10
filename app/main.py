"""
Aplicação FastAPI - Equipe Operacional
"""
import asyncio
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from datetime import datetime
from typing import List

from app.config import config
from app.models import (
    AnalysisRequest, OrchestratorResponse, FileUploadResponse,
    FileAnalysisRequest, ReportGenerationRequest, HealthCheckResponse
)
from app.orchestrator import Orchestrator
from app.modules.file_uploader import FileUploader
from app.modules.report_generator import ReportGenerator, ReportConfig
from app.modules.memory import Memory, MemoryEntry
from app.modules.file_classifier import FileCategory


# Inicializar FastAPI
app = FastAPI(
    title=config.APP_NAME,
    version=config.VERSION,
    description="Sistema multiagente para análise empresarial"
)

# Adicionar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar componentes
orchestrator = Orchestrator()
file_uploader = FileUploader(config.UPLOAD_DIR)
report_generator = ReportGenerator()
memory = Memory()


# ============================================================================
# HEALTH CHECK E INFORMAÇÕES
# ============================================================================

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Verifica a saúde da aplicação
    """
    return HealthCheckResponse(
        status="healthy",
        version=config.VERSION,
        timestamp=datetime.now(),
        agents_available=len(orchestrator.agents),
        modules=["Orchestrator", "FileUploader", "ReportGenerator", "Memory"]
    )


@app.get("/info")
async def get_info():
    """
    Retorna informações sobre agentes e módulos disponíveis
    """
    return {
        "app_name": config.APP_NAME,
        "version": config.VERSION,
        "agents": [
            {
                "name": agent.profile.name,
                "specialty": agent.profile.specialty.value,
                "area": agent.profile.area.value,
                "description": agent.profile.description,
                "expertise_level": agent.profile.expertise_level
            }
            for agent in orchestrator.agents.values()
        ],
        "supported_file_types": list(FileUploader.ALLOWED_EXTENSIONS),
        "upload_directory": str(config.UPLOAD_DIR),
        "database_url": config.DATABASE_URL
    }


# ============================================================================
# ANÁLISE E ORQUESTRAÇÃO
# ============================================================================

@app.post("/analyze", response_model=OrchestratorResponse)
async def analyze_request(request: AnalysisRequest):
    """
    Processa uma requisição e aciona agentes especializados
    
    Exemplo:
    {
        "request": "Analisar configuração FortiGate",
        "context": {"file": "fortigate.conf"},
        "priority": "high"
    }
    """
    try:
        response = await orchestrator.process_request(
            request.request,
            request.context
        )
        return OrchestratorResponse(**response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agents")
async def list_agents():
    """
    Lista todos os agentes especializados disponíveis
    """
    return {
        "total_agents": len(orchestrator.agents),
        "agents": [
            {
                "id": specialty.value,
                "name": agent.profile.name,
                "specialty": agent.profile.specialty.value,
                "area": agent.profile.area.value,
                "expertise_level": agent.profile.expertise_level,
                "description": agent.profile.description
            }
            for specialty, agent in orchestrator.agents.items()
        ]
    }


@app.post("/analyze-agents")
async def analyze_agent_relevance(request: AnalysisRequest):
    """
    Analisa quais agentes serão relevantes para uma requisição
    """
    relevant_specialties = orchestrator.classify_request(request.request)
    return {
        "request": request.request,
        "relevant_agents": [
            {
                "specialty": s.value,
                "name": orchestrator.agents[s].profile.name if s in orchestrator.agents else "Unknown"
            }
            for s in relevant_specialties
        ],
        "total_relevant": len(relevant_specialties)
    }


# ============================================================================
# UPLOAD E PROCESSAMENTO DE ARQUIVOS
# ============================================================================

@app.post("/upload", response_model=FileUploadResponse)
async def upload_single_file(file: UploadFile = File(...)):
    """
    Realiza upload e processa um arquivo individual
    """
    result = await file_uploader.upload_file(file)
    if result["success"]:
        return FileUploadResponse(**result)
    else:
        raise HTTPException(status_code=400, detail=result["error"])


@app.post("/upload-multiple")
async def upload_multiple_files(files: List[UploadFile] = File(...)):
    """
    Realiza upload de múltiplos arquivos
    """
    results = await file_uploader.upload_multiple(files)
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    
    return {
        "total_files": len(results),
        "successful": len(successful),
        "failed": len(failed),
        "files": results
    }


@app.post("/analyze-file")
async def analyze_file(analysis_request: FileAnalysisRequest):
    """
    Analisa um arquivo uploadado
    """
    processed_files = file_uploader.get_processed_files()
    
    if analysis_request.filename not in processed_files:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    
    file_info = processed_files[analysis_request.filename]
    
    # Processar análise baseada no tipo
    analysis_request_obj = AnalysisRequest(
        request=f"Analisar arquivo {analysis_request.filename}",
        context=file_info
    )
    
    response = await orchestrator.process_request(
        f"Arquivo: {analysis_request.filename}\nCategoria: {file_info.get('category')}",
        file_info
    )
    
    return {
        "file_info": file_info,
        "analysis": response
    }


@app.get("/files")
async def list_processed_files():
    """
    Lista todos os arquivos processados
    """
    processed = file_uploader.get_processed_files()
    return {
        "total_files": len(processed),
        "files": list(processed.values())
    }


@app.get("/files/category/{category}")
async def get_files_by_category(category: str):
    """
    Retorna arquivos filtrados por categoria
    """
    try:
        cat = FileCategory[category.upper()]
        files = file_uploader.get_files_by_category(cat)
        return {
            "category": category,
            "total_files": len(files),
            "files": files
        }
    except KeyError:
        raise HTTPException(
            status_code=400,
            detail=f"Categoria inválida. Válidas: {[c.value for c in FileCategory]}"
        )


# ============================================================================
# RELATÓRIOS
# ============================================================================

@app.post("/generate-report")
async def generate_report(report_request: ReportGenerationRequest):
    """
    Gera relatório baseado em análises
    
    Tipos: executive, technical, action_plan, risk_matrix
    """
    try:
        config_obj = ReportConfig(
            title=report_request.title,
            report_type=report_request.report_type,
            include_recommendations=report_request.include_recommendations,
            include_risks=report_request.include_risks,
            include_timeline=report_request.include_timeline
        )
        
        if report_request.report_type == "executive":
            report = report_generator.generate_executive_report(
                report_request.analysis_data,
                config_obj
            )
        elif report_request.report_type == "technical":
            report = report_generator.generate_technical_report(
                report_request.analysis_data,
                config_obj
            )
        elif report_request.report_type == "action_plan":
            report = report_generator.generate_action_plan(
                report_request.analysis_data,
                config_obj
            )
        elif report_request.report_type == "risk_matrix":
            report = report_generator.generate_risk_matrix(
                report_request.analysis_data,
                config_obj
            )
        else:
            raise ValueError(f"Tipo de relatório inválido: {report_request.report_type}")
        
        return {"success": True, "report": report}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/reports")
async def list_reports():
    """
    Lista todos os relatórios gerados
    """
    return {
        "total_reports": len(report_generator.reports),
        "reports": report_generator.reports
    }


# ============================================================================
# MEMÓRIA E HISTÓRICO
# ============================================================================

@app.get("/memory/history")
async def get_conversation_history():
    """
    Retorna histórico de conversas do orquestrador
    """
    return {
        "total_interactions": len(orchestrator.conversation_history),
        "history": orchestrator.conversation_history[-10:]  # Últimas 10
    }


@app.get("/memory/knowledge-base")
async def get_knowledge_base():
    """
    Retorna base de conhecimento do sistema
    """
    return memory.export_knowledge_base()


@app.get("/memory/entries")
async def get_memory_entries():
    """
    Retorna todas as entradas de memória
    """
    return {
        "total_entries": len(memory.entries),
        "entries": [e.to_dict() for e in memory.entries.values()]
    }


# ============================================================================
# ROOT E DOCUMENTAÇÃO
# ============================================================================

@app.get("/")
async def root():
    """
    Endpoint raiz com informações da API
    """
    return {
        "app_name": config.APP_NAME,
        "version": config.VERSION,
        "description": "Sistema multiagente para análise empresarial",
        "documentation": "/docs",
        "openapi_schema": "/openapi.json",
        "quick_start": {
            "1_upload_file": "POST /upload",
            "2_analyze_request": "POST /analyze",
            "3_generate_report": "POST /generate-report",
            "view_agents": "GET /agents",
            "view_history": "GET /memory/history"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=config.API_HOST,
        port=config.API_PORT,
        reload=config.DEBUG
    )

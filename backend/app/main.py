import os
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import date

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

from app.services.importer import import_b3_excel
from app.db.database import init_db
from app.repositories.operations_repository import (
    create_operation,
    list_operations,
    get_operation_by_id,
    update_operation,
    delete_operation,
    list_operations_by_asset
)
from app.repositories.assets_repository import (
    create_asset,
    get_asset_by_id,
    get_asset_by_ticker,
    list_assets,
    update_asset,
    delete_asset
)


app = FastAPI(title="Portfolio Manager")

# 🔐 CORS CONFIG - Origens específicas via variável de ambiente
# Use CORS_ORIGINS="http://localhost:5173,http://localhost:3000" para múltiplas origens
allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type"],
)

# Modelo Pydantic para validação de ativos
class AssetCreate(BaseModel):
    ticker: str = Field(min_length=1, description="Código de negociação")
    asset_class: str = Field(min_length=1, description="Classe do ativo")
    asset_type: str = Field(min_length=1, description="Tipo do ativo")
    product_name: str = Field(min_length=1, description="Nome do produto")

class AssetUpdate(BaseModel):
    ticker: str = Field(min_length=1, description="Código de negociação")
    asset_class: str = Field(min_length=1, description="Classe do ativo")
    asset_type: str = Field(min_length=1, description="Tipo do ativo")
    product_name: str = Field(min_length=1, description="Nome do produto")

# Modelo Pydantic para validação de operações manuais
class OperationCreate(BaseModel):
    asset_id: int = Field(gt=0, description="ID do ativo")
    movement_type: str = Field(pattern="^(COMPRA|VENDA)$", description="Tipo de movimentação")
    quantity: int = Field(gt=0, description="Quantidade negociada")
    price: float = Field(gt=0, description="Preço unitário")
    trade_date: date = Field(description="Data da operação")
    market: str | None = Field(default=None, description="Mercado")
    institution: str | None = Field(default=None, description="Instituição")

@app.on_event("startup")
def startup():
    logger.info("🚀 Iniciando Portfolio Manager v2")
    init_db()
    logger.info("✓ Aplicação pronta para receber requisições")

@app.get("/health")
def health():
    return {"status": "ok"}

# ========== ENDPOINTS DE ATIVOS ==========

@app.post("/assets")
def create_asset_endpoint(asset: AssetCreate):
    logger.info(f"Recebida requisição de criação de ativo: {asset.ticker}")
    try:
        asset_id = create_asset(
            ticker=asset.ticker,
            asset_class=asset.asset_class,
            asset_type=asset.asset_type,
            product_name=asset.product_name
        )
        logger.info(f"Ativo {asset.ticker} criado com ID {asset_id}")
        return {"status": "success", "asset_id": asset_id}
    except Exception as e:
        logger.error(f"Erro ao criar ativo: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/assets")
def get_assets():
    logger.debug("Recebida requisição de listagem de ativos")
    try:
        assets = list_assets()
        return assets
    except Exception as e:
        logger.error(f"Erro ao listar ativos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/assets/{asset_id}")
def get_asset(asset_id: int):
    logger.debug(f"Recebida requisição para buscar ativo ID: {asset_id}")
    try:
        asset = get_asset_by_id(asset_id)
        if not asset:
            raise HTTPException(status_code=404, detail=f"Ativo {asset_id} não encontrado")
        return asset
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar ativo: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/assets/{asset_id}")
def update_asset_endpoint(asset_id: int, asset: AssetUpdate):
    logger.info(f"Recebida requisição de atualização para ativo ID: {asset_id}")
    try:
        update_asset(
            asset_id=asset_id,
            ticker=asset.ticker,
            asset_class=asset.asset_class,
            asset_type=asset.asset_type,
            product_name=asset.product_name
        )
        logger.info(f"Ativo {asset_id} atualizado")
        return {"status": "success", "message": "Ativo atualizado com sucesso"}
    except ValueError as e:
        logger.warning(f"Erro de validação ao atualizar ativo: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao atualizar ativo: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/assets/{asset_id}")
def delete_asset_endpoint(asset_id: int):
    logger.info(f"Recebida requisição de exclusão para ativo ID: {asset_id}")
    try:
        delete_asset(asset_id)
        logger.info(f"Ativo {asset_id} deletado com sucesso")
        return {"status": "success", "message": "Ativo deletado com sucesso"}
    except ValueError as e:
        logger.warning(f"Erro de validação ao deletar ativo: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao deletar ativo: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/assets/{asset_id}/operations")
def get_asset_operations(asset_id: int):
    logger.debug(f"Recebida requisição de operações do ativo ID: {asset_id}")
    try:
        # Verificar se o ativo existe
        asset = get_asset_by_id(asset_id)
        if not asset:
            raise HTTPException(status_code=404, detail=f"Ativo {asset_id} não encontrado")
        
        operations = list_operations_by_asset(asset_id)
        return operations
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao listar operações do ativo: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ========== ENDPOINTS DE IMPORTAÇÃO ==========

@app.post("/import/b3")
async def import_b3(file: UploadFile = File(...)):
    logger.info(f"Recebida requisição de importação: {file.filename}")
    try:
        summary = import_b3_excel(file)
        logger.info(f"Importação bem-sucedida: {summary['inserted']} ops inseridas, {summary['duplicated']} duplicadas")
        return {
            "status": "success",
            "summary": summary
        }
    except Exception as e:
        logger.error(f"Erro na importação: {str(e)}")
        raise

@app.post("/operations")
def create_manual_operation(operation: OperationCreate):
    logger.info(f"Recebida requisição de operação manual: Asset ID {operation.asset_id} - {operation.movement_type}")
    try:
        # Verificar se o ativo existe
        asset = get_asset_by_id(operation.asset_id)
        if not asset:
            raise HTTPException(status_code=404, detail=f"Ativo {operation.asset_id} não encontrado")
        
        payload = operation.model_dump()
        # Converter date para string ISO
        payload["trade_date"] = payload["trade_date"].isoformat()
        payload["source"] = "MANUAL"
        create_operation(payload)
        logger.info(f"Operação manual criada com sucesso para ativo {asset['ticker']}")
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar operação manual: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/operations")
def get_operations():
    logger.debug("Recebida requisição de listagem de operações")
    try:
        operations = list_operations()
        return operations
    except Exception as e:
        logger.error(f"Erro ao listar operações: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/operations/{operation_id}")
def get_operation(operation_id: int):
    logger.debug(f"Recebida requisição para buscar operação ID: {operation_id}")
    try:
        operation = get_operation_by_id(operation_id)
        if not operation:
            raise HTTPException(status_code=404, detail=f"Operação {operation_id} não encontrada")
        return operation
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar operação: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/operations/{operation_id}")
def update_operation_endpoint(operation_id: int, operation: OperationCreate):
    logger.info(f"Recebida requisição de atualização para operação ID: {operation_id}")
    try:
        # Verificar se o ativo existe
        asset = get_asset_by_id(operation.asset_id)
        if not asset:
            raise HTTPException(status_code=404, detail=f"Ativo {operation.asset_id} não encontrado")
        
        payload = operation.model_dump()
        # Converter date para string ISO
        payload["trade_date"] = payload["trade_date"].isoformat()
        payload["source"] = "MANUAL"
        
        new_id = update_operation(operation_id, payload)
        
        logger.info(f"Operação {operation_id} atualizada (nova operação ID: {new_id})")
        return {
            "status": "success",
            "message": "Operação atualizada com sucesso",
            "old_id": operation_id,
            "new_id": new_id
        }
    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"Erro de validação ao atualizar operação: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao atualizar operação: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/operations/{operation_id}")
def delete_operation_endpoint(operation_id: int):
    logger.info(f"Recebida requisição de exclusão para operação ID: {operation_id}")
    try:
        delete_operation(operation_id)
        logger.info(f"Operação {operation_id} deletada com sucesso")
        return {
            "status": "success",
            "message": "Operação deletada com sucesso",
            "deleted_id": operation_id
        }
    except ValueError as e:
        logger.warning(f"Erro de validação ao deletar operação: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao deletar operação: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
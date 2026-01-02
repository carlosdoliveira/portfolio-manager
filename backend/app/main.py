import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import date

from app.services.importer import import_b3_excel
from app.db.database import init_db
from app.repositories.operations_repository import create_operation, list_operations


app = FastAPI(title="Portfolio Manager")

# 🔐 CORS CONFIG - Origens específicas via variável de ambiente
# Use CORS_ORIGINS="http://localhost:5173,http://localhost:3000" para múltiplas origens
allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# Modelo Pydantic para validação de operações manuais
class OperationCreate(BaseModel):
    asset_class: str = Field(min_length=1, description="Classe do ativo")
    asset_type: str = Field(min_length=1, description="Tipo do ativo")
    product_name: str = Field(min_length=1, description="Nome do produto")
    ticker: str | None = Field(default=None, description="Código de negociação")
    movement_type: str = Field(pattern="^(COMPRA|VENDA)$", description="Tipo de movimentação")
    quantity: int = Field(gt=0, description="Quantidade negociada")
    price: float = Field(gt=0, description="Preço unitário")
    trade_date: date = Field(description="Data da operação")
    market: str | None = Field(default=None, description="Mercado")
    institution: str | None = Field(default=None, description="Instituição")

@app.on_event("startup")
def startup():
    init_db()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/import/b3")
async def import_b3(file: UploadFile = File(...)):
    summary = import_b3_excel(file)
    return {
        "status": "success",
        "summary": summary
    }

@app.post("/operations")
def create_manual_operation(operation: OperationCreate):
    try:
        payload = operation.model_dump()
        # Converter date para string ISO
        payload["trade_date"] = payload["trade_date"].isoformat()
        payload["source"] = "MANUAL"
        create_operation(payload)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/operations")
def get_operations():
    return list_operations()
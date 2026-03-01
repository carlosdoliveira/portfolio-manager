import os
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import date
import asyncio

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

from app.services.importer import import_b3_excel, normalize_ticker
from app.services.reconciliation import (
    import_position_snapshot,
    get_reconciliation_diagnosis,
    auto_fix_positions
)
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
    get_asset_with_stats,
    get_asset_by_ticker,
    list_assets,
    update_asset,
    delete_asset
)
from app.repositories.dashboard_repository import (
    get_dashboard_summary
)
from app.repositories.quotes_repository import (
    save_quote,
    get_quote,
    get_all_quotes,
    get_tickers_to_update
)
from app.repositories.fixed_income_repository import (
    create_fixed_income_asset,
    list_fixed_income_assets,
    get_fixed_income_by_asset_id,
    update_fixed_income_asset,
    create_fixed_income_operation,
    list_fixed_income_operations,
    calculate_fixed_income_projection,
    delete_fixed_income_asset
)
from app.services.market_data_service import get_market_data_service
from app.services.position_engine import (
    compute_asset_position,
    compute_asset_position_by_ticker,
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

# Modelos Pydantic para Renda Fixa
class FixedIncomeAssetCreate(BaseModel):
    asset_id: int = Field(gt=0, description="ID do ativo base")
    issuer: str = Field(min_length=1, description="Emissor (Banco, Tesouro Nacional)")
    product_type: str = Field(min_length=1, description="Tipo (CDB, LCI, LCA, TESOURO_SELIC, etc.)")
    indexer: str = Field(min_length=1, description="Indexador (CDI, IPCA, PRE, SELIC)")
    rate: float = Field(gt=0, description="Taxa contratada (%)")
    maturity_date: date = Field(description="Data de vencimento")
    issue_date: date = Field(description="Data de emissão")
    custody_fee: float = Field(default=0.0, ge=0, description="Taxa de custódia anual (%)")

class FixedIncomeOperationCreate(BaseModel):
    asset_id: int = Field(gt=0, description="ID do ativo")
    operation_type: str = Field(pattern="^(APLICACAO|RESGATE|VENCIMENTO)$", description="Tipo de operação")
    amount: float = Field(gt=0, description="Valor bruto")
    trade_date: date = Field(description="Data da operação")
    net_amount: float | None = Field(default=None, description="Valor líquido após IR")
    ir_amount: float = Field(default=0.0, ge=0, description="Valor do IR retido")

# Modelo Pydantic para ajustes de posição (eventos corporativos)
class PositionAdjustment(BaseModel):
    asset_id: int = Field(gt=0, description="ID do ativo")
    adjustment_type: str = Field(
        pattern="^(BONIFICACAO|DESDOBRO|GRUPAMENTO|SUBSCRICAO|CORRECAO)$",
        description="Tipo de ajuste"
    )
    quantity: float = Field(description="Quantidade ajustada (positiva ou negativa)")
    event_date: date = Field(description="Data do evento corporativo")
    description: str = Field(min_length=1, description="Descrição do ajuste")

@app.on_event("startup")
def startup():
    logger.info("🚀 Iniciando Portfolio Manager v2")
    init_db()
    logger.info("✓ Aplicação pronta para receber requisições")

@app.get("/health")
def health():
    return {"status": "ok"}

# ========== DASHBOARD ==========

@app.get("/dashboard/summary")
def get_dashboard():
    """
    Retorna um resumo completo da carteira para o dashboard.
    
    Inclui:
    - Totalizadores (total investido, valor atual, número de ativos)
    - Top 5 posições
    - Operações recentes (últimas 10)
    - Distribuição por classe de ativo
    """
    try:
        logger.info("📊 Buscando resumo do dashboard")
        summary = get_dashboard_summary()
        return summary
    except Exception as e:
        logger.error(f"Erro ao buscar resumo do dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar resumo: {str(e)}")

# ========== ENDPOINTS DE COTAÇÕES ==========

@app.post("/quotes/update")
def update_quotes():
    """
    Atualiza cotações de todos os ativos com posição.
    Busca do yfinance e salva no cache do banco de dados.
    """
    try:
        logger.info("🔄 Iniciando atualização de cotações")
        
        # Buscar tickers que precisam atualização
        tickers = get_tickers_to_update()
        
        if not tickers:
            return {"message": "Nenhum ticker para atualizar", "updated": 0}
        
        logger.info(f"📋 {len(tickers)} tickers para atualizar: {', '.join(tickers[:5])}{'...' if len(tickers) > 5 else ''}")
        
        # Buscar cotações em lote do yfinance
        market_service = get_market_data_service()
        quotes = market_service.get_batch_quotes(tickers)
        
        # Salvar no banco
        updated_count = 0
        for ticker, quote_data in quotes.items():
            if quote_data:
                if save_quote(
                    ticker=ticker,
                    price=quote_data.get("price"),
                    change_value=quote_data.get("change_value"),
                    change_percent=quote_data.get("change_percent"),
                    volume=quote_data.get("volume"),
                    open_price=quote_data.get("open_price"),
                    high_price=quote_data.get("high_price"),
                    low_price=quote_data.get("low_price"),
                    previous_close=quote_data.get("previous_close"),
                    source="yfinance"
                ):
                    updated_count += 1
        
        logger.info(f"✅ {updated_count} cotações atualizadas com sucesso")
        
        return {
            "message": f"{updated_count} cotações atualizadas",
            "total_tickers": len(tickers),
            "updated": updated_count
        }
        
    except Exception as e:
        logger.error(f"Erro ao atualizar cotações: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar cotações: {str(e)}")

@app.get("/quotes")
def list_quotes():
    """
    Lista todas as cotações armazenadas no cache.
    """
    try:
        quotes = get_all_quotes()
        return quotes
    except Exception as e:
        logger.error(f"Erro ao listar cotações: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao listar cotações: {str(e)}")

@app.get("/quotes/{ticker}")
def get_quote_endpoint(ticker: str):
    """
    Busca cotação de um ticker específico do cache.
    """
    try:
        quote = get_quote(ticker.upper())
        if not quote:
            raise HTTPException(status_code=404, detail=f"Cotação de {ticker} não encontrada")
        return quote
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar cotação de {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar cotação: {str(e)}")

# ========== ENDPOINTS DE ATIVOS ==========

@app.post("/assets")
def create_asset_endpoint(asset: AssetCreate):
    logger.info(f"Recebida requisição de criação de ativo: {asset.ticker}")
    try:
        # Normalizar ticker para consolidar fracionário/vista
        # Assumir mercado fracionário se terminar com F
        market_hint = "MERCADO FRACIONARIO" if asset.ticker.upper().endswith("F") else "MERCADO A VISTA"
        ticker_normalized = normalize_ticker(asset.ticker, market_hint)
        
        if ticker_normalized != asset.ticker:
            logger.info(f"Ticker normalizado: {asset.ticker} -> {ticker_normalized}")
        
        asset_id = create_asset(
            ticker=ticker_normalized,
            asset_class=asset.asset_class,
            asset_type=asset.asset_type,
            product_name=asset.product_name
        )
        logger.info(f"Ativo {ticker_normalized} criado com ID {asset_id}")
        return {"status": "success", "asset_id": asset_id, "ticker": ticker_normalized}
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
        asset = get_asset_with_stats(asset_id)
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
        # Normalizar ticker para consolidar fracionário/vista
        market_hint = "MERCADO FRACIONARIO" if asset.ticker.upper().endswith("F") else "MERCADO A VISTA"
        ticker_normalized = normalize_ticker(asset.ticker, market_hint)
        
        if ticker_normalized != asset.ticker:
            logger.info(f"Ticker normalizado na atualização: {asset.ticker} -> {ticker_normalized}")
        
        update_asset(
            asset_id=asset_id,
            ticker=ticker_normalized,
            asset_class=asset.asset_class,
            asset_type=asset.asset_type,
            product_name=asset.product_name
        )
        logger.info(f"Ativo {asset_id} atualizado com ticker {ticker_normalized}")
        return {"status": "success", "message": "Ativo atualizado com sucesso", "ticker": ticker_normalized}
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
        
        # Alertar sobre eventos corporativos detectados
        if summary.get("events_detected", 0) > 0:
            logger.info(f"⚠️  {summary['events_detected']} eventos corporativos detectados")
        
        return {
            "status": "success",
            "summary": summary
        }
    except Exception as e:
        logger.error(f"Erro na importação: {str(e)}")
        raise

# Modelo para aplicar eventos em lote
class ApplyCorporateEventsRequest(BaseModel):
    events: list[dict] = Field(description="Lista de eventos corporativos a aplicar")

@app.post("/admin/apply-corporate-events")
async def apply_corporate_events(request: ApplyCorporateEventsRequest):
    """
    Aplica eventos corporativos detectados em lote.
    
    Cada evento deve ter:
    - type: BONIFICACAO, DESDOBRO, GRUPAMENTO, SUBSCRICAO, CORRECAO
    - ticker: Código do ativo
    - quantity: Quantidade ajustada
    - date: Data do evento
    - description: Descrição
    """
    logger.info(f"Aplicando {len(request.events)} eventos corporativos em lote")
    
    applied = 0
    errors = []
    results = []
    
    for event in request.events:
        try:
            # Pular eventos marcados para skip (leilões de fração)
            if event.get("skip"):
                logger.debug(f"Pulando evento: {event.get('description')}")
                continue
            
            # Buscar asset_id pelo ticker
            ticker = event.get("ticker")
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM assets WHERE ticker = ?", (ticker,))
                result = cursor.fetchone()
                
                if not result:
                    errors.append(f"Ativo {ticker} não encontrado")
                    continue
                
                asset_id = result[0]
            
            # Preparar dados do ajuste
            adjustment = {
                "asset_id": asset_id,
                "movement_type": "COMPRA" if event["quantity"] > 0 else "VENDA",
                "operation_subtype": event["type"],
                "quantity": abs(event["quantity"]),
                "price": 0.0,
                "value": 0.0,
                "trade_date": event["date"],
                "source": "AJUSTE_LOTE",
                "notes": event["description"],
                "market": None,
                "institution": None
            }
            
            # Criar operação
            create_operation(adjustment)
            applied += 1
            
            results.append({
                "ticker": ticker,
                "type": event["type"],
                "quantity": event["quantity"],
                "status": "success"
            })
            
            logger.debug(f"Evento aplicado: {ticker} - {event['type']} - {event['quantity']}")
            
        except Exception as e:
            error_msg = f"{event.get('ticker')}: {str(e)}"
            errors.append(error_msg)
            logger.error(f"Erro ao aplicar evento: {error_msg}")
            results.append({
                "ticker": event.get("ticker"),
                "type": event.get("type"),
                "status": "error",
                "error": str(e)
            })
    
    logger.info(f"Eventos aplicados: {applied}/{len(request.events)} - {len(errors)} erros")
    
    return {
        "status": "success" if applied > 0 else "error",
        "applied": applied,
        "total": len(request.events),
        "errors": errors,
        "results": results
    }

# ========== ENDPOINTS DE RECONCILIAÇÃO ==========

@app.post("/admin/import-position")
async def import_position(file: UploadFile = File(...)):
    """
    Importa arquivo de posição B3 (posicao-*.xlsx) como fonte de verdade.
    Cria snapshots das posições e identifica discrepâncias com o calculado.
    """
    logger.info(f"Importando posição B3: {file.filename}")
    try:
        result = import_position_snapshot(file)
        logger.info(f"Posição importada: {result['snapshots_created']} ativos, {result['discrepancies_found']} discrepâncias")
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        logger.error(f"Erro ao importar posição: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/reconciliation/diagnosis")
async def reconciliation_diagnosis():
    """
    Retorna diagnóstico completo da reconciliação:
    - Posições conforme snapshots (fonte de verdade B3)
    - Posições calculadas do sistema
    - Discrepâncias encontradas
    - Análise de causas
    - Sugestões de correção
    """
    logger.info("Gerando diagnóstico de reconciliação")
    try:
        diagnosis = get_reconciliation_diagnosis()
        issues_count = len(diagnosis.get('issues', []))
        logger.info(f"Diagnóstico gerado: {issues_count} discrepâncias")
        return {
            "status": "success",
            "diagnosis": diagnosis
        }
    except Exception as e:
        logger.error(f"Erro ao gerar diagnóstico: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/reconciliation/auto-fix")
async def reconciliation_auto_fix(ticker: str | None = None):
    """
    Aplica correções automáticas criando operações de ajuste.
    
    - Se ticker=None: corrige todos os ativos com discrepância
    - Se ticker informado: corrige apenas aquele ativo
    
    Cria operações do tipo AJUSTE_RECONCILIACAO para zerar diferenças.
    """
    logger.info(f"Aplicando correções automáticas{' para ' + ticker if ticker else ' para todos os ativos'}")
    try:
        result = auto_fix_positions(ticker)
        fixed_count = result.get('fixed_count', 0)
        logger.info(f"Correções aplicadas: {fixed_count} ajustes")
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        logger.error(f"Erro ao aplicar correções: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ========== ENDPOINTS DE POSIÇÃO (ENGINE) ==========

@app.get("/assets/{ticker}/position")
async def get_asset_position(ticker: str):
    """
    Retorna posição calculada pelo engine (considera eventos corporativos).
    """
    try:
        result = compute_asset_position_by_ticker(ticker)
        return {"status": "success", "position": result}
    except Exception as e:
        logger.error(f"Erro ao calcular posição de {ticker}: {e}")
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/positions/recalculate")
async def recalculate_all_positions():
    """
    Recalcula posição de todos os ativos ativos usando o engine.
    Útil para validação pós-import.
    """
    summary = []
    try:
        assets = list_assets()
        for a in assets:
            try:
                pos = compute_asset_position(a["id"])
                summary.append({
                    "ticker": a["ticker"],
                    "quantity": pos["quantity"],
                    "avg_price": pos["average_price"],
                    "invested_value": pos["invested_value"],
                })
            except Exception as e:
                logger.warning(f"Falha ao calcular {a['ticker']}: {e}")
        return {"status": "success", "count": len(summary), "positions": summary}
    except Exception as e:
        logger.error(f"Erro ao recalcular posições: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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

# ========== ENDPOINTS DE AJUSTES DE POSIÇÃO (EVENTOS CORPORATIVOS) ==========

@app.post("/admin/position-adjustment")
def adjust_position(adjustment: PositionAdjustment):
    """
    Registra ajuste manual de posição (bonificação, desdobro, etc).
    
    Cria uma operação especial com price=0 e source=AJUSTE.
    O preço médio é recalculado automaticamente considerando custo zero.
    """
    logger.info(f"Recebida requisição de ajuste de posição: Asset ID {adjustment.asset_id} - {adjustment.adjustment_type}")
    try:
        # Verificar se o ativo existe
        asset = get_asset_by_id(adjustment.asset_id)
        if not asset:
            raise HTTPException(status_code=404, detail=f"Ativo {adjustment.asset_id} não encontrado")
        
        # Determinar movimento_type baseado na quantidade
        movement_type = "COMPRA" if adjustment.quantity > 0 else "VENDA"
        
        # Criar operação especial de ajuste
        operation_data = {
            "asset_id": adjustment.asset_id,
            "movement_type": movement_type,
            "operation_subtype": adjustment.adjustment_type,
            "quantity": abs(adjustment.quantity),
            "price": 0.0,  # Custo zero para eventos corporativos
            "value": 0.0,
            "trade_date": adjustment.event_date.isoformat(),
            "source": "AJUSTE",
            "notes": adjustment.description,
            "market": None,
            "institution": None
        }
        
        create_operation(operation_data)
        
        # Recalcular posição atual
        operations = list_operations_by_asset(adjustment.asset_id)
        total_quantity = 0
        total_cost = 0.0
        
        for op in operations:
            qty = op['quantity']
            price = op['price']
            
            if op['movement_type'] == 'COMPRA':
                total_quantity += qty
                total_cost += (qty * price)
            elif op['movement_type'] == 'VENDA':
                total_quantity -= qty
                # Não ajusta custo na venda, mantém proporção
        
        # Calcular novo preço médio
        avg_price = total_cost / total_quantity if total_quantity > 0 else 0.0
        
        logger.info(f"Ajuste criado: {adjustment.adjustment_type} de {adjustment.quantity} {asset['ticker']}")
        logger.info(f"Nova posição: {total_quantity} @ R$ {avg_price:.2f}")
        
        return {
            "status": "success",
            "message": f"Ajuste de posição registrado com sucesso",
            "asset": asset['ticker'],
            "adjustment_type": adjustment.adjustment_type,
            "new_position": {
                "quantity": total_quantity,
                "average_price": round(avg_price, 2),
                "total_cost": round(total_cost, 2)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao registrar ajuste de posição: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao registrar ajuste: {str(e)}")

# ========== ENDPOINTS DE RENDA FIXA ==========

@app.post("/fixed-income/assets")
def create_fixed_income_asset_endpoint(fi_asset: FixedIncomeAssetCreate):
    logger.info(f"Recebida requisição de criação de Renda Fixa para asset {fi_asset.asset_id}")
    try:
        # Verificar se o ativo existe
        asset = get_asset_by_id(fi_asset.asset_id)
        if not asset:
            raise HTTPException(status_code=404, detail=f"Ativo {fi_asset.asset_id} não encontrado")
        
        fi_id = create_fixed_income_asset(
            asset_id=fi_asset.asset_id,
            issuer=fi_asset.issuer,
            product_type=fi_asset.product_type,
            indexer=fi_asset.indexer,
            rate=fi_asset.rate,
            maturity_date=fi_asset.maturity_date.isoformat(),
            issue_date=fi_asset.issue_date.isoformat(),
            custody_fee=fi_asset.custody_fee
        )
        logger.info(f"Renda Fixa criada com ID {fi_id}")
        return {"status": "success", "fixed_income_id": fi_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar Renda Fixa: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/fixed-income/assets")
def get_fixed_income_assets():
    logger.debug("Recebida requisição de listagem de Renda Fixa")
    try:
        assets = list_fixed_income_assets()
        return assets
    except Exception as e:
        logger.error(f"Erro ao listar Renda Fixa: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/fixed-income/assets/{asset_id}")
def get_fixed_income_asset(asset_id: int):
    logger.debug(f"Recebida requisição para buscar Renda Fixa do asset ID: {asset_id}")
    try:
        fi_asset = get_fixed_income_by_asset_id(asset_id)
        if not fi_asset:
            raise HTTPException(status_code=404, detail=f"Renda Fixa não encontrada para asset {asset_id}")
        return fi_asset
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar Renda Fixa: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/fixed-income/assets/{asset_id}")
def delete_fixed_income_asset_endpoint(asset_id: int):
    logger.info(f"Recebida requisição de exclusão de Renda Fixa para asset {asset_id}")
    try:
        delete_fixed_income_asset(asset_id)
        logger.info(f"Renda Fixa do asset {asset_id} deletada")
        return {"status": "success", "message": "Renda Fixa deletada com sucesso"}
    except ValueError as e:
        logger.warning(f"Erro de validação ao deletar Renda Fixa: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao deletar Renda Fixa: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/fixed-income/assets/{asset_id}")
def update_fixed_income_asset_endpoint(asset_id: int, updates: FixedIncomeAssetCreate):
    logger.info(f"Recebida requisição de atualização de Renda Fixa para asset {asset_id}")
    try:
        success = update_fixed_income_asset(
            asset_id=asset_id,
            issuer=updates.issuer,
            product_type=updates.product_type,
            indexer=updates.indexer,
            rate=updates.rate,
            maturity_date=updates.maturity_date.isoformat(),
            issue_date=updates.issue_date.isoformat(),
            custody_fee=updates.custody_fee
        )
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Renda Fixa não encontrada para asset {asset_id}")
        
        logger.info(f"Renda Fixa do asset {asset_id} atualizada com sucesso")
        return {"status": "success", "message": "Renda Fixa atualizada com sucesso"}
    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"Erro de validação ao atualizar Renda Fixa: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao atualizar Renda Fixa: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/fixed-income/operations")
def create_fixed_income_operation_endpoint(operation: FixedIncomeOperationCreate):
    logger.info(f"Recebida requisição de operação de Renda Fixa: {operation.operation_type} para asset {operation.asset_id}")
    try:
        op_id = create_fixed_income_operation(
            asset_id=operation.asset_id,
            operation_type=operation.operation_type,
            amount=operation.amount,
            trade_date=operation.trade_date.isoformat(),
            net_amount=operation.net_amount,
            ir_amount=operation.ir_amount
        )
        logger.info(f"Operação de Renda Fixa criada com ID {op_id}")
        return {"status": "success", "operation_id": op_id}
    except Exception as e:
        logger.error(f"Erro ao criar operação de Renda Fixa: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/fixed-income/operations/{asset_id}")
def get_fixed_income_operations_endpoint(asset_id: int):
    logger.debug(f"Recebida requisição de operações de Renda Fixa para asset {asset_id}")
    try:
        operations = list_fixed_income_operations(asset_id)
        return operations
    except Exception as e:
        logger.error(f"Erro ao listar operações de Renda Fixa: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/fixed-income/projection/{asset_id}")
def get_fixed_income_projection_endpoint(
    asset_id: int,
    cdi_rate: float = 13.75,
    ipca_rate: float = 4.5
):
    logger.debug(f"Recebida requisição de projeção para asset {asset_id}")
    try:
        projection = calculate_fixed_income_projection(
            asset_id=asset_id,
            current_cdi_rate=cdi_rate,
            current_ipca_rate=ipca_rate
        )
        return projection
    except Exception as e:
        logger.error(f"Erro ao calcular projeção: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# ==========================================
# 📈 ENDPOINTS DE COTAÇÕES
# ==========================================

@app.get("/quotes/{ticker}")
def get_quote_endpoint(ticker: str):
    """
    Busca cotação de um ativo específico.
    
    Args:
        ticker: Código do ativo (ex: PETR4, VALE3)
    
    Returns:
        Dados da cotação ou 404 se não encontrado
        
    Exemplo:
        GET /quotes/PETR4
        
        {
            "ticker": "PETR4",
            "price": 38.50,
            "change": 0.85,
            "change_percent": 2.26,
            "volume": 25000000,
            ...
        }
    """
    logger.debug(f"Recebida requisição de cotação para {ticker}")
    
    try:
        market_service = get_market_data_service()
        quote = market_service.get_quote(ticker)
        
        if quote is None:
            raise HTTPException(
                status_code=404,
                detail=f"Cotação não encontrada para o ticker {ticker}"
            )
        
        return quote
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar cotação de {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/quotes/batch")
def get_batch_quotes_endpoint(tickers: list[str]):
    """
    Busca cotações de múltiplos ativos de uma vez.
    
    Args:
        tickers: Lista de códigos de ativos
    
    Returns:
        Dicionário com ticker -> dados da cotação
        
    Exemplo:
        POST /quotes/batch
        Body: ["PETR4", "VALE3", "ITUB4"]
        
        {
            "PETR4": {...},
            "VALE3": {...},
            "ITUB4": {...}
        }
    """
    logger.debug(f"Recebida requisição de cotações em lote: {tickers}")
    
    if not tickers:
        raise HTTPException(status_code=400, detail="Lista de tickers não pode estar vazia")
    
    if len(tickers) > 50:
        raise HTTPException(status_code=400, detail="Máximo de 50 tickers por requisição")
    
    try:
        market_service = get_market_data_service()
        quotes = market_service.get_batch_quotes(tickers)
        return quotes
        
    except Exception as e:
        logger.error(f"Erro ao buscar cotações em lote: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/quotes/portfolio/current")
def get_portfolio_quotes_endpoint():
    """
    Busca cotações de todos os ativos com posição atual no portfólio.
    
    IMPORTANTE: Usa cache de cotações quando disponível (atualizado a cada 15 min via cron).
    Busca cotação em tempo real via yfinance apenas se não houver cache.
    
    Returns:
        Dicionário com ticker -> cotação para todos os ativos em carteira
    """
    logger.debug("Recebida requisição de cotações do portfólio")
    
    try:
        # Buscar todos os ativos com posição
        assets = list_assets()
        
        # Filtrar apenas ativos com posição atual > 0
        tickers_with_position = []
        for asset in assets:
            if asset.get('current_position', 0) > 0:
                tickers_with_position.append(asset['ticker'])
        
        if not tickers_with_position:
            return {}
        
        # Buscar cotações usando o sistema de cache
        market_service = get_market_data_service()
        quotes_result = {}
        
        for ticker in tickers_with_position:
            # 1. Tentar cache primeiro
            cached_quote = get_quote(ticker)
            
            if cached_quote:
                logger.debug(f"📦 {ticker}: usando cotação do cache")
                quotes_result[ticker] = {
                    "price": cached_quote["price"],
                    "change_percent": cached_quote.get("change_percent"),
                    "change_value": cached_quote.get("change_value"),
                    "volume": cached_quote.get("volume"),
                    "source": "cache"
                }
            else:
                # 2. Se não houver cache, buscar via yfinance
                logger.debug(f"🌐 {ticker}: buscando cotação via yfinance")
                try:
                    quote = market_service.get_quote(ticker)
                    if quote and quote.get("price"):
                        quotes_result[ticker] = quote
                        
                        # Salvar no cache para próximas requisições
                        save_quote(
                            ticker=ticker,
                            price=quote["price"],
                            change_value=quote.get("change_value"),
                            change_percent=quote.get("change_percent"),
                            volume=quote.get("volume"),
                            open_price=quote.get("open_price"),
                            high_price=quote.get("high_price"),
                            low_price=quote.get("low_price"),
                            previous_close=quote.get("previous_close"),
                            source="yfinance"
                        )
                        logger.debug(f"💾 {ticker}: cotação salva no cache")
                except Exception as e:
                    logger.error(f"Erro ao buscar cotação de {ticker}: {str(e)}")
                    # Continuar com próximo ticker em caso de erro
                    continue
        
        return quotes_result
        
    except Exception as e:
        logger.error(f"Erro ao buscar cotações do portfólio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/quotes/cache/{ticker}")
def clear_quote_cache_endpoint(ticker: str):
    """
    Limpa o cache de cotação de um ativo específico.
    
    Args:
        ticker: Código do ativo
    
    Returns:
        Mensagem de sucesso
    """
    logger.debug(f"Limpando cache de cotação para {ticker}")
    
    try:
        market_service = get_market_data_service()
        market_service.clear_cache(ticker)
        return {"status": "success", "message": f"Cache limpo para {ticker}"}
        
    except Exception as e:
        logger.error(f"Erro ao limpar cache: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/quotes/cache")
def clear_all_quotes_cache_endpoint():
    """
    Limpa todo o cache de cotações.
    
    Returns:
        Mensagem de sucesso
    """
    logger.debug("Limpando todo o cache de cotações")
    
    try:
        market_service = get_market_data_service()
        market_service.clear_cache()
        return {"status": "success", "message": "Cache de cotações limpo"}
        
    except Exception as e:
        logger.error(f"Erro ao limpar cache: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/quotes/portfolio/fast")
def get_portfolio_quotes_fast(background_tasks: BackgroundTasks, refresh: bool = False):
    """
    Busca cotações do portfólio de forma otimizada.
    
    Estratégia:
    1. Retorna imediatamente cotações do cache persistente (banco de dados)
    2. Se refresh=true, dispara atualização em background para próximas consultas
    
    Args:
        refresh: Se True, atualiza cotações em background após retornar cache
    
    Returns:
        Dicionário com ticker -> cotação do cache
    """
    logger.debug(f"Requisição rápida de cotações (refresh={refresh})")
    
    try:
        # Buscar todos os ativos com posição
        assets = list_assets()
        
        # Filtrar apenas ativos com posição atual > 0
        tickers_with_position = []
        for asset in assets:
            if asset.get('current_position', 0) > 0:
                tickers_with_position.append(asset['ticker'])
        
        if not tickers_with_position:
            return {}
        
        # Buscar cotações do cache (banco de dados) - RÁPIDO
        quotes_result = {}
        tickers_to_refresh = []
        
        for ticker in tickers_with_position:
            cached_quote = get_quote(ticker)
            
            if cached_quote:
                quotes_result[ticker] = cached_quote
            else:
                # Sem cache, adicionar na lista para refresh
                tickers_to_refresh.append(ticker)
        
        # Se refresh=True ou existem tickers sem cache, atualizar em background
        if refresh or tickers_to_refresh:
            background_tasks.add_task(
                _update_quotes_background,
                tickers_with_position
            )
            logger.debug(f"🔄 Atualização em background agendada para {len(tickers_with_position)} tickers")
        
        return quotes_result
        
    except Exception as e:
        logger.error(f"Erro ao buscar cotações rápidas: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def _update_quotes_background(tickers: list):
    """
    Atualiza cotações em background.
    Executado de forma assíncrona após retornar resposta ao cliente.
    """
    logger.info(f"🔄 Iniciando atualização em background de {len(tickers)} cotações")
    
    try:
        market_service = get_market_data_service()
        updated_count = 0
        
        for ticker in tickers:
            try:
                # Buscar cotação do yfinance (com force_refresh)
                quote = market_service.get_quote(ticker, force_refresh=True)
                
                if quote and quote.get("price"):
                    # Salvar no banco
                    save_quote(ticker, quote)
                    updated_count += 1
                    logger.debug(f"✅ {ticker}: cotação atualizada")
                    
            except Exception as e:
                logger.error(f"❌ {ticker}: erro ao atualizar - {str(e)}")
                continue
        
        logger.info(f"✅ Atualização concluída: {updated_count}/{len(tickers)} cotações atualizadas")
        
    except Exception as e:
        logger.error(f"Erro na atualização em background: {str(e)}")
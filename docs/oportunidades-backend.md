# Oportunidades de Melhoria — Backend

Este documento descreve as principais oportunidades de melhoria identificadas no backend do Portfolio Manager v2.

---

## 🎯 Status Atual (2026-01-02)

**✅ Segurança Crítica:** Resolvida  
- CORS configurável ✓
- Validação de entrada ✓
- Tratamento de exceções específico ✓

**⚠️ Próximas Prioridades Críticas:**
1. **Context Manager para DB** — Evitar leaks de conexão em cenários de erro
2. **Logging Estruturado** — Auditoria e debugging de produção

**💡 Aplicação está funcional e segura para uso básico!**

---

## 🔴 Críticas (Segurança e Confiabilidade)

### 1. ✅ **CORS está aberto para qualquer origem** — RESOLVIDO
**Localização:** `backend/app/main.py`  
**Status:** ✅ Implementado em 2026-01-02

**Solução aplicada:**
```python
allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
```

✅ **Resultado:** CORS agora é configurável via variável de ambiente com valor padrão seguro.

---

### 2. ✅ **Tratamento de exceções genérico na importação** — RESOLVIDO
**Localização:** `backend/app/services/importer.py`  
**Status:** ✅ Implementado em 2026-01-02

**Solução aplicada:**
```python
except sqlite3.IntegrityError:
    # Violação de UNIQUE → duplicata identificada
    duplicated += 1
except Exception as e:
    # Erro inesperado: rollback e propaga
    conn.rollback()
    conn.close()
    raise ValueError(f"Erro ao processar linha {idx}: {str(e)}")
```

✅ **Resultado:** Duplicatas identificadas corretamente, erros reais propagados com contexto.

---

### 3. ✅ **Ausência de validação de entrada no endpoint `/operations`** — RESOLVIDO
**Localização:** `backend/app/main.py`  
**Status:** ✅ Implementado em 2026-01-02

**Solução aplicada:**
```python
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

@app.post("/operations")
def create_manual_operation(operation: OperationCreate):
    payload = operation.model_dump()
    payload["trade_date"] = payload["trade_date"].isoformat()
    payload["source"] = "MANUAL"
    create_operation(payload)
    return {"status": "success"}
```

✅ **Resultado:** Validação completa com tipos, formatos e valores numéricos.

---

### 4. **Vulnerabilidade de SQL Injection está mitigada, mas pode melhorar**
**Localização:** `backend/app/repositories/operations_repository.py`, `backend/app/services/importer.py`

**Status atual:** ✅ Usa placeholders (`?`), o que protege contra SQL injection.

**Melhoria sugerida:**  
Adotar uma camada de abstração como SQLAlchemy Core ou Tortoise ORM para reduzir erros manuais e melhorar testabilidade.

---

## 🟠 Importantes (Manutenibilidade e Qualidade)

### 5. **Falta de logging estruturado**
**Prioridade:** 🔴 Alta

**Problema:**  
Não há registros de operações críticas (importações, erros, criação manual de operações). Isso dificulta:
- Debugging em produção
- Auditoria de operações
- Monitoramento de performance
- Detecção de comportamentos anômalos

**Impacto:**
- Impossível rastrear quando/quem/o que foi importado
- Dificuldade para diagnosticar problemas reportados por usuários
- Falta de visibilidade sobre uso do sistema

**Solução:**  
Adicionar `logging` com níveis apropriados:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def import_b3_excel(file):
    logger.info(f"Iniciando importação de arquivo B3: {file.filename}")
    # ...
    logger.info(f"Importação concluída: {inserted} inseridas, {duplicated} duplicadas")
    
def create_manual_operation(operation):
    logger.info(f"Criando operação manual: {operation.ticker} - {operation.movement_type}")
    # ...
```

**Recomendação:** Implementar antes de uso em produção para auditoria.

---

### 6. **Conexões de banco não estão sendo gerenciadas adequadamente**
**Localização:** Múltiplos arquivos (`database.py`, `operations_repository.py`, `importer.py`)  
**Prioridade:** 🔴 Alta

**Problema:**  
Cada função abre e fecha uma conexão manualmente. Em caso de exceção, a conexão pode não ser fechada, causando leaks de recursos.

**Status atual:** ⚠️ Parcialmente mitigado no importer (item 2), mas ainda é um problema em `operations_repository.py`.

**Impacto:**
- Em produção, múltiplas requisições simultâneas podem esgotar conexões disponíveis
- Memória não liberada adequadamente
- Dificulta testes unitários (mocking complicado)

**Solução:**  
Usar context manager:

```python
from contextlib import contextmanager

@contextmanager
def get_db():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

# Uso:
with get_db() as conn:
    cursor = conn.cursor()
    cursor.execute(...)
```

**Recomendação:** Implementar antes de ir para produção ou com múltiplos usuários simultâneos.

---

### 7. **Falta de testes unitários e de integração**
**Localização:** `backend/tests/test_import.py`

**Problema:**  
Existe apenas um teste placeholder. Funcionalidades críticas como importação e deduplicação não têm cobertura.

**Solução:**  
Implementar testes com `pytest`:

```python
def test_import_b3_success(tmp_path):
    # Criar Excel de teste
    # Chamar import_b3_excel
    # Verificar inserção no banco
    pass

def test_import_b3_duplicate_ignored():
    # Importar mesmo arquivo duas vezes
    # Verificar que duplicatas foram ignoradas
    pass
```

---

### 8. **Falta de migrations para o banco de dados**
**Problema:**  
Mudanças no schema exigem drop manual da tabela ou recriação do banco.

**Solução:**  
Usar Alembic (se adotar SQLAlchemy) ou criar um sistema simples de versionamento de schema.

---

### 9. **Ausência de healthcheck detalhado**
**Localização:** `backend/app/main.py`

```python
@app.get("/health")
def health():
    return {"status": "ok"}
```

**Problema:**  
Não verifica se o banco de dados está acessível.

**Solução:**  

```python
@app.get("/health")
def health():
    try:
        conn = get_connection()
        conn.execute("SELECT 1")
        conn.close()
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database unhealthy: {e}")
```

---

### 10. **Campos não utilizados no schema**
**Localização:** `backend/app/db/database.py`

**Problema:**  
Campos `asset_class`, `asset_type`, `product_name` não são preenchidos pela importação B3, mas são obrigatórios (`NOT NULL`).

**Solução:**  
- Tornar esses campos opcionais (`TEXT NULL`)  
- OU preencher com valores padrão na importação B3  
- OU ajustar o importer para extrair esses dados do Excel (se existirem)

---

## 🟡 Boas Práticas (Nice to Have)

### 11. **Adicionar rate limiting**
**Objetivo:**  
Proteger contra abuso (ex: múltiplas importações simultâneas).

**Solução:**  
Usar `slowapi`:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/import/b3")
@limiter.limit("10/minute")
async def import_b3(request: Request, file: UploadFile = File(...)):
    ...
```

---

### 12. **Adicionar paginação no endpoint `/operations`**
**Problema:**  
Com milhares de operações, retornar todas de uma vez é ineficiente.

**Solução:**  

```python
@app.get("/operations")
def get_operations(skip: int = 0, limit: int = 100):
    return list_operations(skip=skip, limit=limit)
```

---

### 13. **Criar endpoint para estatísticas agregadas**
**Objetivo:**  
Evitar que o frontend precise processar todas as operações para calcular totais.

**Exemplo:**  
`GET /operations/summary` retorna:

```json
{
  "total_operations": 150,
  "total_invested": 50000.00,
  "unique_tickers": 12,
  "last_import_date": "2025-12-31"
}
```

---

### 14. **Dockerização melhorada**
**Problema atual:**  
O Dockerfile usa `CMD` que não suporta hot-reload em desenvolvimento.

**Solução:**  
Separar produção e desenvolvimento:

```dockerfile
# Usar --reload apenas em dev
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

Ou criar `docker-compose.override.yml`:

```yaml
services:
  api:
    command: uvicorn app.main:app --host 0.0.0.0 --reload
```

---

### 15. **Adicionar variáveis de ambiente para configuração**
**Objetivo:**  
Tornar a aplicação configurável sem modificar código.

**Exemplo:**  

```python
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_path: str = "/app/app/data/portfolio.db"
    cors_origins: str = "http://localhost:5173"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()
```

---

### 16. **Padronizar respostas de erro**
**Problema:**  
Erros retornam formatos inconsistentes.

**Solução:**  

```python
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"error": "validation_error", "message": str(exc)}
    )
```

---

### 17. **Adicionar tipos de retorno nos endpoints**
**Objetivo:**  
Melhorar documentação automática (OpenAPI).

**Exemplo:**  

```python
from pydantic import BaseModel

class ImportSummary(BaseModel):
    total_rows: int
    inserted: int
    duplicated: int
    unique_assets: int
    imported_at: str

@app.post("/import/b3", response_model=ImportSummary)
async def import_b3(file: UploadFile = File(...)):
    summary = import_b3_excel(file)
    return summary
```

---

## 📋 Checklist de Prioridades

**✅ Concluído (2026-01-02):**
- [x] Corrigir CORS (item 1) — ✅ Implementado
- [x] Adicionar validação Pydantic (item 3) — ✅ Implementado
- [x] Melhorar tratamento de exceções (item 2) — ✅ Implementado

**🔴 Crítico - Fazer primeiro:**
- [ ] Implementar context manager para DB (item 6) — **Alta prioridade**
- [ ] Adicionar logging estruturado (item 5) — **Alta prioridade**

**🟠 Importante - Fazer em seguida:**
- [ ] Criar testes unitários (item 7)
- [ ] Melhorar healthcheck (item 9)
- [ ] Ajustar schema para campos não usados (item 10)

**🟡 Nice to have:**
- [ ] Rate limiting (item 11)
- [ ] Paginação (item 12)
- [ ] Endpoint de estatísticas (item 13)
- [ ] Variáveis de ambiente (item 15)

---

## 📊 Resumo de Progresso

**Total de melhorias identificadas:** 17  
**Concluídas:** 3 críticas (segurança) ✅  
**Pendentes críticas/importantes:** 5  
**Pendentes nice-to-have:** 9  

**Próxima prioridade:** Context manager para gerenciamento de conexões DB (item 6)

---

**Última atualização:** 2026-01-02  
**Estimativa de esforço restante:** 2 sprints (assumindo 1 sprint = 2 semanas)

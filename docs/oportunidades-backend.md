# Oportunidades de Melhoria — Backend

Este documento descreve as principais oportunidades de melhoria identificadas no backend do Portfolio Manager v2.

---

## 🔴 Críticas (Segurança e Confiabilidade)

### 1. **CORS está aberto para qualquer origem**
**Localização:** `backend/app/main.py`

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ❌ Qualquer origem permitida
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Problema:**  
Qualquer site pode fazer requisições ao backend, expondo a aplicação a ataques CSRF e acesso não autorizado.

**Solução:**  
Configurar origens explícitas ou usar variável de ambiente:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
```

---

### 2. **Tratamento de exceções genérico na importação**
**Localização:** `backend/app/services/importer.py`

```python
except Exception:
    # Violação de UNIQUE → duplicata
    duplicated += 1
```

**Problema:**  
Captura qualquer exceção como duplicata, ocultando erros reais (tipo de dados incorretos, problemas de conexão, etc.).

**Solução:**  
Capturar especificamente `sqlite3.IntegrityError`:

```python
except sqlite3.IntegrityError:
    duplicated += 1
except Exception as e:
    conn.rollback()
    conn.close()
    raise ValueError(f"Erro ao processar linha: {e}")
```

---

### 3. **Ausência de validação de entrada no endpoint `/operations`**
**Localização:** `backend/app/main.py`

```python
@app.post("/operations")
def create_manual_operation(payload: dict):  # ❌ dict sem validação
```

**Problema:**  
Aceita qualquer estrutura JSON, permitindo dados inválidos ou maliciosos.

**Solução:**  
Criar um modelo Pydantic:

```python
from pydantic import BaseModel, Field
from datetime import date

class OperationCreate(BaseModel):
    asset_class: str = Field(min_length=1)
    asset_type: str = Field(min_length=1)
    product_name: str = Field(min_length=1)
    ticker: str | None = None
    movement_type: str = Field(pattern="^(COMPRA|VENDA)$")
    quantity: int = Field(gt=0)
    price: float = Field(gt=0)
    trade_date: date

@app.post("/operations")
def create_manual_operation(operation: OperationCreate):
    payload = operation.model_dump()
    payload["source"] = "MANUAL"
    create_operation(payload)
    return {"status": "success"}
```

---

### 4. **Vulnerabilidade de SQL Injection está mitigada, mas pode melhorar**
**Localização:** `backend/app/repositories/operations_repository.py`, `backend/app/services/importer.py`

**Status atual:** ✅ Usa placeholders (`?`), o que protege contra SQL injection.

**Melhoria sugerida:**  
Adotar uma camada de abstração como SQLAlchemy Core ou Tortoise ORM para reduzir erros manuais e melhorar testabilidade.

---

## 🟠 Importantes (Manutenibilidade e Qualidade)

### 5. **Falta de logging estruturado**
**Problema:**  
Não há registros de operações críticas (importações, erros, criação manual de operações).

**Solução:**  
Adicionar `logging` com níveis apropriados:

```python
import logging

logger = logging.getLogger(__name__)

def import_b3_excel(file):
    logger.info("Iniciando importação de arquivo B3")
    # ...
    logger.info(f"Importação concluída: {inserted} inseridas, {duplicated} duplicadas")
```

---

### 6. **Conexões de banco não estão sendo gerenciadas adequadamente**
**Localização:** Múltiplos arquivos (`database.py`, `operations_repository.py`, `importer.py`)

**Problema:**  
Cada função abre e fecha uma conexão manualmente. Em caso de exceção, a conexão pode não ser fechada.

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

**Fazer primeiro:**
- [ ] Corrigir CORS (item 1)
- [ ] Adicionar validação Pydantic (item 3)
- [ ] Melhorar tratamento de exceções (item 2)
- [ ] Implementar context manager para DB (item 6)
- [ ] Adicionar logging (item 5)

**Fazer em seguida:**
- [ ] Criar testes unitários (item 7)
- [ ] Melhorar healthcheck (item 9)
- [ ] Ajustar schema para campos não usados (item 10)

**Nice to have:**
- [ ] Rate limiting (item 11)
- [ ] Paginação (item 12)
- [ ] Endpoint de estatísticas (item 13)
- [ ] Variáveis de ambiente (item 15)

---

**Total de melhorias identificadas:** 17  
**Estimativa de esforço:** 2-3 sprints (assumindo 1 sprint = 2 semanas)

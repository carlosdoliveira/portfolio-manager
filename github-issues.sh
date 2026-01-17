#!/bin/bash
# Script para criar issues no GitHub
# Execute após instalar GitHub CLI: sudo apt install gh
# Autentique: gh auth login

echo "Criando issues no GitHub..."

# ========================================
# ISSUES CRÍTICAS - BACKEND
# ========================================

gh issue create \
  --title "[CRÍTICO][BACKEND] Configurar CORS com origens específicas" \
  --body "## 🔴 Problema
Atualmente o CORS está aberto para qualquer origem (\`allow_origins=[\"*\"]\`), expondo a aplicação a ataques CSRF e acesso não autorizado.

## 📍 Localização
\`backend/app/main.py\`

## ✅ Solução proposta
Configurar origens explícitas usando variáveis de ambiente:

\`\`\`python
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv(\"CORS_ORIGINS\", \"http://localhost:5173\").split(\",\"),
    allow_credentials=True,
    allow_methods=[\"GET\", \"POST\"],
    allow_headers=[\"Content-Type\"],
)
\`\`\`

## 📚 Referência
\`docs/oportunidades-backend.md\` (item 1)

## ⏱️ Estimativa
30 minutos" \
  --label "security,backend,critical,sprint-1"

gh issue create \
  --title "[CRÍTICO][BACKEND] Adicionar validação Pydantic no endpoint /operations" \
  --body "## 🔴 Problema
O endpoint \`POST /operations\` aceita \`dict\` sem validação, permitindo dados inválidos ou maliciosos.

## 📍 Localização
\`backend/app/main.py\`

## ✅ Solução proposta
Criar modelo Pydantic:

\`\`\`python
from pydantic import BaseModel, Field
from datetime import date

class OperationCreate(BaseModel):
    asset_class: str = Field(min_length=1)
    asset_type: str = Field(min_length=1)
    product_name: str = Field(min_length=1)
    ticker: str | None = None
    movement_type: str = Field(pattern=\"^(COMPRA|VENDA)$\")
    quantity: int = Field(gt=0)
    price: float = Field(gt=0)
    trade_date: date

@app.post(\"/operations\")
def create_manual_operation(operation: OperationCreate):
    payload = operation.model_dump()
    payload[\"source\"] = \"MANUAL\"
    create_operation(payload)
    return {\"status\": \"success\"}
\`\`\`

## 📚 Referência
\`docs/oportunidades-backend.md\` (item 3)

## ⏱️ Estimativa
1 hora" \
  --label "security,backend,critical,sprint-1"

gh issue create \
  --title "[CRÍTICO][BACKEND] Melhorar tratamento de exceções no importador" \
  --body "## 🔴 Problema
O importador captura qualquer exceção como duplicata, ocultando erros reais (tipo de dados incorretos, problemas de conexão, etc.).

## 📍 Localização
\`backend/app/services/importer.py\`

## ✅ Solução proposta
Capturar especificamente \`sqlite3.IntegrityError\`:

\`\`\`python
import sqlite3

except sqlite3.IntegrityError:
    duplicated += 1
except Exception as e:
    conn.rollback()
    conn.close()
    raise ValueError(f\"Erro ao processar linha: {e}\")
\`\`\`

## 📚 Referência
\`docs/oportunidades-backend.md\` (item 2)

## ⏱️ Estimativa
45 minutos" \
  --label "bug,backend,critical,sprint-1"

gh issue create \
  --title "[CRÍTICO][BACKEND] Ajustar schema do banco - campos obrigatórios não preenchidos" \
  --body "## 🔴 Problema
Campos \`asset_class\`, \`asset_type\`, \`product_name\` são NOT NULL mas não são preenchidos pela importação B3.

## 📍 Localização
\`backend/app/db/database.py\`

## ✅ Solução proposta
Opção 1: Tornar campos opcionais
\`\`\`sql
asset_class TEXT,
asset_type TEXT,
product_name TEXT,
\`\`\`

Opção 2: Preencher com valores padrão na importação

## 📚 Referência
\`docs/oportunidades-backend.md\` (item 10)

## ⏱️ Estimativa
30 minutos" \
  --label "database,backend,critical,sprint-1"

# ========================================
# ISSUES CRÍTICAS - FRONTEND
# ========================================

gh issue create \
  --title "[CRÍTICO][FRONTEND] Mover URL da API para variável de ambiente" \
  --body "## 🔴 Problema
URL da API está hardcoded (\`http://localhost:8000\`), não funciona em produção ou outros ambientes.

## 📍 Localização
\`frontend/src/api/client.ts\`

## ✅ Solução proposta
\`\`\`typescript
const API_URL = import.meta.env.VITE_API_URL || \"http://localhost:8000\";

export async function uploadB3File(file: File) {
  const formData = new FormData();
  formData.append(\"file\", file);

  const response = await fetch(\`\${API_URL}/import/b3\`, {
    method: \"POST\",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.message || \"Erro ao importar arquivo\");
  }

  return response.json();
}
\`\`\`

Criar \`.env.example\`:
\`\`\`
VITE_API_URL=http://localhost:8000
\`\`\`

## 📚 Referência
\`docs/oportunidades-frontend.md\` (item 1)

## ⏱️ Estimativa
15 minutos" \
  --label "config,frontend,critical,sprint-1"

gh issue create \
  --title "[CRÍTICO][FRONTEND] Implementar tratamento de erro detalhado" \
  --body "## 🔴 Problema
Erros são capturados genericamente sem detalhes, usuário não sabe o que causou o problema.

## 📍 Localização
\`frontend/src/components/ImportB3Card.tsx\`

## ✅ Solução proposta
\`\`\`typescript
const [errorMessage, setErrorMessage] = useState<string | null>(null);

try {
  const result = await uploadB3File(file);
  setSummary(result.summary);
  setState(\"success\");
} catch (error) {
  setState(\"error\");
  setErrorMessage(
    error instanceof Error 
      ? error.message 
      : \"Erro desconhecido ao importar arquivo\"
  );
}

// No JSX:
{state === \"error\" && (
  <div className=\"import-status error\">
    <strong>Erro ao importar:</strong> {errorMessage}
  </div>
)}
\`\`\`

## 📚 Referência
\`docs/oportunidades-frontend.md\` (item 2)

## ⏱️ Estimativa
1 hora" \
  --label "ux,frontend,critical,sprint-1"

gh issue create \
  --title "[CRÍTICO][FRONTEND] Implementar página Portfolio com lista de operações" \
  --body "## 🔴 Problema
Página Portfolio está vazia, usuário não consegue visualizar dados importados.

## 📍 Localização
\`frontend/src/pages/Portfolio.tsx\`

## ✅ Solução proposta
1. Criar função no \`client.ts\` para buscar operações
2. Implementar tabela com colunas: data, ticker, tipo, quantidade, preço, valor
3. Adicionar estado de loading e erro

## 📚 Referência
\`docs/oportunidades-frontend.md\` (item 3)

## ⏱️ Estimativa
3 horas" \
  --label "feature,frontend,critical,sprint-1"

gh issue create \
  --title "[CRÍTICO][FRONTEND] Adicionar validação de arquivo antes do upload" \
  --body "## 🔴 Problema
Aceita arquivos .csv mas o backend só processa .xlsx. Causa erro tarde demais.

## 📍 Localização
\`frontend/src/components/DragAndDropArea.tsx\`

## ✅ Solução proposta
\`\`\`typescript
function handleFiles(files: FileList | null) {
  if (!files || files.length === 0) return;
  
  const file = files[0];
  const validExtensions = ['.xlsx', '.xls'];
  const extension = file.name.toLowerCase().slice(file.name.lastIndexOf('.'));
  
  if (!validExtensions.includes(extension)) {
    alert('Formato inválido. Envie um arquivo .xlsx');
    return;
  }
  
  if (file.size > 10 * 1024 * 1024) { // 10MB
    alert('Arquivo muito grande. Limite: 10MB');
    return;
  }
  
  onFileSelected(file);
}
\`\`\`

## 📚 Referência
\`docs/oportunidades-frontend.md\` (item 8)

## ⏱️ Estimativa
30 minutos" \
  --label "validation,frontend,critical,sprint-1"

# ========================================
# ISSUES IMPORTANTES - BACKEND
# ========================================

gh issue create \
  --title "[IMPORTANTE][BACKEND] Implementar context manager para conexões de banco" \
  --body "## 🟠 Problema
Conexões são abertas e fechadas manualmente. Em caso de exceção, podem não ser fechadas.

## 📍 Localização
Múltiplos arquivos: \`database.py\`, \`operations_repository.py\`, \`importer.py\`

## ✅ Solução proposta
\`\`\`python
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
\`\`\`

## 📚 Referência
\`docs/oportunidades-backend.md\` (item 6)

## ⏱️ Estimativa
2 horas" \
  --label "enhancement,backend,sprint-2"

gh issue create \
  --title "[IMPORTANTE][BACKEND] Adicionar logging estruturado" \
  --body "## 🟠 Problema
Não há registros de operações críticas (importações, erros, criação manual).

## ✅ Solução proposta
\`\`\`python
import logging

logger = logging.getLogger(__name__)

def import_b3_excel(file):
    logger.info(\"Iniciando importação de arquivo B3\")
    # ...
    logger.info(f\"Importação concluída: {inserted} inseridas, {duplicated} duplicadas\")
\`\`\`

## 📚 Referência
\`docs/oportunidades-backend.md\` (item 5)

## ⏱️ Estimativa
1 hora" \
  --label "observability,backend,sprint-2"

gh issue create \
  --title "[IMPORTANTE][BACKEND] Criar testes unitários para importação" \
  --body "## 🟠 Problema
Apenas teste placeholder existe. Funcionalidades críticas não têm cobertura.

## ✅ Tarefas
- [ ] Teste de importação bem-sucedida
- [ ] Teste de deduplicação (importar mesmo arquivo 2x)
- [ ] Teste de validação de colunas
- [ ] Teste de erro em dados inválidos

## 📚 Referência
\`docs/oportunidades-backend.md\` (item 7)

## ⏱️ Estimativa
4 horas" \
  --label "testing,backend,sprint-2"

gh issue create \
  --title "[IMPORTANTE][BACKEND] Melhorar healthcheck - verificar banco de dados" \
  --body "## 🟠 Problema
Healthcheck atual não verifica se o banco está acessível.

## 📍 Localização
\`backend/app/main.py\`

## ✅ Solução proposta
\`\`\`python
@app.get(\"/health\")
def health():
    try:
        conn = get_connection()
        conn.execute(\"SELECT 1\")
        conn.close()
        return {\"status\": \"ok\", \"database\": \"connected\"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f\"Database unhealthy: {e}\")
\`\`\`

## 📚 Referência
\`docs/oportunidades-backend.md\` (item 9)

## ⏱️ Estimativa
30 minutos" \
  --label "enhancement,backend,sprint-2"

# ========================================
# ISSUES IMPORTANTES - FRONTEND
# ========================================

gh issue create \
  --title "[IMPORTANTE][FRONTEND] Implementar gerenciamento de estado global" \
  --body "## 🟠 Problema
Não há contexto ou store para compartilhar dados entre páginas.

## ✅ Solução proposta
Usar Zustand ou Context API para:
- Operações carregadas
- Estado de autenticação (futuro)
- Configurações de usuário

## 📚 Referência
\`docs/oportunidades-frontend.md\` (item 5)

## ⏱️ Estimativa
3 horas" \
  --label "architecture,frontend,sprint-2"

gh issue create \
  --title "[IMPORTANTE][FRONTEND] Adicionar tipagem e validação de respostas da API" \
  --body "## 🟠 Problema
TypeScript não valida formato das respostas do backend.

## ✅ Solução proposta
Usar Zod para criar schemas e validar:
\`\`\`typescript
import { z } from 'zod';

const ImportSummarySchema = z.object({
  total_rows: z.number(),
  inserted: z.number(),
  duplicated: z.number(),
  unique_assets: z.number(),
  imported_at: z.string(),
});

type ImportSummary = z.infer<typeof ImportSummarySchema>;
\`\`\`

## 📚 Referência
\`docs/oportunidades-frontend.md\` (item 6)

## ⏱️ Estimativa
2 horas" \
  --label "type-safety,frontend,sprint-2"

gh issue create \
  --title "[IMPORTANTE][FRONTEND] Tornar layout responsivo (mobile-first)" \
  --body "## 🟠 Problema
Sidebar ocupa espaço fixo, layout não funciona em mobile.

## ✅ Solução proposta
- Adicionar breakpoints CSS
- Implementar menu hamburguer para mobile
- Testar em viewports < 768px

## 📚 Referência
\`docs/oportunidades-frontend.md\` (item 11)

## ⏱️ Estimativa
4 horas" \
  --label "ux,frontend,sprint-2"

gh issue create \
  --title "[IMPORTANTE][FRONTEND] Criar componente de tabela reutilizável" \
  --body "## 🟠 Problema
Evitar duplicação ao listar operações em múltiplas páginas.

## ✅ Solução proposta
Criar componente genérico com TypeScript:
\`\`\`typescript
interface Column<T> {
  header: string;
  accessor: keyof T | ((row: T) => React.ReactNode);
}

interface TableProps<T> {
  data: T[];
  columns: Column<T>[];
}

export function Table<T>({ data, columns }: TableProps<T>) {
  // ...
}
\`\`\`

## 📚 Referência
\`docs/oportunidades-frontend.md\` (item 13)

## ⏱️ Estimativa
2 horas" \
  --label "component,frontend,sprint-2"

# ========================================
# ISSUES SPRINT 3
# ========================================

gh issue create \
  --title "[FEATURE][BACKEND] Adicionar paginação no endpoint /operations" \
  --body "## Objetivo
Com milhares de operações, retornar todas de uma vez é ineficiente.

## ✅ Solução proposta
\`\`\`python
@app.get(\"/operations\")
def get_operations(skip: int = 0, limit: int = 100):
    return list_operations(skip=skip, limit=limit)
\`\`\`

## 📚 Referência
\`docs/oportunidades-backend.md\` (item 12)

## ⏱️ Estimativa
2 horas" \
  --label "enhancement,backend,sprint-3"

gh issue create \
  --title "[FEATURE][BACKEND] Criar endpoint /operations/summary" \
  --body "## Objetivo
Evitar que o frontend processe todas operações para calcular totais.

## ✅ Retorno esperado
\`\`\`json
{
  \"total_operations\": 150,
  \"total_invested\": 50000.00,
  \"unique_tickers\": 12,
  \"last_import_date\": \"2025-12-31\"
}
\`\`\`

## 📚 Referência
\`docs/oportunidades-backend.md\` (item 13)

## ⏱️ Estimativa
3 horas" \
  --label "feature,backend,sprint-3"

gh issue create \
  --title "[FEATURE][FRONTEND] Implementar Dashboard com métricas" \
  --body "## Objetivo
Mostrar visão geral da carteira na página principal.

## ✅ Métricas a exibir
- Total investido
- Número de ativos únicos
- Total de operações
- Última importação

## 📚 Referência
\`docs/oportunidades-frontend.md\` (item 3)

## ⏱️ Estimativa
4 horas" \
  --label "feature,frontend,sprint-3"

gh issue create \
  --title "[FEATURE][FRONTEND] Implementar página Analysis com gráficos" \
  --body "## Objetivo
Visualizar distribuição de ativos e performance.

## ✅ Gráficos sugeridos
- Distribuição por ativo (pizza)
- Timeline de operações
- Evolução de posição (se houver vendas)

## 📚 Referência
\`docs/oportunidades-frontend.md\` (item 3)

## ⏱️ Estimativa
6 horas" \
  --label "feature,frontend,sprint-3"

gh issue create \
  --title "[ENHANCEMENT][FRONTEND] Adicionar React Query para cache" \
  --body "## Objetivo
Evitar requisições duplicadas e melhorar performance.

## ✅ Implementação
Usar @tanstack/react-query para:
- Cache de operações
- Invalidação automática após importação
- Loading e error states

## 📚 Referência
\`docs/oportunidades-frontend.md\` (item 12)

## ⏱️ Estimativa
3 horas" \
  --label "enhancement,frontend,sprint-3"

gh issue create \
  --title "[ENHANCEMENT][FRONTEND] Adicionar toast notifications" \
  --body "## Objetivo
Feedback visual não-intrusivo para ações.

## ✅ Implementação
Usar react-hot-toast:
\`\`\`typescript
toast.success(\`\${result.summary.inserted} operações importadas!\`);
toast.error('Erro ao importar arquivo');
\`\`\`

## 📚 Referência
\`docs/oportunidades-frontend.md\` (item 15)

## ⏱️ Estimativa
1 hora" \
  --label "enhancement,frontend,sprint-3"

echo "✅ Issues criadas com sucesso!"
echo ""
echo "Para visualizar: gh issue list"
echo "Para filtrar por sprint: gh issue list --label sprint-1"

# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

## [Unreleased]

### 📊 Consolidação de Mercados

#### Visualização e Documentação de Consolidação de Operações ([2026-01-02])
**Objetivo:** Tornar explícito que operações em diferentes mercados (à vista e fracionário) são consolidadas automaticamente.

**Solução:**
- **Backend:**
  - Documentação explícita na função `list_assets()` sobre consolidação
  - Comentários em SQL explicando que a query soma TODAS as operações independente do mercado
  
- **Frontend:**
  - Card de "Posição Atual" agora mostra nota: "Consolidada (todos os mercados)"
  - Nova seção "Resumo por Mercado" na página de detalhes do ativo
  - Exibe breakdown informativo quando há operações em múltiplos mercados
  - Cards mostrando: Comprado, Vendido e Operações por mercado
  - Nota explicativa: "A posição atual é consolidada automaticamente"
  
- **Documentação:**
  - Novo guia completo: `docs/guides/consolidacao-mercados.md`
  - Exemplos práticos de consolidação
  - Scripts SQL de demonstração: `docs/guides/exemplo-consolidacao.sql`
  - Atualização do README.md com referência ao novo guia

**Benefícios:**
- Transparência total sobre como o sistema agrega operações
- Usuário entende que 100 ações no mercado à vista + 5 no fracionário = 105 ações total
- Possibilidade de drill-down para ver operações individuais por mercado
- Mantém auditabilidade completa (operações originais preservadas)
- Interface educativa e profissional

**Impacto Técnico:**
- Sem mudanças na lógica de consolidação (já funcionava corretamente)
- Apenas melhorias de UI/UX e documentação
- Facilita compreensão para novos desenvolvedores

**Localização:** 
- Backend: `backend/app/repositories/assets_repository.py`
- Frontend: `frontend/src/pages/AssetDetail.tsx`, `frontend/src/pages/AssetDetail.css`
- Docs: `docs/guides/consolidacao-mercados.md`, `docs/guides/exemplo-consolidacao.sql`

---

### 🎨 Frontend

#### URL da API Configurável via Variável de Ambiente ([2026-01-02])
**Objetivo:** Permitir deploy em diferentes ambientes sem modificar código.

**Solução:**
- Migração de URL hardcoded para `import.meta.env.VITE_API_URL`
- Valor padrão: `http://localhost:8000` (desenvolvimento)
- Criação de `frontend/.env` e `frontend/.env.example`
- Função auxiliar `fetchOperations()` adicionada

**Benefícios:**
- Funciona em desenvolvimento, staging e produção
- Configuração simples via arquivo `.env`
- Segue padrão Vite de variáveis de ambiente
- Facilita CI/CD e deploys

**Localização:** `frontend/src/api/client.ts`, `frontend/.env`, `frontend/.env.example`

#### Tratamento de Erro Detalhado na Importação ([2026-01-02])
**Objetivo:** Fornecer feedback claro quando importação falha.

**Solução:**
- Estado `errorMessage` para capturar mensagem específica do backend
- Extração de `error.detail` da resposta HTTP
- Componente visual destacado com:
  - Mensagem de erro detalhada
  - Botão "Tentar novamente" para recuperação
  - Estilo com background vermelho claro e borda
- Tratamento específico de `Error` instances

**Exemplos de feedback:**
- "Colunas obrigatórias ausentes: ['Data do Negócio']"
- "Erro ao processar linha 5: Invalid date format"
- "Erro desconhecido" (fallback)

**Benefícios:**
- Usuário sabe exatamente o que deu errado
- Reduz frustração e tentativas às cegas
- Facilita debug e suporte
- UX profissional

**Localização:** `frontend/src/components/ImportB3Card.tsx`, `frontend/src/styles/import.css`

### �🏗️ Infraestrutura e Qualidade

#### Context Manager para Gerenciamento de Conexões DB ([2026-01-02])
**Objetivo:** Eliminar leaks de recursos e garantir transações seguras.

**Solução:**
- Context manager `get_db()` em `database.py`
- Garante commit automático em sucesso
- Rollback automático em caso de erro
- Fechamento de conexão sempre garantido (finally)
- Atualizado `operations_repository.py` para usar context manager
- Atualizado `importer.py` para usar context manager

**Benefícios:**
- Zero leaks de conexão mesmo com exceções
- Transações ACID garantidas
- Código mais limpo e idiomático
- Facilita testes unitários futuros
- Suporta múltiplos usuários simultâneos

**Localização:** `backend/app/db/database.py`, `backend/app/repositories/operations_repository.py`, `backend/app/services/importer.py`

#### Logging Estruturado ([2026-01-02])
**Objetivo:** Auditoria completa e debugging facilitado em produção.

**Solução:**
- Configuração centralizada em `main.py` com formato padronizado
- Timestamp em todos os logs
- Níveis apropriados (INFO, DEBUG, ERROR)
- Logs em pontos críticos:
  - 🚀 Startup da aplicação
  - 🗄️ Inicialização do banco de dados
  - 📥 Importação B3 (início, validação, duplicatas, conclusão, erros)
  - ✏️ Criação de operações manuais
  - 📋 Listagem de operações
  - ❌ Erros detalhados em todos os fluxos

**Benefícios:**
- Rastreabilidade completa de operações
- Debugging facilitado em produção
- Auditoria de importações e modificações
- Visibilidade do uso do sistema
- Identificação rápida de problemas

**Localização:** `backend/app/main.py`, `backend/app/db/database.py`, `backend/app/repositories/operations_repository.py`, `backend/app/services/importer.py`

### ✨ Funcionalidades

#### CLI de Gerenciamento ([2026-01-02])
**Objetivo:** Facilitar o gerenciamento de todo o ciclo de vida da aplicação.

**Solução:**
- Script bash `portfolio` na raiz do projeto
- Comandos disponíveis:
  - `start` - Inicia todos os serviços com build automático
  - `stop` - Para todos os serviços de forma limpa
  - `restart` - Reinicia todos os serviços
  - `status` - Mostra status atual dos containers
  - `logs [serviço]` - Exibe logs em tempo real (api, frontend ou ambos)
  - `clean` - Remove containers, imagens e volumes Docker
  - `clean-all` - Remoção completa incluindo banco de dados
  - `help` - Documentação completa dos comandos

**Benefícios:**
- Interface amigável com cores e emojis
- Validações de segurança (confirmações para operações destrutivas)
- Mensagens claras de sucesso/erro
- Verificação automática de dependências (Docker, docker-compose)
- Links diretos para serviços após inicialização

**Localização:** `portfolio` (raiz do projeto)

### 🔒 Segurança

#### CORS Configurável ([2026-01-02])
**Problema:** CORS estava configurado com `allow_origins=["*"]`, permitindo que qualquer site fizesse requisições ao backend.

**Solução:** 
- Configuração de origens específicas via variável de ambiente `CORS_ORIGINS`
- Valor padrão: `http://localhost:5173` (desenvolvimento)
- Suporte a múltiplas origens separadas por vírgula
- Restrição de métodos HTTP para apenas `GET` e `POST`
- Restrição de headers para apenas `Content-Type`

**Localização:** `backend/app/main.py`

#### Validação de Entrada com Pydantic ([2026-01-02])
**Problema:** Endpoint `/operations` aceitava qualquer estrutura JSON (`dict`), permitindo dados inválidos ou maliciosos.

**Solução:**
- Criação do modelo `OperationCreate` com validação Pydantic
- Validação de tipos de dados obrigatórios
- Validação de formato: `movement_type` deve ser "COMPRA" ou "VENDA"
- Validação de valores: `quantity` e `price` devem ser maiores que zero
- Validação de comprimento mínimo para strings obrigatórias
- Conversão automática de `date` para string ISO no formato esperado pelo banco

**Localização:** `backend/app/main.py`

#### Tratamento Específico de Exceções ([2026-01-02])
**Problema:** Importador capturava qualquer exceção como duplicata (`except Exception`), ocultando erros reais como problemas de tipo de dados ou conexão.

**Solução:**
- Captura específica de `sqlite3.IntegrityError` para identificar duplicatas
- Tratamento explícito de erros inesperados com:
  - Rollback da transação
  - Fechamento adequado da conexão
  - Propagação de mensagem de erro detalhada com número da linha
- Preservação da rastreabilidade de erros

**Localização:** `backend/app/services/importer.py`

### 📚 Documentação

#### Atualização do README ([2026-01-02])
- Adicionada seção "Segurança e Validação" documentando as medidas implementadas
- Adicionada seção "Variáveis de Ambiente" com exemplos de configuração
- Documentação de como configurar CORS para produção
- Exemplos de uso com `.env` e docker-compose

### 🧪 Qualidade

#### Melhoria na Rastreabilidade de Erros
- Mensagens de erro agora incluem número da linha do arquivo Excel quando há falha na importação
- Logs mais informativos para debugging

## Próximas Melhorias Planejadas

### Prioridade Alta
- [ ] Implementar context manager para gerenciamento de conexões de banco de dados
- [ ] Adicionar logging estruturado
- [ ] Criar testes unitários e de integração
- [ ] Melhorar healthcheck para verificar conectividade do banco

### Prioridade Média
- [ ] Implementar sistema de migrations para o banco de dados
- [ ] Adicionar paginação no endpoint `/operations`
- [ ] Criar endpoint para estatísticas agregadas
- [ ] Ajustar schema para tornar campos não utilizados opcionais

### Prioridade Baixa (Nice to Have)
- [ ] Implementar rate limiting
- [ ] Separar configuração de desenvolvimento e produção no Docker
- [ ] Padronizar respostas de erro
- [ ] Adicionar tipos de retorno nos endpoints para melhor documentação OpenAPI

---

## Referências

Para mais detalhes sobre as oportunidades de melhoria identificadas, consulte:
- [Oportunidades Backend](docs/oportunidades-backend.md)
- [Oportunidades Frontend](docs/oportunidades-frontend.md)

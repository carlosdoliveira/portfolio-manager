# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

## [Unreleased]

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

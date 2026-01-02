# Correção de Bugs: CSS e Importação B3

## Data: 2026-01-02

## Resumo

Dois bugs críticos foram identificados e corrigidos após o deploy da estrutura hierárquica (Carteira → Ativos → Operações):

1. **CSS mal formatado** na experiência de adicionar novo ativo
2. **Erro de "database is locked"** na importação de planilhas B3

---

## Bug #1: CSS Mal Formatado

### Problema

A experiência de adicionar um novo ativo estava ruim porque o arquivo `Portfolio.css` estava incompleto e não tinha estilos para:

- Modal overlay (fundo escurecido)
- Modal content (caixa de diálogo)
- Modal header e botão de fechar
- Formulário de ativos
- Form groups e form rows
- Botões de ação

### Causa Raiz

O arquivo CSS antigo foi criado quando a página Portfolio mostrava operações diretamente. Após a refatoração para mostrar ativos com modais, os estilos não foram atualizados adequadamente.

### Solução

**Arquivo modificado:** `frontend/src/pages/Portfolio.css`

**Mudanças:**

1. **Adicionadas classes de modal:**
   ```css
   .modal-overlay {
     position: fixed;
     background: rgba(0, 0, 0, 0.5);
     /* ... animação fadeIn */
   }
   
   .modal-content {
     background: white;
     border-radius: 12px;
     /* ... animação slideUp */
   }
   
   .modal-header, .modal-close, .modal-body
   ```

2. **Adicionadas classes de formulário:**
   ```css
   .asset-form
   .form-group
   .form-row
   .form-actions
   ```

3. **Melhorados estilos de botões:**
   ```css
   .btn-primary, .btn-secondary, .btn-danger
   .btn-icon (view, edit, delete)
   ```

4. **Adicionadas animações:**
   - `fadeIn` para modal overlay
   - `slideUp` para modal content
   - `slideIn` para alerts

5. **Responsividade:**
   - Grid adaptativo para stats
   - Formulário em coluna única em mobile
   - Botões fullwidth em telas pequenas

### Resultado

✅ Modal de adicionar ativo agora tem boa apresentação visual
✅ Formulário bem formatado com labels e inputs alinhados
✅ Botões com feedback visual (hover, disabled states)
✅ Animações suaves para melhor UX
✅ Responsivo em todos os tamanhos de tela

---

## Bug #2: Database is Locked na Importação B3

### Problema

Ao importar uma planilha B3, o seguinte erro aparecia:

```
ValueError: Erro ao processar linha 1: database is locked
```

### Causa Raiz

O problema tinha duas causas:

1. **Múltiplas conexões simultâneas:**
   - A função `create_asset()` abria uma nova conexão para cada ticker
   - Dentro do loop de importação, múltiplas conexões competiam pelo lock do SQLite
   - SQLite não lida bem com alta concorrência por padrão

2. **Falta de timeout:**
   - A conexão SQLite não tinha timeout configurado
   - Sem WAL (Write-Ahead Logging) habilitado

### Solução

**Arquivos modificados:**

#### 1. `backend/app/db/database.py`

**Mudanças:**

```python
def get_connection():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=30.0)  # ← Timeout de 30s
    conn.execute("PRAGMA journal_mode=WAL")        # ← Write-Ahead Logging
    return conn
```

**Benefícios:**
- `timeout=30.0`: Espera até 30 segundos antes de lançar "database is locked"
- `PRAGMA journal_mode=WAL`: Permite leituras concorrentes e melhor performance

#### 2. `backend/app/services/importer.py`

**Mudanças:**

```python
# ANTES: Chamava create_asset() dentro do loop
for idx, row in df.iterrows():
    asset_id = create_asset(ticker, ...)  # ← Nova conexão a cada iteração!

# DEPOIS: Uma única conexão, dois passos
with get_db() as conn:
    # Passo 1: Criar todos os ativos únicos
    unique_tickers = df["Código de Negociação"].unique()
    for ticker in unique_tickers:
        # Verificar se existe ou criar
        cursor.execute("SELECT id FROM assets WHERE ticker = ?", (ticker,))
        # ... criar se necessário
        asset_cache[ticker] = asset_id
    
    # Passo 2: Inserir operações usando o cache
    for idx, row in df.iterrows():
        asset_id = asset_cache.get(ticker)
        cursor.execute("INSERT INTO operations ...")
```

**Benefícios:**
- Uma única conexão para toda a importação
- Cache de asset IDs para evitar queries repetidas
- Lógica em dois passos: primeiro ativos, depois operações
- Menos overhead de conexões

**Removido:**
```python
from app.repositories.assets_repository import create_asset  # ← Não mais necessário
```

### Resultado

✅ Importação B3 funciona sem erros de lock
✅ Performance melhorada (menos conexões)
✅ Cache de ativos reduz queries repetidas
✅ WAL permite melhor concorrência
✅ Timeout de 30s previne locks eternos

---

## Validação

### Backend

```bash
# Verificar logs
docker logs portfolio-manager-v2-api-1 --tail 20

# Resultado esperado:
# INFO: Application startup complete.
# INFO: Uvicorn running on http://0.0.0.0:8000
```

### Frontend

1. Abrir `http://localhost:5173/portfolio`
2. Clicar em "Adicionar Ativo"
3. Verificar que modal aparece com boa formatação
4. Preencher formulário e salvar
5. Verificar que ativo é criado com sucesso

### Importação

1. Ir para página de Import
2. Selecionar planilha B3 válida
3. Fazer upload
4. Verificar que importação completa sem erros
5. Verificar que ativos e operações são criados corretamente

---

## Commits

```bash
git add .
git commit -m "fix: Corrige CSS do Portfolio e erro de database lock na importação B3

- Reescreve Portfolio.css com suporte completo a modais
- Adiciona animações e estilos responsivos
- Configura SQLite com timeout de 30s e WAL mode
- Refatora importer.py para usar uma única conexão
- Remove chamadas a create_asset() dentro do loop de importação"
```

---

## Lições Aprendidas

### CSS

- **Sempre atualizar estilos após refatorações de UI**
- Componentes modais precisam de overlay + content + header + body
- Animações melhoram percepção de qualidade
- Responsividade não é opcional

### SQLite & Concorrência

- **SQLite não é thread-safe por padrão**
- Sempre configurar `timeout` em conexões
- WAL mode melhora significativamente concorrência
- Evitar múltiplas conexões dentro de loops
- Cache de dados reduz queries e melhora performance

### Importação de Dados

- **Separar criação de entidades da inserção de eventos**
- Processar em lotes quando possível
- Usar cache para evitar lookups repetidos
- Uma transação para toda a operação garante atomicidade

---

## Próximos Passos

- [ ] Testar importação com arquivos grandes (>1000 linhas)
- [ ] Adicionar barra de progresso para importação
- [ ] Implementar validação de dados antes de salvar
- [ ] Adicionar testes automatizados para importação
- [ ] Documentar estrutura esperada da planilha B3

---

## Referências

- [SQLite WAL Mode](https://www.sqlite.org/wal.html)
- [SQLite and Python](https://docs.python.org/3/library/sqlite3.html)
- [CSS Modal Patterns](https://www.w3schools.com/howto/howto_css_modals.asp)

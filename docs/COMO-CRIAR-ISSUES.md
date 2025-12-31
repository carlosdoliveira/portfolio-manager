# Como Criar as Issues no GitHub

Este guia explica como executar o script que cria automaticamente todas as issues de melhoria no GitHub.

---

## Pré-requisitos

### 1. Instalar GitHub CLI

**Ubuntu/Debian:**
```bash
sudo apt install gh
```

**OU via snap:**
```bash
sudo snap install gh
```

**Verificar instalação:**
```bash
gh --version
```

---

### 2. Autenticar no GitHub

```bash
gh auth login
```

Siga os passos:
1. Escolha `GitHub.com`
2. Escolha `HTTPS`
3. Autentique via browser ou token
4. Confirme com `Y`

---

## Executar o Script

### Opção 1: Executar todas as issues de uma vez

```bash
cd docs
./github-issues.sh
```

Isso criará **21 issues** automaticamente:
- 8 críticas (Sprint 1)
- 8 importantes (Sprint 2)
- 6 features (Sprint 3)

---

### Opção 2: Criar issues manualmente (seletivo)

Se preferir criar apenas algumas issues, copie e execute comandos específicos do script:

**Exemplo - apenas issues críticas do backend:**

```bash
gh issue create \
  --title "[CRÍTICO][BACKEND] Configurar CORS com origens específicas" \
  --body "..." \
  --label "security,backend,critical,sprint-1"
```

---

## Verificar Issues Criadas

### Listar todas as issues
```bash
gh issue list
```

### Filtrar por label
```bash
gh issue list --label sprint-1
gh issue list --label critical
gh issue list --label backend
```

### Ver detalhes de uma issue
```bash
gh issue view 1
```

---

## Organizar Issues por Sprint

### Sprint 1 (Críticas)
```bash
gh issue list --label sprint-1
```

### Sprint 2 (Importantes)
```bash
gh issue list --label sprint-2
```

### Sprint 3 (Features)
```bash
gh issue list --label sprint-3
```

---

## Gerenciar Issues via CLI

### Atribuir issue a você
```bash
gh issue edit 1 --add-assignee @me
```

### Adicionar a um milestone
```bash
gh issue edit 1 --milestone "Sprint 1"
```

### Fechar issue
```bash
gh issue close 1 --comment "Implementado em #PR"
```

### Reabrir issue
```bash
gh issue reopen 1
```

---

## Labels Utilizadas

| Label | Significado |
|-------|-------------|
| `critical` | 🔴 Prioridade crítica |
| `sprint-1` | Sprint 1 - Segurança e Estabilidade |
| `sprint-2` | Sprint 2 - Qualidade |
| `sprint-3` | Sprint 3 - Features |
| `backend` | Issue relacionada ao backend |
| `frontend` | Issue relacionada ao frontend |
| `security` | Questão de segurança |
| `bug` | Comportamento incorreto |
| `enhancement` | Melhoria de funcionalidade existente |
| `feature` | Nova funcionalidade |
| `testing` | Relacionado a testes |
| `documentation` | Documentação |

---

## Criar Project Board (Opcional)

Para organizar visualmente as issues:

```bash
# Via web
# Acesse: https://github.com/carlosdoliveira/portfolio-manager/projects
# Clique em "New project" > "Board"
# Adicione as issues criadas
```

---

## Troubleshooting

### Erro: "command not found: gh"
**Solução:** Instale GitHub CLI (ver pré-requisitos)

### Erro: "authentication required"
**Solução:** Execute `gh auth login`

### Erro: "Resource not accessible by integration"
**Solução:** Verifique permissões do token em Settings > Developer settings > Personal access tokens

### Erro: "label not found"
**Solução:** As labels serão criadas automaticamente ao executar o script

---

## Alternativa: Criar Issues via Interface Web

Se preferir não usar CLI, você pode:

1. Acessar: https://github.com/carlosdoliveira/portfolio-manager/issues
2. Clicar em "New issue"
3. Copiar título e descrição do arquivo `github-issues.sh`
4. Adicionar labels manualmente

---

## Próximos Passos

Após criar as issues:

1. ✅ Revisar e ajustar prioridades se necessário
2. ✅ Atribuir issues aos membros do time
3. ✅ Criar milestones para cada sprint
4. ✅ Começar pela Sprint 1 (issues críticas)
5. ✅ Atualizar status conforme progresso

---

**Última atualização:** 31/12/2025

# Sugestão de Commit Message

## Título
```
feat: adiciona visualização e documentação de consolidação de mercados
```

## Descrição Completa
```
feat: adiciona visualização e documentação de consolidação de mercados

Implementa melhorias de UX e documentação para tornar explícito que
operações em diferentes mercados (à vista e fracionário) são
consolidadas automaticamente em uma única posição por ativo.

Backend:
- Adiciona documentação explícita em assets_repository.py
- Documenta que consolidação ignora o campo 'market'
- Mantém lógica existente (sem breaking changes)

Frontend:
- Adiciona nota "Consolidada (todos os mercados)" no card de posição
- Implementa seção "Resumo por Mercado" na página de detalhes
- Mostra breakdown informativo por mercado (à vista, fracionário)
- Adiciona estilos CSS para nova seção
- Exibe apenas quando há operações em múltiplos mercados

Documentação:
- Cria guia completo: docs/guides/consolidacao-mercados.md
- Adiciona exemplos práticos de cálculo
- Inclui scripts SQL de demonstração
- Adiciona diagrama visual do fluxo completo
- Atualiza README.md e CHANGELOG.md

Testes:
- Adiciona teste automatizado: tests/test_consolidacao_mercados.py
- Valida criação de operações em múltiplos mercados
- Confirma consolidação correta (100 + 5 = 105 ações)
- Verifica preservação das operações originais
- Teste passa com sucesso ✅

Benefícios:
- Transparência total sobre agregação de operações
- Usuário entende como posição é calculada
- Mantém auditabilidade completa
- Facilita onboarding de novos desenvolvedores
- Segue princípios event-based do projeto

Arquivos modificados:
- backend/app/repositories/assets_repository.py
- frontend/src/pages/AssetDetail.tsx
- frontend/src/pages/AssetDetail.css
- docs/guides/consolidacao-mercados.md (novo)
- docs/guides/exemplo-consolidacao.sql (novo)
- docs/guides/fluxo-consolidacao-visual.md (novo)
- docs/IMPLEMENTACAO-CONSOLIDACAO.md (novo)
- docs/README.md
- CHANGELOG.md
- tests/test_consolidacao_mercados.py (novo)
- tests/test-consolidacao-mercados.sh (novo)

Validação:
- ✅ Sem erros de compilação
- ✅ Containers Docker rodando
- ✅ Teste automatizado passando
- ✅ Frontend renderizando corretamente
- ✅ Documentação completa
```

## Comandos Git Sugeridos

```bash
# Adicionar arquivos
git add backend/app/repositories/assets_repository.py
git add frontend/src/pages/AssetDetail.tsx
git add frontend/src/pages/AssetDetail.css
git add docs/
git add tests/
git add CHANGELOG.md

# Commit
git commit -m "feat: adiciona visualização e documentação de consolidação de mercados

Implementa melhorias de UX e documentação para tornar explícito que
operações em diferentes mercados (à vista e fracionário) são
consolidadas automaticamente em uma única posição por ativo.

- Backend: Adiciona documentação explícita sobre consolidação
- Frontend: Nova seção 'Resumo por Mercado' na página de detalhes
- Documentação: Guia completo com exemplos e diagramas
- Testes: Script automatizado validando consolidação (✅ passando)

Benefícios: Transparência, auditabilidade e melhor UX

Refs: #consolidacao-mercados"

# Push (opcional)
# git push origin main
```

## Alternativa: Commit Curto

Se preferir um commit mais conciso:

```bash
git commit -m "feat: adiciona visualização de consolidação de mercados

- Nova seção 'Resumo por Mercado' no frontend
- Documentação completa em docs/guides/
- Teste automatizado validando consolidação
- Nota explicativa nos cards de posição"
```

## Branch Strategy (Opcional)

Se estiver seguindo GitFlow:

```bash
# Criar branch feature
git checkout -b feature/consolidacao-mercados-visualization

# ... fazer commit(s) ...

# Criar PR para main/develop
# Título: feat: Visualização e Documentação de Consolidação de Mercados
# Descrição: [usar descrição completa acima]
```

# Quickstart: Limpeza da Documentação

**Feature**: 002-docs-limpeza-atualizada  
**Date**: 2026-02-28

## Objetivo

Executar limpeza do diretório `docs/` mantendo somente conteúdo vigente no fluxo principal, preservando histórico relevante em `docs/archive/`.

## Passo a Passo

### 1) Criar inventário

- Mapear todos os arquivos de `docs/`.
- Classificar cada arquivo como `vigente`, `histórico`, `obsoleto` ou `duplicado`.
- Registrar justificativa por decisão.

### 2) Definir canônico por domínio

Para cada domínio abaixo, escolher exatamente um documento principal:
- Arquitetura
- API
- Setup/Desenvolvimento
- Status/Roadmap
- Guias operacionais

### 3) Aplicar ações

- `vigente`: manter e atualizar conteúdo quando necessário.
- `histórico`: mover para `docs/archive/` com contexto de data/escopo.
- `obsoleto`/`duplicado`: remover ou converter em nota de migração curta.

### 4) Atualizar navegação

- Revisar `README.md`, `docs/INDEX.md` e `mkdocs.yml`.
- Garantir que entradas principais apontam para documentos vigentes.

### 5) Validar consistência

- Verificar links internos críticos.
- Confirmar ausência de documento canônico duplicado por tema.
- Revisar padronização de linguagem (PT-BR).

## Checklist de Conclusão

- [ ] Inventário final com 100% dos arquivos classificados
- [ ] Índice principal sem links quebrados
- [ ] Documentação ativa sem duplicidade por tema
- [ ] Histórico preservado somente no arquivo
- [ ] Regra de governança documentada para novas PRs

## Critério de Pronto

A feature é considerada pronta quando o usuário consegue encontrar os documentos principais (API, arquitetura, setup, status) em menos de 60 segundos a partir do `docs/INDEX.md`, sem encontrar conteúdos conflitantes.

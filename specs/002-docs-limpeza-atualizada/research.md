# Research: Limpeza da Documentação com Foco em Conteúdo Vigente

**Feature**: 002-docs-limpeza-atualizada  
**Date**: 2026-02-28  
**Status**: Complete

## Research Tasks Completed

### 1. Estratégia de Classificação de Documentos

**Decision**: Adotar taxonomia de quatro estados: `vigente`, `histórico`, `obsoleto`, `duplicado`.

**Rationale**:
- Cria decisão objetiva para cada arquivo.
- Evita remoções indevidas de material relevante para rastreabilidade.
- Permite separar claramente documentação operacional de memória histórica.

**Alternatives considered**:
- ❌ Apenas `ativo/inativo`: insuficiente para distinguir histórico de obsolescência.
- ❌ Não classificar formalmente: mantém ambiguidade e reduz auditabilidade.
- ✅ Quatro estados explícitos: mais claro e acionável.

---

### 2. Estratégia de Limpeza Sem Perda de Contexto

**Decision**: Preservar histórico relevante em `docs/archive/` e remover apenas obsoleto sem valor de referência.

**Rationale**:
- Mantém trilha de decisões do projeto.
- Reduz ruído na navegação principal.
- Evita retrabalho em análises futuras.

**Alternatives considered**:
- ❌ Remoção agressiva de tudo que não for atual: risco alto de perda de contexto.
- ❌ Manter tudo no diretório principal: baixa usabilidade.
- ✅ Arquivar seletivamente + limpar diretório ativo: melhor equilíbrio.

---

### 3. Fonte Canônica por Domínio

**Decision**: Definir um documento principal por domínio (arquitetura, API, setup, status).

**Rationale**:
- Elimina conflito entre múltiplas versões de um mesmo tema.
- Simplifica manutenção contínua.
- Facilita onboarding de contribuidores.

**Alternatives considered**:
- ❌ Múltiplos documentos equivalentes por tema: gera inconsistência.
- ✅ Um canônico por tema + notas de migração: previsível e sustentável.

---

### 4. Validação de Navegação e Links

**Decision**: Validar links dos pontos de entrada (`README.md`, `docs/INDEX.md`, `mkdocs.yml`) após cada mudança.

**Rationale**:
- Minimiza risco de documentação “quebrada” após remoções/movimentações.
- Garante experiência consistente para usuário e time técnico.

**Alternatives considered**:
- ❌ Conferência visual parcial: propensa a erro.
- ✅ Checklist de validação de links críticos: simples e suficiente para o escopo.

---

### 5. Governança para Evitar Regressão

**Decision**: Inserir política de revisão periódica e checklist de PR para documentação.

**Rationale**:
- Evita retorno do acúmulo de documentos obsoletos.
- Transforma limpeza pontual em rotina de manutenção.

**Alternatives considered**:
- ❌ Limpeza única sem política: problema retorna em poucos ciclos.
- ✅ Regra simples em PR + revisão trimestral: baixo custo operacional.

## Technology/Process Decisions Summary

| Aspecto | Decisão | Justificativa |
|---|---|---|
| Classificação | 4 estados | Clareza e ação objetiva |
| Retenção histórica | Arquivar em `docs/archive/` | Preserva rastreabilidade |
| Canonicidade | 1 doc por domínio | Evita conflito e duplicidade |
| Navegação | Validar links críticos | Evita referência quebrada |
| Sustentação | Governança em PR + revisão periódica | Previne regressão |

## Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Remoção de conteúdo ainda útil | Alto | Revisão por critérios e marcação prévia |
| Quebra de links em índices | Alto | Validação de links críticos antes de merge |
| Divergência entre docs canônicas | Médio | Definição explícita de “owner” por domínio |
| Reintrodução de duplicatas | Médio | Checklist obrigatório em PR |

## Dependencies & Prerequisites

- Mapeamento da estrutura atual em `docs/`.
- Revisão manual dos pontos de entrada de documentação.
- Atualização do índice principal e das referências cruzadas.

**Status**: ✅ Research Complete - Ready for Phase 1

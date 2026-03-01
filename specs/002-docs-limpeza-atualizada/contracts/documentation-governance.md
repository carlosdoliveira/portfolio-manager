# Contract: Governança de Documentação Vigente

**Feature**: 002-docs-limpeza-atualizada  
**Date**: 2026-02-28  
**Type**: Processo interno / contrato editorial

## 1. Escopo do Contrato

Este contrato define como a documentação ativa do projeto é mantida sem conteúdo obsoleto no fluxo principal de navegação.

## 2. Entradas Obrigatórias

- Lista de arquivos existentes em `docs/`.
- Índices e pontos de entrada (`README.md`, `docs/INDEX.md`, `mkdocs.yml`).
- Critérios de classificação: `vigente`, `histórico`, `obsoleto`, `duplicado`.

## 3. Saídas Obrigatórias

- Inventário classificado por arquivo com justificativa.
- Mapa de documentos canônicos por tema.
- Índices atualizados sem links quebrados.
- Registro de governança para PRs futuras.

## 4. Regras Normativas

1. Cada tema de documentação deve possuir somente um documento canônico.
2. Conteúdo histórico não deve permanecer no fluxo principal de navegação.
3. Arquivos removidos ou movidos devem ter links e referências atualizados no mesmo ciclo.
4. Toda alteração relevante de código deve refletir atualização do documento canônico correspondente.
5. Linguagem dos documentos ativos deve ser português (Brasil).

## 5. Critérios de Aceitação

- 100% dos documentos de `docs/` classificados.
- 0 links quebrados nos pontos de entrada.
- Redução objetiva de redundância documental no diretório ativo.
- Existência de política de revisão periódica e checklist para PR.

## 6. Não Objetivos

- Reescrever completamente todo o acervo histórico.
- Alterar arquitetura técnica do produto.
- Introduzir nova ferramenta complexa de docs sem necessidade.

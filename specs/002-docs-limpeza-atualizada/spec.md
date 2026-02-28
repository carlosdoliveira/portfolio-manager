# Feature Specification: Limpeza da Documentação com Foco em Conteúdo Vigente

**Feature Branch**: `002-docs-limpeza-atualizada`  
**Created**: 2026-02-28  
**Status**: Draft  
**Input**: User description: "gostaria de fazer uma limpeza na documentação do projeto e garantir que tão somente o que é atualizado esteja presente."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Inventário e Classificação da Documentação (Priority: P1)

Como mantenedor do projeto, quero um inventário único dos arquivos de `docs/` com status (vigente, histórico, obsoleto, duplicado) para saber exatamente o que manter e o que remover/arquivar.

**Why this priority**: Sem inventário e critérios explícitos, qualquer limpeza vira ação arriscada e pode apagar conteúdo necessário.

**Independent Test**: Executar o checklist de classificação e verificar que 100% dos arquivos em `docs/` possuem decisão registrada.

**Acceptance Scenarios**:

1. **Given** a árvore atual de `docs/`, **When** o inventário é executado, **Then** cada arquivo recebe uma classificação e justificativa.
2. **Given** arquivos com sobreposição de tema, **When** são avaliados, **Then** apenas um documento canônico por tema é marcado como vigente.
3. **Given** documentos sem atualização relevante, **When** passam pelos critérios de vigência, **Then** são marcados para arquivo ou remoção.

---

### User Story 2 - Estrutura Enxuta e Navegável (Priority: P2)

Como usuário da documentação, quero navegar por um índice limpo e sem documentos duplicados para encontrar informações corretas rapidamente.

**Why this priority**: O valor da limpeza depende de navegação clara; remover sem reorganizar reduz discoverability.

**Independent Test**: Abrir `docs/INDEX.md` e validar que todos os links apontam para documentos vigentes e existentes.

**Acceptance Scenarios**:

1. **Given** documentos classificados como vigentes, **When** o índice é atualizado, **Then** ele referencia somente documentos vigentes.
2. **Given** documentos movidos para arquivo, **When** o índice principal é validado, **Then** não há links quebrados.
3. **Given** documentos obsoletos removidos, **When** a busca por títulos antigos é feita, **Then** há redirecionamento por nota de migração quando aplicável.

---

### User Story 3 - Governança para Evitar Nova Degradação (Priority: P3)

Como contribuidor, quero regras objetivas de atualização e arquivamento para impedir que a documentação volte a ficar desatualizada.

**Why this priority**: Sem governança, a limpeza se perde no tempo e o problema reaparece.

**Independent Test**: Aplicar checklist de contribuição em uma alteração nova e confirmar aderência sem ambiguidade.

**Acceptance Scenarios**:

1. **Given** nova feature implementada, **When** PR é aberto, **Then** há requisito explícito de atualização dos documentos canônicos.
2. **Given** documento sem manutenção ativa, **When** ultrapassa prazo de revisão definido, **Then** recebe marcação de status e ação (atualizar/arquivar).
3. **Given** mudança de API/arquitetura, **When** documentação é revisada, **Then** documentos de referência técnica e guias permanecem consistentes entre si.

### Edge Cases

- Documento com conteúdo parcialmente vigente e parcialmente obsoleto deve ser dividido em seção vigente + histórico arquivado.
- Documento histórico importante para rastreabilidade não deve ser removido; deve ser movido para `docs/archive/` com rótulo claro.
- Dois documentos diferentes com o mesmo assunto e versões conflitantes devem convergir para um canônico com nota de depreciação no outro.
- Links internos para arquivos removidos devem ser corrigidos no mesmo PR de limpeza.
- Documentos em português com termos divergentes devem ser padronizados para reduzir ambiguidade.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Sistema de documentação DEVE definir critérios objetivos de vigência para classificar cada arquivo de `docs/`.
- **FR-002**: Processo DEVE gerar inventário com decisão por arquivo: `vigente`, `histórico`, `obsoleto`, `duplicado`.
- **FR-003**: Documentos classificados como `vigente` DEVEM ter fonte canônica única por tema.
- **FR-004**: Documentos `histórico` DEVEM permanecer acessíveis em `docs/archive/` com contexto de data e escopo.
- **FR-005**: Documentos `obsoleto` ou `duplicado` DEVEM ser removidos ou redirecionados por nota de migração.
- **FR-006**: Índices principais (`docs/INDEX.md`, `README.md`, `mkdocs.yml`) DEVEM referenciar somente conteúdo vigente ou histórico explicitamente identificado.
- **FR-007**: Limpeza DEVE preservar coerência com princípios arquiteturais já definidos em `docs/architecture/principios-core.md`.
- **FR-008**: Processo DEVE incluir validação de links internos para evitar referências quebradas após movimentações.
- **FR-009**: Processo DEVE estabelecer política de revisão periódica para impedir reincidência de conteúdo desatualizado.
- **FR-010**: Toda documentação nova ou alterada DEVE estar em português (Brasil), com linguagem clara e objetiva.

### Key Entities *(include if feature involves data)*

- **DocumentoCanônico**: Documento oficial e vigente para um domínio específico (API, arquitetura, guia operacional), com dono e data de última revisão.
- **InventárioDeDocumentação**: Lista estruturada dos arquivos com status, motivo da decisão e ação necessária.
- **RegraDeGovernança**: Conjunto de critérios de atualização, arquivamento e validação de links aplicado em PRs.
- **MapaDeNavegação**: Índices e entradas que conectam usuários aos documentos corretos sem duplicidade.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% dos arquivos em `docs/` possuem classificação registrada no inventário.
- **SC-002**: 0 links quebrados em `docs/INDEX.md`, `README.md` e `mkdocs.yml` após a limpeza.
- **SC-003**: Redução mínima de 30% no número de documentos redundantes/obsoletos no diretório ativo de `docs/`.
- **SC-004**: Tempo para localizar documento canônico principal (API, arquitetura, setup) fica abaixo de 60 segundos em validação manual.
- **SC-005**: Novas PRs com mudança de feature passam a incluir atualização explícita da documentação canônica correspondente.

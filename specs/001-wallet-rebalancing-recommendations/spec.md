# Feature Specification: Recomendações de Rebalanceamento de Carteiras

**Feature Branch**: `001-wallet-rebalancing-recommendations`  
**Created**: 2026-02-22  
**Status**: Draft  
**Input**: User description: "Web application supporting personal investment management with wallet rebalancing recommendations based on profitability and value characteristics. Interface in Portuguese (Brazil) for democratized, accessible investment management."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Visualizar Carteiras Existentes (Priority: P1)

O usuário acessa a nova página "Carteiras" e visualiza todas as suas carteiras de investimento organizadas por objetivo (ex: Renda Fixa, Crescimento, Dividendos). Cada carteira mostra valor total, rentabilidade e alocação atual.

**Why this priority**: Fundação essencial - sem visualização das carteiras, nenhuma funcionalidade de rebalanceamento faz sentido. Entrega valor imediato ao permitir organização mental dos investimentos.

**Independent Test**: Usuário com operações existentes acessa /carteiras e vê lista de carteiras com totalizadores calculados a partir das operações. Pode ser demonstrado sem implementar rebalanceamento.

**Acceptance Scenarios**:

1. **Given** usuário possui operações de PETR4, VALE3 e ITSA4, **When** acessa página Carteiras, **Then** vê carteira padrão "Principal" com valor total, quantidade de ativos e rentabilidade calculada
2. **Given** usuário não possui operações, **When** acessa página Carteiras, **Then** vê mensagem "Nenhuma carteira criada" com botão "Criar primeira carteira"
3. **Given** usuário possui múltiplas carteiras, **When** visualiza lista, **Then** vê cada carteira com nome, valor total, percentual de alocação e indicador visual de performance (positivo/negativo)

---

### User Story 2 - Criar e Configurar Carteiras Personalizadas (Priority: P2)

O usuário cria uma nova carteira definindo nome, tipo (Renda Fixa, Ações, FIIs, Mista) e opcionalmente alocação-alvo percentual para cada tipo de ativo. Atribui ativos existentes às carteiras criadas.

**Why this priority**: Permite personalização e organização avançada, mas depende da visualização básica (US1). Entrega valor ao usuário que quer segregar investimentos por objetivo.

**Independent Test**: Usuário cria carteira "Aposentadoria" do tipo "Renda Fixa", atribui CDBs e Tesouro Direto, define alocação-alvo 70% RF / 30% FIIs. Sistema persiste e calcula métricas específicas dessa carteira.

**Acceptance Scenarios**:

1. **Given** usuário está na página Carteiras, **When** clica "Nova Carteira" e preenche nome "Dividendos", tipo "Ações", **Then** carteira é criada vazia e aparece na lista
2. **Given** carteira "Dividendos" criada, **When** usuário seleciona ativos ITSA4, VALE3 e move para a carteira, **Then** ativos são associados e valor da carteira recalculado
3. **Given** carteira com ativos, **When** usuário define alocação-alvo (60% Ações Valor, 40% Dividendos), **Then** sistema salva configuração e mostra desvio atual vs alvo

---

### User Story 3 - Receber Recomendações de Rebalanceamento (Priority: P3)

O usuário, na página de uma carteira específica, clica em "Analisar Rebalanceamento" e recebe sugestões concretas de compra/venda para atingir alocação-alvo, considerando custos de corretagem e impacto tributário.

**Why this priority**: Funcionalidade principal de valor, mas requer carteiras configuradas (US1, US2). Democratiza estratégia avançada de investimento.

**Independent Test**: Usuário com carteira "Crescimento" desbalanceada (80% PETR4, 20% VALE3, alvo: 50%/50%) recebe recomendação: "Vender 150 PETR4 (R$ 4.500) e Comprar 90 VALE3 (R$ 4.500)" com simulação de resultado pós-rebalanceamento.

**Acceptance Scenarios**:

1. **Given** carteira com alocação desbalanceada > 5% do alvo, **When** usuário clica "Analisar Rebalanceamento", **Then** sistema exibe tabela com ativos fora do alvo e sugestões de ajuste
2. **Given** recomendação gerada, **When** usuário visualiza detalhes, **Then** vê simulação: alocação atual → alocação pós-rebalanceamento, custos estimados (corretagem + impostos), impacto na rentabilidade
3. **Given** carteira já balanceada (desvio < 5%), **When** usuário solicita análise, **Then** sistema exibe "Carteira balanceada ✓" e sugere "Próxima revisão recomendada: 3 meses"

---

### User Story 4 - Executar Rebalanceamento Guiado (Priority: P4)

Após aceitar recomendação, o usuário é guiado em modo passo-a-passo para registrar as operações de venda e compra sugeridas, com validação de cada etapa e atualização em tempo real da carteira.

**Why this priority**: UX avançada que melhora adoção, mas não essencial para MVP. Usuário pode executar manualmente via CRUD de operações.

**Independent Test**: Usuário aceita rebalanceamento, sistema cria checklist: "1. Vender 150 PETR4 ☐", "2. Comprar 90 VALE3 ☐". Ao registrar cada operação, item é marcado e carteira recalculada.

**Acceptance Scenarios**:

1. **Given** recomendação aceita, **When** usuário inicia execução, **Then** sistema abre modal com checklist de operações pendentes
2. **Given** checklist aberto, **When** usuário clica "Registrar" em uma operação, **Then** abre formulário pré-preenchido (ticker, quantidade, tipo) para confirmação
3. **Given** todas operações executadas, **When** usuário finaliza, **Then** sistema exibe "Rebalanceamento concluído ✓", atualiza carteira e registra evento de rebalanceamento para histórico

---

### Edge Cases

- **Carteira vazia**: Sistema deve permitir criação de carteira sem ativos e sugerir "Adicione ativos para começar"
- **Ativos sem cotação**: Se ativo não possui cotação atualizada, rebalanceamento não pode ser calculado - exibir aviso e sugerir atualização manual
- **Múltiplas carteiras com mesmo ativo**: Ativo pode pertencer a N carteiras (ex: PETR4 em "Crescimento" e "Dividendos") - alocações são independentes
- **Alocação-alvo soma ≠ 100%**: Validar que soma das alocações-alvo = 100%, ou permitir "resto" automático em categoria "Outros"
- **Custos impedem rebalanceamento**: Se corretagem + impostos > benefício do rebalanceamento, sistema deve alertar "Não recomendado - custos superam ganhos"
- **Operações fracionadas**: Sugestões devem respeitar lote mínimo (ações: lote padrão ou fracionário conforme mercado do ativo)
- **Renda Fixa não negociável**: Ativos de RF (CDB, LCI) não podem ser vendidos - rebalanceamento deve apenas sugerir novos aportes
- **Carteira sem alocação-alvo**: Se usuário não definiu alvo, análise de rebalanceamento fica desabilitada com mensagem educativa

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Sistema DEVE permitir criar, editar e excluir carteiras de investimento com nome e tipo
- **FR-002**: Sistema DEVE calcular valor total, rentabilidade e alocação atual de cada carteira a partir das operações existentes (principle IV: valores derivados calculados)
- **FR-003**: Usuário DEVE poder atribuir ativos existentes a uma ou mais carteiras
- **FR-004**: Sistema DEVE permitir definir alocação-alvo percentual por categoria de ativo dentro de uma carteira
- **FR-005**: Sistema DEVE validar que soma das alocações-alvo = 100% antes de salvar
- **FR-006**: Sistema DEVE calcular desvio entre alocação atual e alvo para cada categoria
- **FR-007**: Sistema DEVE gerar recomendações de rebalanceamento quando desvio > threshold configurável (padrão: 5%)
- **FR-008**: Recomendações DEVEM incluir operações específicas (vender X unidades de ativo Y, comprar Z unidades de ativo W) com valores monetários
- **FR-009**: Sistema DEVE simular custos de rebalanceamento (corretagem + impostos estimados) e alertar se custo > benefício
- **FR-010**: Sistema DEVE respeitar liquidez de ativos (RF não negociável, ações fracionárias vs lote padrão)
- **FR-011**: Interface DEVE ser 100% em português (Brasil) incluindo labels, mensagens de erro e tooltips educativos
- **FR-012**: Carteiras DEVEM ser persistidas com relacionamento many-to-many com ativos (um ativo pode estar em N carteiras)
- **FR-013**: Sistema NÃO DEVE armazenar valores calculados como estado persistente - sempre recalcular de operações (principle IV)
- **FR-014**: Ao executar rebalanceamento, operações criadas DEVEM ser imutáveis e auditáveis (principle I)
- **FR-015**: Sistema DEVE exibir estados de loading, erro e vazio para todas as interações (código de qualidade frontend)

### Key Entities

- **Carteira (Wallet)**: Agrupamento lógico de ativos com nome, tipo (Ações/FIIs/RF/Mista), alocação-alvo opcional. Relaciona-se N:M com Ativos. Valores (total, rentabilidade) são calculados dinamicamente.
- **Alocação-Alvo (TargetAllocation)**: Configuração percentual desejada para cada categoria de ativo dentro de uma carteira. Ex: 60% Ações, 40% FIIs. Soma deve ser 100%.
- **Recomendação de Rebalanceamento (RebalancingRecommendation)**: Análise calculada sob demanda (não persistida) contendo lista de operações sugeridas, custos estimados e simulação de resultado pós-rebalanceamento.
- **Atribuição Ativo-Carteira (WalletAssetAssignment)**: Relacionamento entre Ativo e Carteira, opcionalmente com peso/prioridade customizado.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Usuário consegue criar carteira e atribuir 3+ ativos em menos de 2 minutos
- **SC-002**: Sistema calcula e exibe recomendação de rebalanceamento em menos de 3 segundos para carteira com até 20 ativos
- **SC-003**: Interface renderiza corretamente em desktop (1920x1080) e mobile (375x667) sem scroll horizontal
- **SC-004**: 90% dos usuários compreendem sugestão de rebalanceamento sem consultar documentação (medido por teste de usabilidade)
- **SC-005**: Cálculos de alocação têm precisão de 2 casas decimais e são consistentes com dashboard principal
- **SC-006**: Rebalanceamento executado através da interface gera operações válidas que aparecem corretamente na página Operações

- **SC-001**: [Measurable metric, e.g., "Users can complete account creation in under 2 minutes"]
- **SC-002**: [Measurable metric, e.g., "System handles 1000 concurrent users without degradation"]
- **SC-003**: [User satisfaction metric, e.g., "90% of users successfully complete primary task on first attempt"]
- **SC-004**: [Business metric, e.g., "Reduce support tickets related to [X] by 50%"]

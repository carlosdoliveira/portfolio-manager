# Quickstart: Carteiras e Rebalanceamento

**Feature**: 001-wallet-rebalancing-recommendations  
**Audience**: Desenvolvedores e usuários finais  
**Date**: 2026-02-22

## Para Desenvolvedores

### Setup Local

```bash
# 1. Checkout do branch
git checkout 001-wallet-rebalancing-recommendations

# 2. Aplicar migration no banco
cd backend
python -m app.db.database  # Executa migrations automáticas

# Ou manualmente:
sqlite3 app/data/portfolio.db < migrations/add_wallets_tables.sql

# 3. Rebuild containers
cd ..
docker-compose down
docker-compose up --build

# 4. Acessar aplicação
open http://localhost:5173/carteiras
```

### Estrutura de Arquivos

```
backend/app/
├── main.py                         # Adicionar rotas /wallets
├── repositories/
│   └── wallets_repository.py       # CRUD wallets
├── services/
│   ├── wallet_calculator.py        # Cálculos alocação
│   └── rebalancing_engine.py       # Algoritmo rebalanceamento
└── tests/
    └── test_rebalancing_engine.py  # Testes unitários

frontend/src/
├── pages/
│   └── Carteiras.tsx               # Página principal
├── components/
│   ├── WalletCard.tsx              # Card resumo
│   ├── WalletForm.tsx              # CRUD form
│   ├── AllocationChart.tsx         # Gráfico pizza
│   ├── RebalancingPanel.tsx        # Painel sugestões
│   └── AssetAllocationEditor.tsx   # Editor alocação-alvo
└── api/
    └── client.ts                   # Adicionar métodos wallets
```

### Testes Manuais Rápidos

#### Backend (curl)

```bash
# 1. Criar carteira
curl -X POST http://localhost:8000/api/wallets \
  -H "Content-Type: application/json" \
  -d '{"name": "Teste", "type": "Mista"}'

# 2. Listar carteiras
curl http://localhost:8000/api/wallets

# 3. Atribuir ativos (IDs 1, 2, 3)
curl -X POST http://localhost:8000/api/wallets/1/assets \
  -H "Content-Type: application/json" \
  -d '{"asset_ids": [1, 2, 3]}'

# 4. Definir alocação-alvo
curl -X PUT http://localhost:8000/api/wallets/1/allocations/target \
  -H "Content-Type: application/json" \
  -d '{"allocations": [
    {"category": "Ações", "target_percent": 60.0},
    {"category": "FIIs", "target_percent": 40.0}
  ]}'

# 5. Calcular rebalanceamento
curl http://localhost:8000/api/wallets/1/rebalancing?threshold=5.0
```

#### Frontend (Browser)

1. Acesse http://localhost:5173/carteiras
2. Clique "Nova Carteira" → preencha nome "Dividendos" → Salvar
3. Veja card criado na lista
4. Clique no card → visualize detalhes vazios
5. Clique "Adicionar Ativos" → selecione PETR4, VALE3 → Confirmar
6. Veja ativos listados com valores calculados
7. Clique "Configurar Alocação-Alvo" → defina: Ações 70%, FIIs 30% → Salvar
8. Clique "Analisar Rebalanceamento" → visualize sugestões

---

## Para Usuários Finais

### Passo 1: Criar Sua Primeira Carteira

1. No menu lateral, clique em **"Carteiras"**
2. Clique no botão **"+ Nova Carteira"**
3. Preencha:
   - **Nome**: Ex: "Aposentadoria", "Dividendos", "Crescimento"
   - **Tipo**: Escolha entre Ações, FIIs, Renda Fixa ou Mista
4. Clique **"Salvar"**

💡 **Dica**: Crie carteiras separadas para objetivos diferentes (ex: curto prazo vs longo prazo)

---

### Passo 2: Adicionar Ativos à Carteira

1. Clique no card da carteira recém-criada
2. Na página de detalhes, clique **"Adicionar Ativos"**
3. Selecione os ativos da lista (ex: PETR4, VALE3, ITSA4)
4. Clique **"Confirmar"**

📊 **Resultado**: Você verá cada ativo com quantidade, preço médio, valor atual e percentual da carteira

---

### Passo 3: Definir Alocação-Alvo (Opcional)

Se você quer receber recomendações de rebalanceamento, defina quanto quer em cada categoria:

1. Na página da carteira, clique **"Configurar Alocação-Alvo"**
2. Defina percentuais desejados:
   - **Ações**: Ex: 60%
   - **FIIs**: Ex: 30%
   - **Renda Fixa**: Ex: 10%
3. Certifique-se que a soma = 100%
4. Clique **"Salvar"**

✅ **Validação**: Sistema mostra erro se soma ≠ 100%

---

### Passo 4: Analisar Rebalanceamento

Quando sua carteira desbalancear (ex: ações valorizaram e agora são 75% ao invés de 60%):

1. Na página da carteira, clique **"Analisar Rebalanceamento"**
2. Sistema calcula e exibe:
   - **Alocação atual vs alvo** (gráfico visual)
   - **Sugestões concretas**: "Vender 50 PETR4" ou "Comprar 20 HGLG11"
   - **Custos estimados**: Corretagem + impostos
   - **Benefício líquido**: Quanto você ganha balanceando

3. Avalie:
   - 🟢 **Verde "Recomendado"**: Benefício > custos → vale a pena
   - 🔴 **Vermelho "Não recomendado"**: Custos > benefício → espere

---

### Passo 5: Executar Rebalanceamento (Futuro - US4)

*Funcionalidade planejada:*

1. Clique **"Executar Rebalanceamento"** no painel de sugestões
2. Sistema abre checklist passo-a-passo:
   - ☐ Vender 50 PETR4
   - ☐ Comprar 20 HGLG11
3. Para cada item:
   - Clique **"Registrar"**
   - Confirme operação (formulário pré-preenchido)
4. Sistema marca item como concluído ✓
5. Após todas operações: carteira atualizada automaticamente

---

## Casos de Uso Comuns

### Caso 1: Carteira de Aposentadoria (Conservadora)

```
Nome: Aposentadoria
Tipo: Mista
Alocação-Alvo:
  - Renda Fixa: 70%
  - FIIs: 20%
  - Ações: 10%

Ativos sugeridos:
  - Tesouro IPCA+ 2035
  - CDB 120% CDI
  - HGLG11 (FII shoppings)
  - ITSA4 (ação defensiva)
```

**Estratégia**: Rebalancear a cada 6 meses ou quando desvio > 10%

---

### Caso 2: Carteira de Crescimento (Agressiva)

```
Nome: Crescimento
Tipo: Ações
Alocação-Alvo:
  - Ações Crescimento: 60%
  - Ações Valor: 30%
  - ETFs: 10%

Ativos sugeridos:
  - MGLU3, PETZ3 (crescimento)
  - PETR4, VALE3 (valor)
  - BOVA11 (ETF Ibovespa)
```

**Estratégia**: Rebalancear trimestralmente ou quando desvio > 5%

---

### Caso 3: Carteira de Dividendos

```
Nome: Dividendos
Tipo: Mista
Alocação-Alvo:
  - Ações Dividendos: 50%
  - FIIs: 50%

Ativos sugeridos:
  - ITSA4, BBAS3, TAEE11
  - HGLG11, MXRF11, KNRI11
```

**Estratégia**: Manter balanceado, reinvestir dividendos recebidos

---

## Dicas de Uso

### ✅ Boas Práticas

- **Crie carteiras por objetivo**, não por corretora (ex: "Aposentadoria", não "XP")
- **Defina alocação-alvo realista**: Comece com faixas amplas (ex: 50-70% ações)
- **Rebalancear com disciplina**: Siga threshold (5-10%), não emocione
- **Considere impostos**: Vender ações gera IR sobre ganhos
- **Prefira aportes a vendas**: Quando possível, balanceie comprando (não vendendo)

### ⚠️ Evite

- **Rebalancear toda semana**: Custos superam benefícios
- **Ignorar custos**: Corretagem de R$ 50 come pequenos ganhos
- **Definir alocação muito rígida**: Ex: "45.37% ações" → impossível manter
- **Vender Renda Fixa**: Sistema já alerta, mas atenção: RF tem baixa liquidez

---

## Glossário

| Termo | Definição |
|-------|-----------|
| **Carteira** | Agrupamento de ativos por objetivo (ex: Aposentadoria) |
| **Alocação-Alvo** | % desejado para cada categoria de ativo |
| **Rebalanceamento** | Ajustar posições para voltar à alocação-alvo |
| **Desvio** | Diferença entre alocação atual e alvo (em pontos percentuais) |
| **Threshold** | Desvio mínimo para acionar rebalanceamento (padrão: 5%) |
| **Custo de Rebalanceamento** | Corretagem + impostos das operações sugeridas |
| **Benefício Líquido** | Ganho de balanceamento - custos |

---

## Próximos Passos

Após dominar carteiras básicas, explore:

1. **Múltiplas carteiras**: Segregue por prazo (curto/médio/longo)
2. **Pesos customizados**: Defina % específico para ativos importantes
3. **Revisão periódica**: Configure lembretes (futuro) para revisar trimestralmente

---

## Troubleshooting

### "Carteira não possui alocação-alvo"

**Solução**: Clique "Configurar Alocação-Alvo" e defina percentuais desejados

---

### "Cotações desatualizadas"

**Solução**: Vá em Dashboard → clique "Atualizar Cotações" → aguarde 30s → tente novamente

---

### "Não recomendado - custos superam ganhos"

**Explicação**: Seu desvio é pequeno e corretagem anularia o benefício. Espere ou aporte novo capital.

---

### Rebalanceamento sugere vender Renda Fixa

**Explicação**: Sistema detecta RF mas ação é "Aportar", não "Vender". Leia sugestão completa.

---

**Status**: ✅ Quickstart Complete

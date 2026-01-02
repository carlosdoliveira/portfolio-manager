# Princípios Arquiteturais do Portfolio Manager v2

Esta documentação descreve os princípios fundamentais que guiam todas as decisões técnicas do projeto.

---

## 🎯 Filosofia Geral

Portfolio Manager v2 é construído sobre uma **fundação sólida orientada a eventos**.

Favoreça sempre:
- **Clareza** sobre abstrações prematuras
- **Auditabilidade** sobre otimização precoce
- **Corretude** sobre rapidez de implementação

---

## 1. Operações São Eventos Imutáveis

### Princípio

Toda ação financeira (compra ou venda) é representada como uma **nova operação**.

### Regras

- ✅ **Nunca mutate uma operação existente** para representar uma venda
- ✅ Uma venda é sempre um novo registro com `movement_type = "VENDA"`
- ❌ **Não atualize** uma operação de compra quando o ativo é vendido

### Justificativa

Este princípio é **inegociável** porque:
- Permite auditoria completa do histórico
- Facilita reconciliação com extratos da corretora
- Torna cálculos de P&L determinísticos
- Evita perda acidental de dados históricos

### Exemplo Correto

```python
# Compra
{
  "id": 1,
  "ticker": "PETR4",
  "movement_type": "COMPRA",
  "quantity": 100,
  "price": 30.50,
  "trade_date": "2025-01-15"
}

# Venda (operação separada)
{
  "id": 2,
  "ticker": "PETR4",
  "movement_type": "VENDA",
  "quantity": 50,
  "price": 32.00,
  "trade_date": "2025-02-20"
}
```

### Exemplo Incorreto ❌

```python
# NÃO FAÇA ISSO!
# Atualizar operação de compra ao vender
{
  "id": 1,
  "ticker": "PETR4",
  "movement_type": "COMPRA",
  "quantity": 50,  # ❌ Alterado de 100 para 50
  "price": 30.50,
  "trade_date": "2025-01-15"
}
```

---

## 2. Importação É Idempotente

### Princípio

Importar o mesmo arquivo Excel da B3 múltiplas vezes **não deve criar duplicatas**.

### Implementação

Deduplicação baseada em chave de negócio:
- `trade_date`
- `movement_type`
- `market`
- `institution`
- `ticker`
- `quantity`
- `price`

### Garantias

1. **Banco de dados:** UNIQUE constraint na tabela `operations`
2. **Código:** Tratamento específico de `sqlite3.IntegrityError`
3. **UX:** Feedback claro sobre operações duplicadas

### Exemplo

```python
# Primeira importação
result = import_b3_excel("negociacao-2025-12-31.xlsx")
# { "inserted": 167, "duplicated": 0 }

# Segunda importação (mesmo arquivo)
result = import_b3_excel("negociacao-2025-12-31.xlsx")
# { "inserted": 0, "duplicated": 167 }
```

---

## 3. Pensamento Orientado a Eventos

### Princípio

Sempre raciocine sobre dados como **eventos ao longo do tempo**, não como estado mutável.

### Valores Derivados

Posição atual, saldo, P&L são **calculados** a partir de operações, nunca armazenados como estado autoritativo.

Ao menos nas fases iniciais, derivados devem ser:
- Calculados sob demanda
- Recalculáveis a qualquer momento
- Determinísticos (mesmas operações = mesmos resultados)

### Quando Armazenar Estado Derivado

Apenas quando:
- Performance se torna um problema real (medido, não assumido)
- Com estratégia de invalidação clara
- Mantendo operações como fonte da verdade

### Exemplo

```python
# ✅ Correto: calcular posição atual
def get_current_position(ticker: str) -> int:
    operations = fetch_operations(ticker)
    
    position = 0
    for op in operations:
        if op.movement_type == "COMPRA":
            position += op.quantity
        elif op.movement_type == "VENDA":
            position -= op.quantity
    
    return position

# ❌ Incorreto: armazenar posição como coluna
# Tabela: positions (ticker, quantity)
# Requer atualização a cada operação, pode desincronizar
```

---

## 4. Explícito > Implícito

### Princípio

Código deve ser óbvio e fácil de auditar.

### Diretrizes

- Prefira SQL explícito sobre ORMs pesados
- Funções pequenas e focadas
- Tratamento de exceções específico
- Validação de entrada rigorosa
- Logging estruturado em pontos-chave

### Exemplo

```python
# ✅ Correto: SQL explícito, exceções tratadas
def create_operation(conn, operation):
    try:
        conn.execute("""
            INSERT INTO operations 
            (ticker, movement_type, quantity, price, trade_date)
            VALUES (?, ?, ?, ?, ?)
        """, (
            operation.ticker,
            operation.movement_type,
            operation.quantity,
            operation.price,
            operation.trade_date
        ))
        logging.info(f"Operação criada: {operation.ticker}")
    except sqlite3.IntegrityError:
        logging.warning(f"Operação duplicada: {operation.ticker}")
        raise HTTPException(409, "Operação já existe")

# ❌ Incorreto: ORM mágico, exceção genérica
def create_operation(operation):
    try:
        db.session.add(operation)
        db.session.commit()
    except Exception:
        return {"error": "Erro"}
```

---

## 5. Testabilidade e Confiabilidade

### Princípio

Toda nova funcionalidade deve ser testável e testada antes do commit.

### Práticas

1. **Backend:** Testar endpoints, validação, casos de erro
2. **Frontend:** Verificar renderização, interações, estados de erro
3. **Integração:** Fluxos completos (upload → import → display)

### Checklist Antes de Commit

- [ ] Código executa sem erros
- [ ] Casos de erro são tratados
- [ ] Logs estão presentes
- [ ] Testes manuais executados
- [ ] Documentação atualizada

---

## 6. Simplicidade para Documentação

### Princípio

Código refatorado deve ser **simples de documentar**.

Se uma função precisa de 3 parágrafos para ser explicada, ela provavelmente precisa ser dividida.

### Diretrizes

- Nomes descritivos (funções, variáveis)
- Funções pequenas e com propósito único
- Evite truques "inteligentes"
- Prefira lógica explícita
- Docstrings em funções públicas

### Exemplo

```python
# ✅ Fácil de documentar
def calculate_total_invested(operations: list[Operation]) -> float:
    """Calcula o total investido somando todas as compras."""
    return sum(
        op.quantity * op.price 
        for op in operations 
        if op.movement_type == "COMPRA"
    )

# ❌ Difícil de documentar
def calc(ops):
    return reduce(lambda a,b: a+(b[2]*b[3] if b[1]=="C" else 0), ops, 0)
```

---

## Perguntas para Validar Decisões

Antes de adicionar qualquer funcionalidade, pergunte:

1. ✅ Isto é um **evento** ou uma **visão derivada**?
2. ✅ Pode ser recalculado a partir de operações existentes?
3. ✅ Isto preserva auditabilidade?
4. ✅ Isto quebra idempotência?
5. ✅ Isto dificulta reconciliação futura?

Se alguma resposta for problemática, **redesenhe**.

---

## Não-Objetivos (Por Enquanto)

- Otimização prematura
- ORMs pesados
- Bibliotecas complexas de estado (Redux, etc.)
- Abstrações over-engineered

---

## Resumo

Portfolio Manager v2 é construído sobre:
- **Imutabilidade** de eventos
- **Idempotência** de importações
- **Derivação** de valores
- **Clareza** de código
- **Testabilidade** de funcionalidades

Seu papel: **preserve essa fundação** enquanto estende o sistema incrementalmente.

Se em dúvida, favoreça **clareza, auditabilidade e corretude**.

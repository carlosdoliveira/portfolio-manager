# 🐛 Diagnóstico Final: Consolidação Fracionário/Vista

**Status:** ✅ RESOLVIDO  
**Data:** 3 de janeiro de 2026  
**Commit Final:** aed1a03

---

## 🎯 Problema Reportado

Após implementação do Item #2 (consolidação fracionário/vista), usuário reportou:

> "problema ainda persiste. Ao importar a planilha... os ativos importados seguem sendo duplicados entre o que é Fracionado e Mercado a Vista"

**Observado:**
- ITSA4 e ITSA4F aparecendo como ativos separados no UI
- 27 tickers únicos na planilha → 27 ativos criados (deveria ser ~22)
- Normalização não estava acontecendo

---

## 🔍 Causa Raiz Identificada

### BUG CRÍTICO: Normalização com Acentos

A função `normalize_ticker()` procurava por `"FRACIONARIO"` (sem acento), mas a planilha B3 real usa **"Mercado Fracionário"** com acento **á**.

```python
# ❌ CÓDIGO COM BUG
if "FRACIONARIO" in market and ticker.endswith("F"):
    return ticker[:-1]
```

**Por que falhava:**
1. Planilha B3: campo `Mercado` = `"Mercado Fracionário"` (com acento)
2. Código faz `.upper()`: `"MERCADO FRACIONÁRIO"` (mantém acento!)
3. Condição: `"FRACIONARIO" in "MERCADO FRACIONÁRIO"` → **FALSO** ❌
4. Ticker não era normalizado, criando duplicatas

**Nota Técnica:**  
Python `.upper()` **não remove acentos**, apenas converte para maiúsculas:
```python
"Fracionário".upper() == "FRACIONÁRIO"  # ✅ True (mantém acento)
"Fracionário".upper() == "FRACIONARIO"  # ❌ False
```

---

## ✅ Solução Implementada

Adicionar normalização de acentos antes da verificação:

```python
# ✅ CÓDIGO CORRIGIDO
market_normalized = market.replace("Á", "A").replace("É", "E") \
                          .replace("Í", "I").replace("Ó", "O") \
                          .replace("Ú", "U")

if "FRACIONARIO" in market_normalized and ticker.endswith("F"):
    return ticker[:-1]
```

**Arquivo:** `backend/app/services/importer.py` (linhas 50-58)  
**Commit:** aed1a03

---

## 📊 Validação com Planilha Real

### Teste: negociacao-2025-12-31-12-41-52.xlsx

**ANTES (com bug):**
```
Tickers únicos (raw): 27
Ativos criados: 27
- ITSA4: 2 operações (vista)
- ITSA4F: 18 operações (fracionário)
Status: ❌ Duplicado
```

**DEPOIS (corrigido):**
```
Tickers únicos (raw): 27
Ativos criados: 22 ✅ (5 pares consolidados)
- ITSA4: 20 operações (2 vista + 18 fracionário) ✅
- 0 ativos com sufixo 'F' ✅
Status: ✅ Consolidado
```

### Pares Consolidados

5 pares identificados e consolidados corretamente:

1. **BRSR6** + BRSR6F → BRSR6
2. **COGN3** + COGN3F → COGN3
3. **ITSA4** + ITSA4F → ITSA4
4. **JHSF3** + JHSF3F → JHSF3
5. **VVAR3** + VVAR3F → VVAR3

### Verificação no Banco

```sql
-- Total de ativos
SELECT COUNT(*) FROM assets WHERE status='ACTIVE';
-- Resultado: 22 ✅

-- Ativos com 'F' no final
SELECT ticker FROM assets WHERE ticker LIKE '%F' AND status='ACTIVE';
-- Resultado: (vazio) ✅

-- Operações de ITSA4
SELECT a.ticker, o.market, COUNT(*) 
FROM operations o 
JOIN assets a ON o.asset_id = a.id
WHERE a.ticker = 'ITSA4'
GROUP BY a.ticker, o.market;
-- Resultado:
-- ITSA4 | Mercado à Vista       | 2
-- ITSA4 | Mercado Fracionário   | 18
-- Total: 20 operações ✅
```

---

## 🎯 Resultado Final

✅ **Consolidação funcionando 100%**

- Redução de 27 → 22 ativos (5 pares consolidados)
- 0 ativos com sufixo 'F' no banco
- Operações corretamente vinculadas ao ativo consolidado
- Campo `market` preservado para auditoria
- Import idempotente mantido

---

## 📝 Lições Aprendidas

### 1. Testar com Dados Reais
Mock data nos testes não capturou o acento no campo "Mercado".  
**Ação:** Adicionar testes com dados reais de planilha B3.

### 2. Normalização de Strings
`.upper()` não remove acentos em Python (comportamento esperado).  
**Ação:** Sempre normalizar acentos quando comparar strings.

### 3. Validação Rigorosa
Logs mostravam "27 → 27" mas deveria ser "27 → 22".  
**Ação:** Alertar quando normalização não reduz quantidade.

### 4. Volume Docker
Database deve ser montado em `./backend/data` (não `./backend/app/data`).  
**Ação:** Script de reset agora usa `sudo rm -rf` para limpar corretamente.

---

## 🔗 Commits Relacionados

- `d61f0ea` - fix: aplica normalização de ticker também no CRUD manual
- `aed1a03` - fix(importer): corrige normalização para aceitar acentos no campo mercado

---

## 🚀 Próximos Passos

✅ Item #2 **COMPLETAMENTE RESOLVIDO**

Pode prosseguir para:
- Item #4: Totalizadores zerados (P0)
- Item #5: Valores por ativo zerados (P0)
- Item #6: Preço médio zerado (P1)

Ver: [CORRECAO-CALCULOS-CARTEIRA.md](CORRECAO-CALCULOS-CARTEIRA.md)

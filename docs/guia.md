# Guia Rápido

Guia de início rápido para o Portfolio Manager v2.

---

## 🎯 Objetivo

Este guia apresenta os passos essenciais para começar a usar o Portfolio Manager v2, desde a instalação até a primeira importação de dados.

---

## 📋 Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- **Docker** (versão 20.10 ou superior)
- **Docker Compose** (versão 2.0 ou superior)
- **Git** (para clonar o repositório)

---

## 🚀 Instalação

### 1. Clone o Repositório

```bash
git clone https://github.com/carlosdoliveira/portfolio-manager.git
cd portfolio-manager
```

### 2. Inicie os Serviços

```bash
./portfolio start
```

Este comando irá:
- Construir as imagens Docker
- Iniciar o backend (FastAPI)
- Iniciar o frontend (React + Vite)
- Criar o banco de dados SQLite

### 3. Acesse a Aplicação

Após a inicialização, acesse:

- **Frontend:** [http://localhost:5173](http://localhost:5173)
- **API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Backend:** [http://localhost:8000](http://localhost:8000)

---

## 📊 Primeira Importação B3

### Passo 1: Obter o Arquivo Excel

1. Acesse o site da B3
2. Baixe o relatório de negociações em formato Excel
3. Salve o arquivo em seu computador

### Passo 2: Importar na Aplicação

1. No frontend, acesse a página "Importar B3"
2. Clique em "Escolher Arquivo"
3. Selecione o arquivo Excel baixado
4. Clique em "Importar"

O sistema irá:
- Validar o formato do arquivo
- Processar as operações
- Deduplica automaticamente operações já importadas
- Exibir o resultado da importação

---

## 💼 Gerenciando Ativos

### Criar um Novo Ativo

1. Acesse "Ativos" no menu
2. Clique em "Novo Ativo"
3. Preencha os dados:
   - Ticker (código da ação)
   - Tipo de ativo
   - Descrição (opcional)
4. Clique em "Salvar"

### Visualizar Ativos

A tela de ativos mostra:
- Lista de todos os ativos
- Quantidade total de cada ativo
- Preço médio de compra
- Valor atual de mercado
- Variação (P&L não realizado)

---

## 📈 Operações Manuais

### Registrar Compra ou Venda

1. Acesse "Operações" no menu
2. Clique em "Nova Operação"
3. Preencha:
   - Ativo
   - Tipo (Compra ou Venda)
   - Data
   - Quantidade
   - Preço
4. Clique em "Salvar"

!!! warning "Importante"
    Operações são eventos imutáveis. Uma venda não altera uma compra anterior, mas cria um novo registro de venda.

---

## 💰 Renda Fixa

### Registrar um Título de Renda Fixa

1. Acesse "Renda Fixa" no menu
2. Clique em "Novo Título"
3. Preencha os dados:
   - Tipo (CDB, LCI, LCA, Tesouro Direto)
   - Emissor
   - Data de aplicação
   - Data de vencimento
   - Valor aplicado
   - Taxa (% a.a.)
4. Clique em "Salvar"

### Visualizar Projeções

O sistema calcula automaticamente:
- Rendimento bruto
- IR (se aplicável)
- Rendimento líquido
- Valor de resgate

---

## 🔧 Comandos Úteis

### Verificar Status

```bash
./portfolio status
```

### Ver Logs

```bash
./portfolio logs
```

### Reiniciar Serviços

```bash
./portfolio restart
```

### Parar Serviços

```bash
./portfolio stop
```

### Limpar Tudo (incluindo dados)

```bash
./portfolio clean-all
```

!!! danger "Atenção"
    O comando `clean-all` remove o banco de dados. Use com cuidado!

---

## 🆘 Problemas Comuns

### Containers não iniciam

**Solução:**
```bash
./portfolio clean
./portfolio start
```

### Porta já em uso

**Solução:**
Edite `docker-compose.yml` e altere as portas:
```yaml
ports:
  - "8001:8000"  # Altere 8000 para 8001
```

### Banco de dados corrompido

**Solução:**
```bash
./portfolio clean-all
./portfolio start
```

---

## 📚 Próximos Passos

- [Referência Técnica](referencia.md) - Detalhes da API e arquitetura
- [Documentação da API](api/endpoints.md) - Todos os endpoints disponíveis
- [Princípios Arquiteturais](architecture/principios-core.md) - Como o sistema funciona

---

## 📞 Suporte

- 🐛 [Reportar um Bug](https://github.com/carlosdoliveira/portfolio-manager/issues)
- 💡 [Sugerir uma Feature](https://github.com/carlosdoliveira/portfolio-manager/issues)
- 📖 [Documentação Completa](INDEX.md)

# Guia de Setup do Ambiente de Desenvolvimento

Este guia descreve como configurar o ambiente local para desenvolvimento do Portfolio Manager v2.

---

## 📋 Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- **Docker** (versão 20.10 ou superior)
- **Docker Compose** (versão 2.0 ou superior)
- **Git**

### Verificando Instalações

```bash
docker --version
# Docker version 20.10.x ou superior

docker compose version
# Docker Compose version v2.x.x ou superior

git --version
# git version 2.x.x ou superior
```

---

## 🚀 Setup Inicial

### 1. Clonar o Repositório

```bash
git clone https://github.com/carlosdoliveira/portfolio-manager.git
cd portfolio-manager-v2
```

### 2. Configurar Variáveis de Ambiente

#### Backend

Crie o arquivo `.env` na raiz do projeto:

```bash
# .env
CORS_ORIGINS=http://localhost:5173
```

#### Frontend

Crie o arquivo `frontend/.env`:

```bash
cd frontend
cp .env.example .env
```

Conteúdo de `frontend/.env`:

```bash
VITE_API_URL=http://localhost:8000
```

### 3. Iniciar a Aplicação

Use a CLI do projeto para gerenciar os containers:

```bash
# Tornar a CLI executável (primeira vez)
chmod +x portfolio

# Iniciar todos os serviços
./portfolio start
```

A CLI irá:
- Construir as imagens Docker
- Iniciar os containers (backend + frontend)
- Exibir os logs em tempo real

### 4. Verificar se Está Funcionando

Após alguns segundos, você deverá ver:

```
✓ Backend disponível em http://localhost:8000
✓ Frontend disponível em http://localhost:5173
```

Acesse http://localhost:5173 no navegador para ver a aplicação.

---

## 🛠️ Comandos da CLI

A CLI `./portfolio` oferece os seguintes comandos:

### Start

Inicia todos os serviços:

```bash
./portfolio start
```

### Stop

Para todos os serviços:

```bash
./portfolio stop
```

### Restart

Reinicia os serviços (útil após mudanças de código):

```bash
./portfolio restart
```

### Status

Verifica o status dos containers:

```bash
./portfolio status
```

### Logs

Exibe logs de um serviço específico:

```bash
# Logs do backend
./portfolio logs backend

# Logs do frontend
./portfolio logs frontend

# Logs de ambos
./portfolio logs
```

### Clean

Remove containers e volumes (mantém imagens):

```bash
./portfolio clean
```

### Clean All

Remove tudo (containers, volumes, imagens):

```bash
./portfolio clean-all
```

### Help

Exibe ajuda completa:

```bash
./portfolio help
```

---

## 🏗️ Estrutura do Projeto

```
portfolio-manager-v2/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── db/
│   │   │   └── database.py      # SQLite setup
│   │   ├── repositories/
│   │   │   └── operations_repository.py
│   │   └── services/
│   │       └── importer.py      # B3 Excel import
│   ├── data/                    # SQLite database
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── api/
│   │   │   └── client.ts        # API client
│   │   ├── components/
│   │   │   ├── ImportB3Card.tsx
│   │   │   └── layout/
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Import.tsx
│   │   │   └── Portfolio.tsx
│   │   └── styles/
│   ├── Dockerfile
│   └── package.json
│
├── docs/                        # Documentação wiki
├── docker-compose.yml
├── portfolio                    # CLI de orquestração
└── .env                        # Configurações
```

---

## 🔧 Desenvolvimento

### Modo de Desenvolvimento

O projeto está configurado para **hot reload**:

- **Backend:** FastAPI recarrega automaticamente ao salvar arquivos `.py`
- **Frontend:** Vite recarrega instantaneamente ao salvar arquivos `.tsx/.ts/.css`

Basta editar os arquivos e ver as mudanças no navegador.

### Executando Comandos nos Containers

#### Backend

```bash
# Entrar no container do backend
docker compose exec backend bash

# Executar Python
docker compose exec backend python -c "print('Hello')"
```

#### Frontend

```bash
# Entrar no container do frontend
docker compose exec frontend sh

# Executar npm commands
docker compose exec frontend npm run build
```

---

## 🧪 Testando a Importação

Para testar a funcionalidade de importação:

1. Acesse http://localhost:5173/import
2. Arraste um arquivo Excel da B3 (formato oficial de negociações)
3. Clique em "Importar"
4. Verifique o resumo da importação

### Arquivo de Teste

Um arquivo de exemplo está disponível em `tests/` (se houver).

---

## 📊 Acessando o Banco de Dados

O banco SQLite está em `backend/data/portfolio.db`.

Para inspecionar:

```bash
# Entrar no container
docker compose exec backend bash

# Abrir SQLite
sqlite3 /app/data/portfolio.db

# Ver tabelas
.tables

# Ver schema
.schema operations

# Fazer query
SELECT COUNT(*) FROM operations;

# Sair
.quit
```

---

## 🔍 Debugging

### Verificar Logs

Use `./portfolio logs` para verificar erros:

```bash
# Logs completos
./portfolio logs

# Últimas 50 linhas do backend
./portfolio logs backend --tail=50
```

### Problemas Comuns

#### Porta em Uso

Se portas 8000 ou 5173 estiverem ocupadas:

```bash
# Verificar processos usando a porta
lsof -i :8000
lsof -i :5173

# Matar processo
kill -9 <PID>
```

#### Containers Não Iniciam

```bash
# Limpar tudo e reconstruir
./portfolio clean-all
./portfolio start
```

#### Mudanças Não Aparecem

```bash
# Reiniciar serviços
./portfolio restart
```

#### Erro de Permissão no SQLite

```bash
# Garantir permissões no diretório data
chmod -R 777 backend/data
```

---

## 🧹 Limpeza

### Limpar Dados (Reset Database)

```bash
# Parar serviços
./portfolio stop

# Remover banco de dados
rm backend/data/portfolio.db

# Reiniciar (banco será recriado)
./portfolio start
```

### Limpar Docker Completamente

```bash
# Remover tudo do projeto
./portfolio clean-all

# Remover imagens órfãs do Docker
docker system prune -a
```

---

## 📚 Próximos Passos

Após configurar o ambiente:

1. Leia [Princípios Arquiteturais](../architecture/principios-core.md)
2. Consulte [Documentação de API](../api/)
3. Veja [Oportunidades de Melhoria](../oportunidades-backend.md) e [Frontend](../oportunidades-frontend.md)
4. Escolha uma tarefa e comece a contribuir!

---

## 🆘 Precisa de Ajuda?

- Consulte a [documentação completa](../README.md)
- Abra uma issue no GitHub
- Entre em contato com o time de desenvolvimento

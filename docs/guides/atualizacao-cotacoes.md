# Atualização Automática de Cotações

Este documento explica como configurar a atualização automática de cotações usando cron jobs.

## 📋 Visão Geral

O sistema mantém um cache de cotações no banco de dados SQLite para:
- ✅ Melhorar performance do dashboard
- ✅ Reduzir chamadas à API do yfinance  
- ✅ Permitir consultas rápidas de preços
- ✅ Funcionar mesmo se a API estiver lenta

## 🔄 Métodos de Atualização

### 1. Via API (Manual ou Webhook)

```bash
curl -X POST http://localhost:8000/quotes/update
```

**Resposta:**
```json
{
  "message": "14 cotações atualizadas",
  "total_tickers": 14,
  "updated": 14
}
```

### 2. Via Script Python (Cron Job)

Execute o script diretamente:

```bash
python3 backend/scripts/update_quotes_cron.py
```

## ⏰ Configurar Cron Job

### Passo 1: Tornar o script executável

```bash
chmod +x backend/scripts/update_quotes_cron.py
```

### Passo 2: Editar crontab

```bash
crontab -e
```

### Passo 3: Adicionar job

**Opção 1: Atualizar a cada 15 minutos (horário de mercado)**
```cron
# Atualizar cotações seg-sex, 9h-18h, a cada 15 min
*/15 9-18 * * 1-5 cd /home/seu-usuario/portfolio-manager-v2 && /usr/bin/python3 backend/scripts/update_quotes_cron.py >> backend/data/cron.log 2>&1
```

**Opção 2: Atualizar apenas nos fechamentos (10h e 18h)**
```cron
# Atualizar cotações seg-sex, às 10h e 18h
0 10,18 * * 1-5 cd /home/seu-usuario/portfolio-manager-v2 && /usr/bin/python3 backend/scripts/update_quotes_cron.py >> backend/data/cron.log 2>&1
```

**Opção 3: Atualizar a cada hora**
```cron
# Atualizar cotações a cada hora
0 * * * * cd /home/seu-usuario/portfolio-manager-v2 && /usr/bin/python3 backend/scripts/update_quotes_cron.py >> backend/data/cron.log 2>&1
```

### Passo 4: Verificar logs

```bash
tail -f backend/data/cron.log
# ou
tail -f backend/data/quotes_update.log
```

## 🐳 Configurar com Docker

Se estiver usando Docker, você tem duas opções:

### Opção 1: Cron no Host

Chame a API do container:

```cron
*/15 9-18 * * 1-5 curl -X POST http://localhost:8000/quotes/update >> /var/log/portfolio-quotes.log 2>&1
```

### Opção 2: Cron dentro do Container

1. Adicione ao `Dockerfile`:

```dockerfile
RUN apt-get update && apt-get install -y cron
COPY backend/scripts/quotes-cron /etc/cron.d/quotes-cron
RUN chmod 0644 /etc/cron.d/quotes-cron
RUN crontab /etc/cron.d/quotes-cron
```

2. Crie arquivo `backend/scripts/quotes-cron`:

```
*/15 9-18 * * 1-5 cd /app && python3 backend/scripts/update_quotes_cron.py >> /app/backend/data/cron.log 2>&1
```

3. Inicie o cron no container:

```dockerfile
CMD service cron start && uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 📊 Monitoramento

### Ver últimas atualizações

```bash
sqlite3 backend/data/portfolio.db "SELECT ticker, price, updated_at FROM quotes ORDER BY updated_at DESC LIMIT 10;"
```

### Ver status do cron

```bash
# Listar jobs ativos
crontab -l

# Ver log do sistema
grep CRON /var/log/syslog

# Ver log da aplicação
tail -f backend/data/quotes_update.log
```

## 🔧 Troubleshooting

### Cron não executa

1. Verificar se o cron está rodando:
```bash
sudo service cron status
```

2. Verificar permissões:
```bash
ls -la backend/scripts/update_quotes_cron.py
```

3. Testar manualmente:
```bash
cd /home/seu-usuario/portfolio-manager-v2
python3 backend/scripts/update_quotes_cron.py
```

### Cotações não atualizam

1. Verificar logs:
```bash
tail -20 backend/data/quotes_update.log
```

2. Verificar conexão com yfinance:
```bash
python3 -c "import yfinance as yf; print(yf.Ticker('PETR4.SA').history(period='1d'))"
```

3. Verificar banco de dados:
```bash
sqlite3 backend/data/portfolio.db "SELECT COUNT(*) FROM quotes;"
```

## 💡 Recomendações

- **Desenvolvimento:** Atualizar manualmente via API quando necessário
- **Produção:** Cron job a cada 15 minutos durante horário de mercado
- **Cache TTL:** O yfinance já tem delay de ~15min, não precisa atualizar mais frequentemente
- **Horário:** Mercado brasileiro: 10h-17h (horário de Brasília)

## 📚 Referências

- [Crontab Guru](https://crontab.guru/) - Testar expressões cron
- [yfinance Docs](https://pypi.org/project/yfinance/) - Documentação da API
- [SQLite Docs](https://www.sqlite.org/docs.html) - Documentação do banco

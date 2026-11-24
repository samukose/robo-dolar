# 💸 Robô do Dólar

Robô em Python que busca todo dia a cotação oficial do dólar (PTAX) na **API do Banco Central** (gratuita), guarda tudo numa tabela **MySQL** sem repetir nenhum dia e roda sozinho todo fim de tarde por agendamento.

> Projeto de portfólio de dados: consumo de API, banco de dados relacional, idempotência e automação.

## Como funciona

```
API do Banco Central (PTAX)  →  Python (requests)  →  MySQL  →  agendador (cron / Agendador de Tarefas)
```

1. O script consulta a API para um período de datas.
2. Para cada dia, mantém a última cotação (fechamento).
3. Grava no MySQL com `INSERT IGNORE`. A data é chave primária, então rodar duas vezes **nunca duplica** dados.
4. O agendador executa o script automaticamente todo dia útil.

## Tecnologias

- Python 3.10+
- MySQL 8
- Bibliotecas: `requests`, `mysql-connector-python`, `python-dotenv`, `truststore`

## Estrutura

```
robo-dolar/
├── robo_dolar.py       # busca na API e grava no banco
├── schema.sql          # cria o banco e a tabela
├── requirements.txt    # dependências
├── .env.example        # modelo de configuração
└── README.md
```

## Como usar

### 1. Preparar o banco
Execute o `schema.sql` no MySQL Workbench (ou pelo terminal). Ele cria o banco `cotacoes` e a tabela `cotacao_dolar`:

| coluna    | tipo          | descrição                     |
|-----------|---------------|-------------------------------|
| data      | DATE (PK)     | dia da cotação, único         |
| compra    | DECIMAL(10,4) | cotação de compra             |
| venda     | DECIMAL(10,4) | cotação de venda              |
| criado_em | TIMESTAMP     | quando o registro foi gravado |

### 2. Instalar dependências
```bash
pip install -r requirements.txt
```

### 3. Configurar a conexão
Copie `.env.example` para `.env` e preencha com seus dados:
```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=sua_senha
MYSQL_DATABASE=cotacoes
```
O `.env` está no `.gitignore`, então sua senha não vai para o GitHub.

### 4. Rodar
Carga histórica (uma vez):
```bash
python robo_dolar.py 2024-01-01
```
Uso diário (busca os últimos 10 dias):
```bash
python robo_dolar.py
```

### 5. Consultar
```sql
SELECT data, venda FROM cotacao_dolar ORDER BY data DESC LIMIT 10;
```

## Agendamento

**Windows** (Agendador de Tarefas, todo dia às 18:30):
```powershell
schtasks /create /tn "RoboDolar" /tr "python C:\caminho\robo-dolar\robo_dolar.py" /sc daily /st 18:30
```

**Linux / macOS** (cron, dias úteis às 18:30):
```
30 18 * * 1-5 python /caminho/robo-dolar/robo_dolar.py
```

## Próximos passos (ideias)

- Dashboard com a evolução do preço (Streamlit ou Power BI)
- Alerta por e-mail/Telegram quando o dólar passar de um valor
- Suporte a outras moedas (euro, libra)
- Logs e testes automatizados

## Fonte dos dados

[API Olinda – PTAX – Banco Central do Brasil](https://dadosabertos.bcb.gov.br/)

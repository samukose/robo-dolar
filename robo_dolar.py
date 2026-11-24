"""Robô do dólar: busca a PTAX na API do Banco Central e grava no MySQL sem repetir dias.

Uso:
    python robo_dolar.py              # busca os últimos 10 dias (uso diário)
    python robo_dolar.py 2024-01-01   # carga histórica desde a data informada
"""
import os
import sys
from datetime import date, timedelta

import mysql.connector
import requests
import truststore
from dotenv import load_dotenv

truststore.inject_into_ssl()  
load_dotenv()

URL = ("https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/"
       "CotacaoDolarPeriodo(dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)")


def buscar(inicio: date, fim: date) -> list[dict]:
    params = {
        "@dataInicial": f"'{inicio:%m-%d-%Y}'",
        "@dataFinalCotacao": f"'{fim:%m-%d-%Y}'",
        "$format": "json",
        "$select": "cotacaoCompra,cotacaoVenda,dataHoraCotacao",
    }
    r = requests.get(URL, params=params, timeout=30)
    r.raise_for_status()
    return r.json()["value"]


def conectar():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "cotacoes"),
    )


def salvar(linhas: list[dict]) -> int:
    # Uma linha por dia: fica com a última cotação (fechamento) de cada data.
    por_dia = {}
    for l in sorted(linhas, key=lambda x: x["dataHoraCotacao"]):
        por_dia[l["dataHoraCotacao"][:10]] = (
            l["dataHoraCotacao"][:10], l["cotacaoCompra"], l["cotacaoVenda"])
    conn = conectar()
    cur = conn.cursor()
    # INSERT IGNORE: se a data já existe, o MySQL pula (sem duplicar).
    cur.executemany(
        "INSERT IGNORE INTO cotacao_dolar (data, compra, venda) VALUES (%s, %s, %s)",
        list(por_dia.values()))
    novos = cur.rowcount
    conn.commit()
    conn.close()
    return novos


if __name__ == "__main__":
    hoje = date.today()
    inicio = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else hoje - timedelta(days=10)
    dados = buscar(inicio, hoje)
    print(f"{len(dados)} cotações recebidas do Banco Central")
    print(f"{salvar(dados)} dias novos gravados no MySQL")

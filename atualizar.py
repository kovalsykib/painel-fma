#!/usr/bin/env python3
"""
Rotina diária: baixa os dados do INMET das estações em estacoes.json, atualiza o histórico
(dados/<codigo>_diario.csv), recalcula a FMA sobre todo o histórico e gera o painel (docs/index.html).

Rodar:  python atualizar.py
"""
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

from fma import baixar_inmet, calcular_fma, diarizar

RAIZ = Path(__file__).parent
DADOS = RAIZ / "dados"
DOCS = RAIZ / "docs"
DIAS_INICIAL = 90        # primeira execução: baixa 90 dias para aquecer o acumulado
DIAS_ATUALIZACAO = 10    # execuções seguintes: reprocessa os últimos 10 dias (corrige dados atrasados)
DIAS_NO_PAINEL = 60
FUSO = timezone(timedelta(hours=-3))  # Brasília


def atualizar_estacao(est, hoje):
    cod = est["codigo"]
    arq = DADOS / f"{cod}_diario.csv"

    if arq.exists():
        hist = pd.read_csv(arq, parse_dates=["data"]).set_index("data")
        dias = max(DIAS_ATUALIZACAO, (hoje - hist.index.max().date()).days + 2)  # cobre falhas de vários dias
    else:
        hist = pd.DataFrame(columns=["umidade", "chuva"])
        hist.index.name = "data"
        dias = DIAS_INICIAL

    raw = baixar_inmet(cod, hoje - timedelta(days=dias + 1), hoje)
    novo = diarizar(raw)
    if not novo.empty:
        novo["data"] = pd.to_datetime(novo["data"])
        novo = novo[novo["data"].dt.date <= hoje].set_index("data")
        # hoje, antes da leitura das 13h, ainda não há umidade: não mostra o dia como "Sem dado"
        novo = novo[~((novo.index.date == hoje) & novo["umidade"].isna())]
        # valores novos têm prioridade; lacunas são preenchidas com o que já estava guardado
        hist = novo.combine_first(hist) if len(hist) else novo

    if hist.empty:
        raise RuntimeError(f"{cod}: nenhum dado disponível")

    hist = hist.sort_index()
    hist = hist.reindex(pd.date_range(hist.index.min(), hist.index.max(), name="data"))  # dias sem dado aparecem
    hist[["umidade", "chuva"]].to_csv(arq, date_format="%Y-%m-%d")

    res = calcular_fma(hist.reset_index())
    res.to_csv(DADOS / f"{cod}_fma.csv", index=False, date_format="%Y-%m-%d")
    return res


def serie_para_painel(res):
    ult = res.tail(DIAS_NO_PAINEL)
    linhas = []
    for _, r in ult.iterrows():
        linhas.append({
            "data": r["data"].strftime("%Y-%m-%d"),
            "umidade": None if pd.isna(r["umidade"]) else round(float(r["umidade"]), 1),
            "chuva": None if pd.isna(r["chuva"]) else round(float(r["chuva"]), 1),
            "fma": None if pd.isna(r["fma"]) else round(float(r["fma"]), 2),
            "classe": r["classe"],
            "aviso": r["aviso"],
        })
    return linhas


def gerar_painel(estacoes, resultados, erros):
    agora = datetime.now(FUSO)
    saida = {
        "atualizado": agora.strftime("%d/%m/%Y às %H:%M (Brasília)"),
        "erros": erros,
        "estacoes": [
            {"codigo": e["codigo"], "nome": e["nome"], "municipio": e["municipio"],
             "serie": serie_para_painel(resultados[e["codigo"]])}
            for e in estacoes if e["codigo"] in resultados
        ],
    }
    (DOCS / "dados.json").write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
    modelo = (RAIZ / "painel_template.html").read_text(encoding="utf-8")
    html = modelo.replace("__DADOS__", json.dumps(saida, ensure_ascii=False))
    (DOCS / "index.html").write_text(html, encoding="utf-8")


def main():
    DADOS.mkdir(exist_ok=True)
    DOCS.mkdir(exist_ok=True)
    estacoes = json.loads((RAIZ / "estacoes.json").read_text(encoding="utf-8"))
    hoje = datetime.now(FUSO).date()

    resultados, erros = {}, []
    for est in estacoes:
        cod = est["codigo"]
        try:
            resultados[cod] = atualizar_estacao(est, hoje)
            ult = resultados[cod].dropna(subset=["fma"]).tail(1)
            if not ult.empty:
                r = ult.iloc[0]
                print(f"{cod} {est['municipio']}: FMA {r['fma']:.2f} ({r['classe']}) em {r['data']:%d/%m/%Y}")
        except Exception as e:
            print(f"ERRO em {cod}: {e}", file=sys.stderr)
            erros.append({"codigo": cod, "erro": str(e)})
            arq = DADOS / f"{cod}_fma.csv"  # falhou o download: mostra o último resultado guardado
            if arq.exists():
                resultados[cod] = pd.read_csv(arq, parse_dates=["data"]).fillna({"aviso": ""})

    gerar_painel(estacoes, resultados, erros)
    if erros and not resultados:
        sys.exit(1)


if __name__ == "__main__":
    main()

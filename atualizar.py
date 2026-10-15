#!/usr/bin/env python3
"""
Rotina diária do painel FMA dos 15 municípios do PMIF.

Para cada município (municipios.json): baixa umidade e chuva horárias do modelo ECMWF (via Open-Meteo) no ponto de
cálculo do município, atualiza o histórico (dados/<codigo_ibge>_diario.csv), recalcula a FMA sobre todo o histórico e
gera o painel (docs/index.html e docs/dados.json).

Rodar:  python atualizar.py
"""
import json
import math
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

from fma import MODELO_PADRAO, baixar_openmeteo, calcular_fma

RAIZ = Path(__file__).parent
DADOS = RAIZ / "dados"
DOCS = RAIZ / "docs"
DIAS_INICIAL = 90        # primeira execução: baixa 90 dias para aquecer o acumulado
DIAS_ATUALIZACAO = 10    # execuções seguintes: reprocessa os últimos 10 dias (corrige dados atrasados)
DIAS_NO_PAINEL = 60
FUSO = timezone(timedelta(hours=-3))  # Brasília


def dist_km(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    h = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2
    return 2 * 6371.0 * math.asin(math.sqrt(h))


def estacao_mais_proxima(lat, lon):
    """Estação INMET (das usadas na validação) mais próxima do município; só para contexto no painel."""
    arq = RAIZ / "dados_estacoes" / "estacoes_meta.json"
    if not arq.exists():
        return None
    meta = json.loads(arq.read_text(encoding="utf-8"))
    cod = min(meta, key=lambda c: dist_km(lat, lon, meta[c]["latitude"], meta[c]["longitude"]))
    return {"codigo": cod, "nome": meta[cod]["nome"], "km": round(dist_km(lat, lon, meta[cod]["latitude"], meta[cod]["longitude"]))}


def atualizar_municipio(m, hoje):
    cod = m["codigo_ibge"]
    arq = DADOS / f"{cod}_diario.csv"

    if arq.exists():
        hist = pd.read_csv(arq, parse_dates=["data"]).set_index("data")
        dias = max(DIAS_ATUALIZACAO, (hoje - hist.index.max().date()).days + 2)  # cobre falhas de vários dias
    else:
        hist = pd.DataFrame(columns=["umidade", "chuva"])
        hist.index.name = "data"
        dias = DIAS_INICIAL

    novo = baixar_openmeteo(m["latitude"], m["longitude"], dias + 1, agora_local=datetime.now(FUSO))
    if not novo.empty:
        novo["data"] = pd.to_datetime(novo["data"])
        novo = novo[novo["data"].dt.date <= hoje].set_index("data")
        # hoje, antes da leitura das 13h, ainda não há umidade: não mostra o dia como "Sem dado"
        novo = novo[~((novo.index.date == hoje) & novo["umidade"].isna())]
        # valores novos têm prioridade; lacunas são preenchidas com o que já estava guardado
        hist = novo.combine_first(hist) if len(hist) else novo

    if hist.empty:
        raise RuntimeError(f"{m['nome']}: nenhum dado disponível")

    hist = hist.sort_index()
    hist = hist.reindex(pd.date_range(hist.index.min(), hist.index.max(), name="data"))  # dias sem dado aparecem
    hist[["umidade", "chuva"]].to_csv(arq, date_format="%Y-%m-%d")

    res = calcular_fma(hist.reset_index())
    res.to_csv(DADOS / f"{cod}_fma.csv", index=False, date_format="%Y-%m-%d")
    return res


def serie_para_painel(res):
    linhas = []
    for _, r in res.tail(DIAS_NO_PAINEL).iterrows():
        linhas.append({
            "data": r["data"].strftime("%Y-%m-%d"),
            "umidade": None if pd.isna(r["umidade"]) else round(float(r["umidade"]), 1),
            "chuva": None if pd.isna(r["chuva"]) else round(float(r["chuva"]), 1),
            "fma": None if pd.isna(r["fma"]) else round(float(r["fma"]), 2),
            "classe": r["classe"],
            "aviso": r["aviso"],
        })
    return linhas


def gerar_painel(municipios, resultados, erros):
    agora = datetime.now(FUSO)
    saida = {
        "atualizado": agora.strftime("%d/%m/%Y às %H:%M (Brasília)"),
        "modelo": "ECMWF IFS 0,25° (via Open-Meteo)",
        "modelo_id": MODELO_PADRAO,
        "erros": erros,
        "municipios": [
            {"codigo_ibge": m["codigo_ibge"], "nome": m["nome"], "latitude": m["latitude"], "longitude": m["longitude"],
             "estacao_proxima": estacao_mais_proxima(m["latitude"], m["longitude"]),
             "serie": serie_para_painel(resultados[m["codigo_ibge"]])}
            for m in municipios if m["codigo_ibge"] in resultados
        ],
    }
    (DOCS / "dados.json").write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
    # o painel leva também os contornos (só no HTML, para o dados.json continuar leve)
    com_mapa = dict(saida)
    com_mapa["contornos"] = {m["codigo_ibge"]: m["poligonos"] for m in municipios}
    modelo = (RAIZ / "painel_template.html").read_text(encoding="utf-8")
    html = modelo.replace("__DADOS__", json.dumps(com_mapa, ensure_ascii=False, separators=(",", ":")))
    (DOCS / "index.html").write_text(html, encoding="utf-8")


def main():
    DADOS.mkdir(exist_ok=True)
    DOCS.mkdir(exist_ok=True)
    municipios = json.loads((RAIZ / "municipios.json").read_text(encoding="utf-8"))
    hoje = datetime.now(FUSO).date()

    resultados, erros = {}, []
    for m in municipios:
        cod = m["codigo_ibge"]
        try:
            resultados[cod] = atualizar_municipio(m, hoje)
            ult = resultados[cod].dropna(subset=["fma"]).tail(1)
            if not ult.empty:
                r = ult.iloc[0]
                print(f"{m['nome']}: FMA {r['fma']:.2f} ({r['classe']}) em {r['data']:%d/%m/%Y}")
        except Exception as e:
            print(f"ERRO em {m['nome']}: {e}", file=sys.stderr)
            erros.append({"codigo": cod, "nome": m["nome"], "erro": str(e)})
            arq = DADOS / f"{cod}_fma.csv"  # falhou o download: mostra o último resultado guardado
            if arq.exists():
                resultados[cod] = pd.read_csv(arq, parse_dates=["data"]).fillna({"aviso": ""})
        time.sleep(1)   # gentileza com a API gratuita

    gerar_painel(municipios, resultados, erros)
    if erros and not resultados:
        sys.exit(1)


if __name__ == "__main__":
    main()

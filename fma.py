#!/usr/bin/env python3
"""
FMA - Fórmula de Monte Alegre (Soares, 1972)

FMA = soma acumulada de 100/H, onde H = umidade relativa (%) às 13h (local).
Regras de chuva (24h, em mm):
    <= 2,4        : sem alteração
    2,5  a  4,9   : abate 30% do acumulado da véspera e soma 100/H do dia
    5,0  a  9,9   : abate 60% do acumulado da véspera e soma 100/H do dia
    10,0 a 12,9   : abate 80% do acumulado da véspera e soma 100/H do dia
    > 12,9        : interrompe o cálculo (acumulado = 0); recomeça no dia seguinte

Janela de chuva: das 14h do dia anterior até as 13h do dia do cálculo (horário local).

Classes de perigo:
    <= 1,0 Nulo | 1,1-3,0 Pequeno | 3,1-8,0 Médio | 8,1-20,0 Alto | > 20,0 Muito alto

Uso:
    python fma.py --csv dados.csv                  # colunas: data,umidade,chuva
    python fma.py --estacao A601 --dias 60         # baixa do INMET (API pública)
"""
import argparse
import time
from datetime import date, timedelta

import pandas as pd

HORA_UTC_13H_LOCAL = 16  # 13h de Brasília (UTC-3) = 16h UTC. Ajuste se a estação usar outro fuso.

CLASSES = [(1.0, "Nulo"), (3.0, "Pequeno"), (8.0, "Médio"), (20.0, "Alto"),(>20.0, "Muito alto")]


def classificar(valor):
    if pd.isna(valor):
        return "Sem dado"
    for limite, nome in CLASSES:
        if valor <= limite:
            return nome
    return "Muito alto"


def calcular_fma(df):
    """df com colunas: data, umidade (% às 13h), chuva (mm em 24h).
    Retorna df com fma, classe e aviso."""
    df = df.sort_values("data").reset_index(drop=True).copy()
    acumulado = 0.0
    valores, avisos = [], []
    for _, linha in df.iterrows():
        h, chuva = linha["umidade"], linha["chuva"]

        if pd.isna(h):  # sem umidade: não dá para somar; mantém acumulado e sinaliza
            valores.append(float("nan"))
            avisos.append("sem umidade às 13h")
            continue

        aviso = ""
        if pd.isna(chuva):
            aviso = "chuva ausente (assumida 0 mm)"
            chuva = 0.0

        if chuva > 12.9:
            acumulado = 0.0
            valores.append(0.0)
            avisos.append(aviso)
            continue
        if chuva >= 10.0:
            acumulado *= 0.2
        elif chuva >= 5.0:
            acumulado *= 0.4
        elif chuva >= 2.5:
            acumulado *= 0.7

        acumulado += 100.0 / max(h, 1.0)  # evita divisão por zero
        valores.append(acumulado)
        avisos.append(aviso)

    df["fma"] = valores
    df["classe"] = df["fma"].map(classificar)
    df["aviso"] = avisos
    return df


# ---------------------------------------------------------------- INMET
def baixar_inmet(codigo, inicio, fim, tentativas=3):
    import requests

    url = f"https://apitempo.inmet.gov.br/estacao/{inicio:%Y-%m-%d}/{fim:%Y-%m-%d}/{codigo}"
    ultimo_erro = None
    cabecalhos = {"User-Agent": "Mozilla/5.0 (compatible; painel-fma)", "Accept": "application/json"}
    for i in range(tentativas):
        try:
            r = requests.get(url, timeout=60, headers=cabecalhos)
            corpo = r.text.strip()
            if r.status_code != 200:
                raise ValueError(f"HTTP {r.status_code}. Início da resposta: {corpo[:300]!r}")
            try:
                dados = r.json()
            except ValueError:
                raise ValueError(
                    f"HTTP {r.status_code}, tipo {r.headers.get('Content-Type')}, "
                    f"{len(corpo)} caracteres. Início da resposta: {corpo[:300]!r}"
                )
            if not isinstance(dados, list):
                raise ValueError(f"resposta inesperada da API: {str(dados)[:300]}")
            return pd.DataFrame(dados)
        except Exception as e:  # rede, JSON inválido, HTTP != 200
            ultimo_erro = e
            time.sleep(5 * (i + 1))
    raise RuntimeError(f"falha ao baixar {codigo} do INMET: {ultimo_erro}")


def _coluna(raw, opcoes):
    for c in opcoes:
        if c in raw.columns:
            return c
    raise KeyError(f"nenhuma das colunas {opcoes} encontrada. Colunas recebidas: {list(raw.columns)}")


def diarizar(raw, hora_utc=HORA_UTC_13H_LOCAL):
    """Transforma dados horários do INMET (UTC) em umidade às 13h locais e chuva das 24h anteriores
    (das 14h do dia anterior às 13h do dia)."""
    if raw.empty:
        return pd.DataFrame(columns=["data", "umidade", "chuva"])
    raw = raw.copy()
    c_umd = _coluna(raw, ["UMD_INS", "UMID_INS", "UMD"])
    c_chuva = _coluna(raw, ["CHUVA", "PRE_INS"])

    hora = pd.to_numeric(raw["HR_MEDICAO"], errors="coerce") // 100
    raw["dt"] = pd.to_datetime(raw["DT_MEDICAO"]) + pd.to_timedelta(hora, unit="h")
    raw["umd"] = pd.to_numeric(raw[c_umd], errors="coerce")
    raw["chuva_h"] = pd.to_numeric(raw[c_chuva], errors="coerce")
    raw = raw.sort_values("dt")

    umid = raw[raw["dt"].dt.hour == hora_utc].copy()
    umid["data"] = umid["dt"].dt.normalize()
    umid = umid.set_index("data")["umd"]
    umid = umid[~umid.index.duplicated(keep="last")]

    # janela de 24h terminando às 13h locais: (hora_utc+1 do dia anterior) até hora_utc do dia
    raw["data"] = (raw["dt"] + pd.to_timedelta(23 - hora_utc, unit="h")).dt.normalize()
    chuva = raw.groupby("data")["chuva_h"].agg(lambda s: s.sum(min_count=20))  # NaN se faltar muita hora

    out = pd.concat([umid.rename("umidade"), chuva.rename("chuva")], axis=1)
    out.index.name = "data"
    out = out.dropna(how="all").reset_index()
    out["data"] = pd.to_datetime(out["data"]).dt.date
    return out


# ---------------------------------------------------------------- Open-Meteo
def baixar_openmeteo(lat, lon, dias=90, agora_local=None, tentativas=3):
    """Baixa umidade e chuva horárias (modelo/reanálise) do Open-Meteo para um ponto e devolve,
    por dia: umidade às 13h locais e chuva acumulada das 14h do dia anterior às 13h do dia.

    No Open-Meteo, 'precipitation' de cada hora é a soma da hora anterior, o mesmo critério do INMET;
    por isso a janela usa os rótulos de 14:00 (dia anterior) até 13:00 (dia do cálculo).
    Horários futuros são descartados: só entram dias cuja leitura das 13h já passou."""
    import requests

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat, "longitude": lon,
        "hourly": "relative_humidity_2m,precipitation",
        "timezone": "America/Sao_Paulo",
        "past_days": min(int(dias), 92),
        "forecast_days": 1,
    }
    ultimo_erro = None
    for i in range(tentativas):
        try:
            r = requests.get(url, params=params, timeout=60)
            if r.status_code != 200:
                raise ValueError(f"HTTP {r.status_code}. Início da resposta: {r.text[:300]!r}")
            h = r.json()["hourly"]
            break
        except Exception as e:
            ultimo_erro = e
            time.sleep(5 * (i + 1))
    else:
        raise RuntimeError(f"falha ao baixar dados do Open-Meteo: {ultimo_erro}")

    df = pd.DataFrame({
        "dt": pd.to_datetime(h["time"]),  # já em horário local (America/Sao_Paulo)
        "umd": pd.to_numeric(pd.Series(h["relative_humidity_2m"]), errors="coerce"),
        "chuva_h": pd.to_numeric(pd.Series(h["precipitation"]), errors="coerce"),
    })
    if agora_local is not None:
        df = df[df["dt"] <= pd.Timestamp(agora_local).tz_localize(None)]  # sem horários futuros

    umid = df[df["dt"].dt.hour == 13].copy()
    umid["data"] = umid["dt"].dt.normalize()
    umid = umid.set_index("data")["umd"]

    # janela 14:00 (dia anterior) ... 13:00 (dia): desloca 10h para frente e agrupa por dia
    df["data"] = (df["dt"] + pd.to_timedelta(10, unit="h")).dt.normalize()
    chuva = df.groupby("data")["chuva_h"].agg(lambda s: s.sum(min_count=20))
    # só vale a chuva de dias cuja janela já terminou (existe a leitura das 13h)
    chuva = chuva[chuva.index.isin(umid.index)]

    out = pd.concat([umid.rename("umidade"), chuva.rename("chuva")], axis=1)
    out.index.name = "data"
    out = out.dropna(how="all").reset_index()
    out["data"] = pd.to_datetime(out["data"]).dt.date
    return out


def main():
    ap = argparse.ArgumentParser(description="Calcula a FMA (Fórmula de Monte Alegre)")
    ap.add_argument("--csv", help="CSV com colunas data,umidade,chuva")
    ap.add_argument("--estacao", help="Código INMET da estação (ex.: A601)")
    ap.add_argument("--dias", type=int, default=60, help="Janela de dias a baixar (inclui aquecimento)")
    ap.add_argument("--saida", help="Salva o resultado em CSV")
    args = ap.parse_args()

    if args.csv:
        df = pd.read_csv(args.csv, parse_dates=["data"])
    elif args.estacao:
        fim = date.today()
        raw = baixar_inmet(args.estacao, fim - timedelta(days=args.dias + 1), fim)
        df = diarizar(raw)
    else:
        ap.error("informe --csv ou --estacao")

    res = calcular_fma(df)
    print(res.to_string(index=False))
    if args.saida:
        res.to_csv(args.saida, index=False)


if __name__ == "__main__":
    main()

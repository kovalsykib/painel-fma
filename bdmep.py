"""
Leitura dos CSVs horários do BDMEP/INMET (estações automáticas) e conversão para o formato diário da FMA.

Formato do arquivo (conferido em out/2026):
  - 8 linhas de metadados (Nome, Codigo Estacao, Latitude, Longitude, Altitude, Situacao, Data Inicial/Final, Periodicidade)
  - uma linha em branco e a linha de cabeçalho, que começa com "Data Medicao"
  - separador ';', decimal ',', ausência de medição = 'null', ';' no fim de cada linha
  - Hora Medicao em UTC, no formato HHMM
"""
import io
import re
from pathlib import Path

import pandas as pd

COLUNAS = {
    "PRECIPITACAO TOTAL, HORARIO(mm)": "chuva_h",
    "TEMPERATURA DO AR - BULBO SECO, HORARIA(°C)": "temp",
    "UMIDADE RELATIVA DO AR, HORARIA(%)": "umd",
    "VENTO, VELOCIDADE HORARIA(m/s)": "vento",
}


def ler_bdmep(caminho):
    """Lê um CSV horário do BDMEP. Retorna (meta, df) com df indexado por 'dt' (UTC, sem fuso)
    e colunas chuva_h, temp, umd, vento (NaN onde o INMET informa 'null')."""
    texto = Path(caminho).read_text(encoding="utf-8-sig")
    linhas = texto.splitlines()
    i_cab = next(i for i, l in enumerate(linhas) if l.startswith("Data Medicao"))

    meta = {}
    for l in linhas[:i_cab]:
        if ":" in l:
            k, v = l.split(":", 1)
            meta[k.strip()] = v.strip()
    meta["codigo"] = meta.get("Codigo Estacao")
    for k in ("Latitude", "Longitude", "Altitude"):
        if k in meta:
            meta[k.lower()] = float(meta[k])

    df = pd.read_csv(
        io.StringIO("\n".join(linhas[i_cab:])),
        sep=";", decimal=",", na_values=["null", ""], dtype={"Hora Medicao": str},
        index_col=False,
    )
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
    desconhecidas = [c for c in df.columns if c not in COLUNAS and c not in ("Data Medicao", "Hora Medicao")]
    if desconhecidas:
        raise ValueError(f"colunas inesperadas no BDMEP: {desconhecidas}")

    hora = df["Hora Medicao"].str.zfill(4).str[:2].astype(int)
    df["dt"] = pd.to_datetime(df["Data Medicao"]) + pd.to_timedelta(hora, unit="h")
    df = df.rename(columns=COLUNAS).drop(columns=["Data Medicao", "Hora Medicao"]).set_index("dt").sort_index()
    df = df[~df.index.duplicated(keep="last")]
    return meta, df


def diario_fma(df_horario, hora_utc=16, min_horas_chuva=20):
    """Converte dados horários (UTC) em umidade às 13h locais (16h UTC) e chuva acumulada
    das 14h do dia anterior às 13h do dia (rótulos 17h UTC do dia anterior ... 16h UTC do dia).
    Aceita df com colunas 'umd' e 'chuva_h' indexado por 'dt' (UTC)."""
    d = df_horario
    umid = d.loc[d.index.hour == hora_utc, "umd"]
    umid.index = umid.index.normalize()

    deslocado = d.index + pd.Timedelta(hours=23 - hora_utc)  # 17h UTC (D-1) -> 00h de D ... 16h UTC (D) -> 23h de D
    chuva = d["chuva_h"].groupby(deslocado.normalize()).agg(lambda s: s.sum(min_count=min_horas_chuva))
    chuva = chuva[chuva.index.isin(umid.index)]

    out = pd.concat([umid.rename("umidade"), chuva.rename("chuva")], axis=1)
    out.index.name = "data"
    return out.dropna(how="all")

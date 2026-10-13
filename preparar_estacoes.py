#!/usr/bin/env python3
"""
Converte os CSVs horários do BDMEP em arquivos diários leves (dados_estacoes/<COD>.csv) com, por dia:
umidade às 13h locais, chuva das 14h do dia anterior às 13h do dia, temperatura e vento às 13h locais.
Também grava dados_estacoes/estacoes_meta.json (nome, coordenadas, altitude).

Uso:  python preparar_estacoes.py PASTA_COM_OS_CSVS [--desde 2022-01-01]
"""
import argparse
import glob
import json
from pathlib import Path

import pandas as pd

from bdmep import diario_fma, ler_bdmep

RAIZ = Path(__file__).parent
SAIDA = RAIZ / "dados_estacoes"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pasta")
    ap.add_argument("--desde", default="2022-01-01")
    args = ap.parse_args()

    SAIDA.mkdir(exist_ok=True)
    meta_todas = {}
    for arq in sorted(glob.glob(str(Path(args.pasta) / "*dados_A*_H_*.csv"))):
        meta, h = ler_bdmep(arq)
        cod = meta["codigo"]
        d = diario_fma(h)
        h13 = h[h.index.hour == 16][["temp", "vento"]]
        h13.index = h13.index.normalize()
        d = d.join(h13.rename(columns={"temp": "temp13", "vento": "vento13"}), how="left")
        d = d.loc[args.desde:]
        d.round(2).to_csv(SAIDA / f"{cod}.csv", date_format="%Y-%m-%d")
        meta_todas[cod] = {
            "nome": meta["Nome"].title(), "latitude": meta["latitude"], "longitude": meta["longitude"],
            "altitude": meta["altitude"], "dados_desde": str(d.index.min().date()), "dados_ate": str(d.index.max().date()),
            "dias": int(len(d)), "pct_umidade_13h": round(100 * d["umidade"].notna().mean(), 1),
            "pct_chuva": round(100 * d["chuva"].notna().mean(), 1),
        }
        print(f"{cod}: {len(d)} dias, UR 13h em {meta_todas[cod]['pct_umidade_13h']}%, chuva em {meta_todas[cod]['pct_chuva']}%")
    (SAIDA / "estacoes_meta.json").write_text(json.dumps(meta_todas, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()

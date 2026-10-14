#!/usr/bin/env python3
"""
Compara modelos FIXOS do Open-Meteo (GFS, ICON, ECMWF) e combinações deles contra as estações do INMET,
com a mesma régua da calibração: classe da FMA, erro da FMA, detecção de chuva > 12,9 mm.

Cenários: gfs | icon | ecmwf | media3 (UR = média dos 3; chuva = média dos 3)
          | mediana3 (chuva = mediana dos 3, equivale a "2 de 3 concordam" para o limiar) | bruto_automatico (best match).
Período: dados de 2024-10-01 em diante (aquecimento da FMA); métricas só a partir de 2025-01-01.

Uso:  python comparar_modelos.py            (6 estações)
      python comparar_modelos.py --todas    (todas as estações)
Saída: comparacao_modelos/relatorio.md e metricas.csv
"""
import json
import sys
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

import calibracao as cal
import calibrar
from fma import diario_de_openmeteo

RAIZ = Path(__file__).parent
SAIDA = RAIZ / "comparacao_modelos"
INICIO_DADOS = date(2024, 10, 1)
INICIO_TESTE = "2025-01-01"
MODELOS = {"gfs": "gfs_seamless", "icon": "icon_seamless", "ecmwf": "ecmwf_ifs025"}


def diario(h):
    d = diario_de_openmeteo(h)
    d["data"] = pd.to_datetime(d["data"])
    return d.set_index("data")


def combinar(series, chuva_fn):
    """series: lista de DataFrames diários (umidade, chuva). UR = média; chuva = chuva_fn (média ou mediana)."""
    ur = pd.concat([s["umidade"] for s in series], axis=1)
    ch = pd.concat([s["chuva"] for s in series], axis=1)
    return pd.DataFrame({"umidade": ur.mean(axis=1), "chuva": getattr(ch, chuva_fn)(axis=1)})


def main(baixador=calibrar.baixar_horario, n_estacoes=6):
    SAIDA.mkdir(exist_ok=True)
    meta = json.loads((calibrar.ESTACOES / "estacoes_meta.json").read_text(encoding="utf-8"))
    cods = sorted(meta)
    if n_estacoes and len(cods) > n_estacoes:
        passo = len(cods) / n_estacoes
        cods = [cods[int(i * passo)] for i in range(n_estacoes)]
    ontem = date.today() - timedelta(days=1)

    linhas = []
    for cod in cods:
        m = meta[cod]
        ini = max(INICIO_DADOS, date.fromisoformat(m["dados_desde"]))
        print(f"{cod} {m['nome']}", flush=True)
        obs = calibrar.carregar_obs(cod)
        obs = obs[obs.index >= pd.Timestamp(ini)]
        por_modelo = {}
        for nome, id_ in MODELOS.items():
            print(f"   {nome}...", flush=True)
            por_modelo[nome] = diario(baixador(m["latitude"], m["longitude"], ini, ontem, modelo=id_))
        print("   automatico (best match)...", flush=True)
        auto = diario(baixador(m["latitude"], m["longitude"], ini, ontem))

        cenarios = dict(por_modelo)
        trio = list(por_modelo.values())
        cenarios["media3"] = combinar(trio, "mean")
        cenarios["mediana3"] = combinar(trio, "median")
        cenarios["automatico"] = auto
        for nome, serie in cenarios.items():
            r = cal.metricas(serie, obs, INICIO_TESTE)
            r.update(estacao=cod, cenario=nome)
            linhas.append(r)

    df = pd.DataFrame(linhas)
    df.round(2).to_csv(SAIDA / "metricas.csv", index=False)
    escrever_relatorio(df, meta)
    print("Pronto: comparacao_modelos/relatorio.md e metricas.csv")


def _fmt(x, d=1):
    return "-" if pd.isna(x) else f"{x:.{d}f}".replace(".", ",")


def escrever_relatorio(df, meta):
    ordem = ["gfs", "icon", "ecmwf", "media3", "mediana3", "automatico"]
    rot = {"gfs": "GFS", "icon": "ICON", "ecmwf": "ECMWF", "media3": "Média dos 3", "mediana3": "Mediana dos 3",
           "automatico": "Automático (atual)"}

    def tabela(col, d, titulo):
        piv = df.pivot(index="estacao", columns="cenario", values=col)[ordem]
        w = df[df["cenario"] == "gfs"].set_index("estacao")["dias_fma"]
        cab = "| Estação | " + " | ".join(rot[c] for c in ordem) + " |"
        linhas = [cab, "|---" * (len(ordem) + 1) + "|"]
        for cod, r in piv.iterrows():
            linhas.append(f"| {cod} {meta[cod]['nome']} | " + " | ".join(_fmt(r[c], d) for c in ordem) + " |")
        med = {c: (piv[c] * w).sum() / w[piv[c].notna()].sum() for c in ordem}
        linhas.append("| **Média ponderada** | " + " | ".join(f"**{_fmt(med[c], d)}**" for c in ordem) + " |")
        return f"### {titulo}\n\n" + "\n".join(linhas) + "\n"

    ev = df[df["cenario"] == "gfs"].set_index("estacao")["eventos_12_9mm"].sum()
    txt = [
        "# Comparação de modelos fixos do Open-Meteo x estações INMET\n",
        f"Período avaliado: a partir de {INICIO_TESTE}. Eventos reais de chuva > 12,9 mm: {int(ev)} (soma das estações).\n",
        "Sem correção estatística em nenhum cenário: é o dado do modelo como sai da API.\n",
        tabela("classe_exata_pct", 1, "Acerto exato da classe da FMA (%) - maior é melhor"),
        tabela("classe_mais_menos_1_pct", 1, "Acerto com tolerância de 1 classe (%)"),
        tabela("fma_mae", 2, "Erro médio absoluto da FMA - menor é melhor"),
        tabela("ur_mae", 1, "Erro médio absoluto da UR às 13h (p.p.)"),
        tabela("pod_12_9mm_pct", 1, "Detecção de chuva > 12,9 mm (%) - maior é melhor"),
        tabela("alarmes_falsos_12_9mm_pct", 1, "Alarmes falsos de chuva > 12,9 mm (%) - menor é melhor"),
        calibrar._secao_lacunas(),
    ]
    (SAIDA / "relatorio.md").write_text("\n".join(txt), encoding="utf-8")


if __name__ == "__main__":
    main(n_estacoes=0 if "--todas" in sys.argv else 6)

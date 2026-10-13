#!/usr/bin/env python3
"""
Calibra o Open-Meteo com as estações do INMET e mede o quanto a correção melhora, em dados que o ajuste não viu.

Para cada estação (dados_estacoes/<COD>.csv):
  1. baixa do Open-Meteo (API de previsões arquivadas, o mesmo produto da rotina diária) umidade e chuva horárias no ponto da estação;
  2. converte para o dia da FMA (UR às 13h, chuva das 14h às 13h), com a mesma função da rotina diária;
  3. ajusta a correção com os dados até 31/12/2024 e testa de 01/01/2025 até o último dia, de três formas:
        bruto | corrigido com a PRÓPRIA estação | corrigido com a estação VIZINHA (teste espacial: simula um município sem estação);
  4. reajusta com todo o período e grava calibracao/parametros.json e calibracao/relatorio.md.

Uso:  python calibrar.py
"""
import json
import math
import sys
import time
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import requests

import calibracao as cal
from fma import diario_de_openmeteo

RAIZ = Path(__file__).parent
ESTACOES = RAIZ / "dados_estacoes"
SAIDA = RAIZ / "calibracao"
INICIO_MODELO = date(2022, 1, 1)      # a API de previsões arquivadas começa por volta de 2022
INICIO_TESTE = "2025-01-01"
URL_HIST = "https://historical-forecast-api.open-meteo.com/v1/forecast"


def baixar_horario(lat, lon, inicio, fim, tentativas=5):
    """Baixa em blocos de 1 ano e junta. Devolve dict no formato 'hourly' do Open-Meteo."""
    juntos = {"time": [], "relative_humidity_2m": [], "precipitation": []}
    ini = inicio
    while ini <= fim:
        fim_bloco = min(date(ini.year, 12, 31), fim)
        params = {"latitude": lat, "longitude": lon, "start_date": ini.isoformat(), "end_date": fim_bloco.isoformat(),
                  "hourly": "relative_humidity_2m,precipitation", "timezone": "America/Sao_Paulo"}
        for i in range(tentativas):
            r = requests.get(URL_HIST, params=params, timeout=120)
            if r.status_code == 200:
                h = r.json()["hourly"]
                for k in juntos:
                    juntos[k] += h[k]
                break
            corpo = r.text[:300]
            if "Daily API request limit" in corpo:
                raise RuntimeError(f"limite diário do Open-Meteo atingido: {corpo}")
            if r.status_code == 400:      # período sem dados na API (ex.: antes do início do arquivo): pula o bloco
                print(f"   AVISO: {ini}..{fim_bloco} indisponível no Open-Meteo, bloco ignorado ({corpo!r})", flush=True)
                break
            espera = 65 if r.status_code == 429 else 5 * (i + 1)
            print(f"   HTTP {r.status_code} ({corpo!r}); nova tentativa em {espera}s", flush=True)
            time.sleep(espera)
        else:
            raise RuntimeError(f"Open-Meteo falhou para {lat},{lon} em {ini}..{fim_bloco}: HTTP {r.status_code} {corpo}")
        ini = fim_bloco + timedelta(days=1)
        time.sleep(2)
    return juntos


def dist_km(a, b):
    R = 6371.0
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    dl, dp = math.radians(b[1] - a[1]), p2 - p1
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))


def carregar_obs(cod):
    d = pd.read_csv(ESTACOES / f"{cod}.csv", parse_dates=["data"]).set_index("data")
    return d[["umidade", "chuva"]]


def main(baixador=baixar_horario):
    SAIDA.mkdir(exist_ok=True)
    meta = json.loads((ESTACOES / "estacoes_meta.json").read_text(encoding="utf-8"))
    ontem = date.today() - timedelta(days=1)

    obs, mod = {}, {}
    for cod, m in meta.items():
        print(f"{cod} {m['nome']}: baixando Open-Meteo...", flush=True)
        h = baixador(m["latitude"], m["longitude"], max(INICIO_MODELO, date.fromisoformat(m["dados_desde"])), ontem)
        d = diario_de_openmeteo(h)
        d["data"] = pd.to_datetime(d["data"])
        mod[cod] = d.set_index("data")
        obs[cod] = carregar_obs(cod)
        print(f"   {len(mod[cod])} dias do modelo, {len(obs[cod])} dias da estação", flush=True)

    # --- ajuste só com o treino (antes de INICIO_TESTE)
    treino = {c: (mod[c][mod[c].index < INICIO_TESTE], obs[c][obs[c].index < INICIO_TESTE]) for c in meta}
    params_treino = {c: cal.ajustar(*treino[c]) for c in meta}

    linhas = []
    for cod in meta:
        viz = min((c for c in meta if c != cod), key=lambda c: dist_km((meta[cod]["latitude"], meta[cod]["longitude"]),
                                                                        (meta[c]["latitude"], meta[c]["longitude"])))
        dkm = dist_km((meta[cod]["latitude"], meta[cod]["longitude"]), (meta[viz]["latitude"], meta[viz]["longitude"]))
        cenarios = {
            "bruto": mod[cod],
            "corrigido_propria": cal.aplicar(mod[cod], params_treino[cod]),
            "corrigido_vizinha": cal.aplicar(mod[cod], params_treino[viz]),
        }
        for nome, serie in cenarios.items():
            m = cal.metricas(serie, obs[cod], INICIO_TESTE)
            m.update(estacao=cod, cenario=nome, vizinha=viz if nome == "corrigido_vizinha" else "", dist_vizinha_km=round(dkm, 1) if nome == "corrigido_vizinha" else None)
            linhas.append(m)
    df = pd.DataFrame(linhas)
    df.round(2).to_csv(SAIDA / "metricas.csv", index=False)

    # --- parâmetros finais: reajusta com todo o período
    finais = {c: cal.ajustar(mod[c], obs[c]) for c in meta}
    (SAIDA / "parametros.json").write_text(json.dumps(finais), encoding="utf-8")

    escrever_relatorio(df, meta)
    print("Pronto: calibracao/relatorio.md, metricas.csv e parametros.json")


def _fmt(x, d=1):
    return "-" if pd.isna(x) else f"{x:.{d}f}".replace(".", ",")


def escrever_relatorio(df, meta):
    def tabela(col, d=1, titulo=""):
        piv = df.pivot(index="estacao", columns="cenario", values=col)[["bruto", "corrigido_propria", "corrigido_vizinha"]]
        w = df[df["cenario"] == "bruto"].set_index("estacao")["dias_fma"]
        linhas = ["| Estação | Bruto | Corrigido (própria estação) | Corrigido (estação vizinha) |", "|---|---|---|---|"]
        for cod, r in piv.iterrows():
            linhas.append(f"| {cod} {meta[cod]['nome']} | {_fmt(r['bruto'], d)} | {_fmt(r['corrigido_propria'], d)} | {_fmt(r['corrigido_vizinha'], d)} |")
        med = {c: (piv[c] * w).sum() / w[piv[c].notna()].sum() for c in piv.columns}
        linhas.append(f"| **Média (ponderada por dias)** | **{_fmt(med['bruto'], d)}** | **{_fmt(med['corrigido_propria'], d)}** | **{_fmt(med['corrigido_vizinha'], d)}** |")
        return f"### {titulo}\n\n" + "\n".join(linhas) + "\n"

    ev = df[df["cenario"] == "bruto"].set_index("estacao")["eventos_12_9mm"].sum()
    txt = [
        "# Relatório de calibração (Open-Meteo x estações INMET)\n",
        f"Teste em dados que o ajuste não viu: de {INICIO_TESTE} até o último dia disponível. "
        f"O ajuste usa só os dados anteriores a essa data. Eventos de chuva > 12,9 mm (que zeram a FMA) no teste: {int(ev)} (soma das estações).\n",
        "**Como ler:** *Bruto* = Open-Meteo sem correção. *Própria estação* = correção aprendida na própria estação (caso ideal). "
        "*Estação vizinha* = correção aprendida na estação mais próxima, aplicada sem olhar a estação-alvo "
        "(simula um município sem estação).\n",
        tabela("classe_exata_pct", 1, "Acerto exato da classe de perigo da FMA (%) - quanto maior, melhor"),
        tabela("classe_mais_menos_1_pct", 1, "Acerto da classe com tolerância de 1 classe (%)"),
        tabela("fma_mae", 2, "Erro médio absoluto da FMA (pontos de FMA) - quanto menor, melhor"),
        tabela("ur_vies", 1, "Viés da umidade às 13h (pontos percentuais; positivo = modelo mais úmido)"),
        tabela("ur_mae", 1, "Erro médio absoluto da umidade às 13h (pontos percentuais)"),
        tabela("chuva_vies_mm_dia", 2, "Viés da chuva de 24h (mm/dia; negativo = modelo chove menos)"),
        tabela("pod_12_9mm_pct", 1, "Detecção de chuva > 12,9 mm, que zera a FMA (% dos eventos reais que o modelo também marca)"),
        tabela("alarmes_falsos_12_9mm_pct", 1, "Alarmes falsos de chuva > 12,9 mm (% dos eventos do modelo que a estação não confirma)"),
        "\n## Limites\n",
        "- A correção ajusta a **distribuição** (viés) do modelo. Se o modelo errar o **dia** da chuva, ela não conserta.\n"
        "- Chuvas convectivas localizadas são o ponto mais frágil, e justamente uma chuva > 12,9 mm zera a FMA.\n"
        "- Dado calibrado continua sendo estimativa de modelo, não medição de estação.\n",
    ]
    (SAIDA / "relatorio.md").write_text("\n".join(txt), encoding="utf-8")


if __name__ == "__main__":
    main()

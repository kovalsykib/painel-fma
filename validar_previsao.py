#!/usr/bin/env python3
"""
Valida a PREVISÃO da FMA (ECMWF via Open-Meteo) por antecedência, contra as estações do INMET.

Para cada dia D0 do período de teste e cada horizonte h = 1, 2, 3 dias:
  1. parte da FMA "do dia" no dia D0 (calculada com o modelo, como no painel);
  2. avança dia a dia até D0+h usando, para o dia D0+j, a previsão feita j dias antes (j = 1..h),
     que é o que o painel teria na tarde de D0 (Previous Runs API do Open-Meteo: variáveis *_previous_dayK);
  3. compara a FMA prevista com a FMA da estação em D0+h (classe exata, ±1 classe, erro absoluto).
Também mede, por antecedência, a detecção da chuva > 12,9 mm (a que zera a FMA) e uma referência ingênua:
"persistência" (repetir a FMA do dia D0).

Uso:  python validar_previsao.py           (6 estações)
      python validar_previsao.py --todas
Saída: validacao_previsao.json (lido pela rotina diária: a previsão só aparece no painel se este arquivo existir),
       comparacao_modelos/previsao_relatorio.md e previsao_metricas.csv
"""
import hashlib
import json
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import requests

import calibracao as cal
from fma import MODELO_PADRAO, diario_de_openmeteo, passo_fma

RAIZ = Path(__file__).parent
ESTACOES = RAIZ / "dados_estacoes"
SAIDA = RAIZ / "comparacao_modelos"
CACHE = SAIDA / "previsao_cache"
URL = "https://previous-runs-api.open-meteo.com/v1/forecast"
INICIO_DADOS = date(2024, 10, 1)       # aquecimento da FMA
INICIO_TESTE = "2025-01-01"
HORIZONTES = (1, 2, 3)
LEADS = (0, 1, 2, 3)                    # 0 = valor "do dia" (análise/curto prazo); k = previsão feita k dias antes
DIAS_BLOCO = 30
ORCAMENTO_MIN = 120
INICIO_EXEC = time.time()
NAO_BAIXADOS = []


def nomes(lead):
    suf = "" if lead == 0 else f"_previous_day{lead}"
    return f"relative_humidity_2m{suf}", f"precipitation{suf}"


def baixar_bloco(lat, lon, ini, fim, tentativas=4):
    chave = hashlib.md5(f"prev|{lat:.4f}|{lon:.4f}|{MODELO_PADRAO}|{ini}|{fim}".encode()).hexdigest()[:16]
    arq = CACHE / f"{chave}.json"
    if arq.exists():
        return json.loads(arq.read_text())
    if time.time() - INICIO_EXEC > ORCAMENTO_MIN * 60:
        NAO_BAIXADOS.append(f"({lat}, {lon}) {ini}..{fim}: tempo esgotado, fica para a próxima rodada")
        return None
    hourly = ",".join(n for k in LEADS for n in nomes(k))
    params = {"latitude": lat, "longitude": lon, "start_date": ini.isoformat(), "end_date": fim.isoformat(),
              "hourly": hourly, "models": MODELO_PADRAO, "timezone": "America/Sao_Paulo"}
    motivo = ""
    for i in range(tentativas):
        try:
            r = requests.get(URL, params=params, timeout=(20, 240))
            if r.status_code == 200:
                h = r.json()["hourly"]
                out = {"time": h["time"]}
                for k in LEADS:
                    for n in nomes(k):
                        v = h.get(n, h.get(f"{n}_{MODELO_PADRAO}"))
                        if v is None:
                            raise KeyError(f"variável {n} ausente; vieram: {list(h)[:12]}")
                        out[n] = [None if x is None else round(x, 1) for x in v]
                CACHE.mkdir(parents=True, exist_ok=True)
                arq.write_text(json.dumps(out, separators=(",", ":")))
                return out
            motivo = f"HTTP {r.status_code} {r.text[:200]!r}"
            if r.status_code == 400:
                break
        except (requests.exceptions.RequestException, ValueError, KeyError) as e:
            motivo = f"{type(e).__name__}: {str(e)[:200]}"
        print(f"   {ini}..{fim}: {motivo}; tentativa {i + 1}/{tentativas}", flush=True)
        time.sleep(65 if "429" in motivo else 5 * (i + 1))
    NAO_BAIXADOS.append(f"({lat}, {lon}) {ini}..{fim}: {motivo}")
    return None


def baixar_blocos(lat, lon, ini, fim):
    juntos = {"time": []}
    for k in LEADS:
        for n in nomes(k):
            juntos[n] = []
    while ini <= fim:
        f = min(ini + timedelta(days=DIAS_BLOCO - 1), fim)
        h = baixar_bloco(lat, lon, ini, f)
        if h:
            for k in juntos:
                juntos[k] += h[k]
        ini = f + timedelta(days=1)
        time.sleep(0.5)
    return juntos


def series_por_lead(h):
    """{lead: DataFrame diário (umidade às 13h, chuva 14h-13h) indexado por data}."""
    out = {}
    for k in LEADS:
        un, cn = nomes(k)
        d = diario_de_openmeteo({"time": h["time"], "relative_humidity_2m": h[un], "precipitation": h[cn]})
        d["data"] = pd.to_datetime(d["data"])
        out[k] = d.set_index("data")
    return out


def fma_corrente(s0):
    """FMA diária pelo valor 'do dia' (lead 0): é o ponto de partida da previsão. Devolve (série FMA, série do acumulado)."""
    idx = pd.date_range(s0.index.min(), s0.index.max())
    s0 = s0.reindex(idx)
    acc, vals, accs = 0.0, [], []
    for u, c in zip(s0["umidade"], s0["chuva"]):
        acc, v = passo_fma(acc, u, c)
        vals.append(v)
        accs.append(acc)
    return pd.Series(vals, index=idx), pd.Series(accs, index=idx)


def avaliar_estacao(s, obs):
    """Linhas de resultado (uma por dia D0 x horizonte) para uma estação."""
    s0 = s[0]
    fma0, acc0 = fma_corrente(s0)
    obs_fma = cal.serie_fma(obs)["fma"]
    linhas = []
    for d0 in acc0.index:
        if d0 < pd.Timestamp(INICIO_TESTE) - timedelta(days=1) or pd.isna(fma0.get(d0)):
            continue
        acc = acc0[d0]
        for h in HORIZONTES:
            alvo = d0 + timedelta(days=h)
            # dia d0+j vem da previsão feita j dias antes
            ok = True
            a = acc
            for j in range(1, h + 1):
                dj = d0 + timedelta(days=j)
                sj = s[j]
                if dj not in sj.index:
                    ok = False
                    break
                a, v = passo_fma(a, sj.at[dj, "umidade"], sj.at[dj, "chuva"])
            if not ok or pd.isna(v) or alvo not in obs_fma.index or pd.isna(obs_fma[alvo]) or alvo < pd.Timestamp(INICIO_TESTE):
                continue
            ch_obs = obs["chuva"].get(alvo)
            ch_prev = s[h]["chuva"].get(alvo)
            linhas.append({"d0": d0, "h": h, "alvo": alvo, "prev": v, "pers": fma0[d0], "obs": obs_fma[alvo],
                           "chuva_prev": ch_prev, "chuva_obs": ch_obs})
    return pd.DataFrame(linhas)


def classe(v):
    from fma import classificar
    return classificar(v)


def resumir(df):
    """Métricas por horizonte a partir das linhas (todas as estações)."""
    ordem = {c: i for i, c in enumerate(cal.CLASSES_ORDEM)}
    res = {}
    for h, g in df.groupby("h"):
        co = g["obs"].map(classe).map(ordem)
        cp = g["prev"].map(classe).map(ordem)
        cps = g["pers"].map(classe).map(ordem)
        ch = g.dropna(subset=["chuva_prev", "chuva_obs"])
        ev_o, ev_p = ch["chuva_obs"] > 12.9, ch["chuva_prev"] > 12.9
        tp, fn, fp = int((ev_o & ev_p).sum()), int((ev_o & ~ev_p).sum()), int((~ev_o & ev_p).sum())
        res[int(h)] = {
            "dias": int(len(g)),
            "classe_exata_pct": round(float((cp == co).mean() * 100), 1),
            "classe_mais_menos_1_pct": round(float(((cp - co).abs() <= 1).mean() * 100), 1),
            "fma_mae": round(float((g["prev"] - g["obs"]).abs().mean()), 2),
            "persistencia_classe_exata_pct": round(float((cps == co).mean() * 100), 1),
            "persistencia_classe_mais_menos_1_pct": round(float(((cps - co).abs() <= 1).mean() * 100), 1),
            "persistencia_fma_mae": round(float((g["pers"] - g["obs"]).abs().mean()), 2),
            "eventos_12_9mm": int(ev_o.sum()),
            "pod_12_9mm_pct": round(100 * tp / (tp + fn), 1) if (tp + fn) else None,
            "alarmes_falsos_12_9mm_pct": round(100 * fp / (tp + fp), 1) if (tp + fp) else None,
        }
    return res


def main(baixador=baixar_blocos, n_estacoes=6):
    SAIDA.mkdir(exist_ok=True)
    meta = json.loads((ESTACOES / "estacoes_meta.json").read_text(encoding="utf-8"))
    cods = sorted(meta)
    if n_estacoes and len(cods) > n_estacoes:
        passo = len(cods) / n_estacoes
        cods = [cods[int(i * passo)] for i in range(n_estacoes)]
    ontem = date.today() - timedelta(days=1)

    todas, por_est = [], {}
    for cod in cods:
        m = meta[cod]
        ini = max(INICIO_DADOS, date.fromisoformat(m["dados_desde"]))
        print(f"{cod} {m['nome']}", flush=True)
        h = baixador(m["latitude"], m["longitude"], ini, ontem)
        s = series_por_lead(h)
        obs = pd.read_csv(ESTACOES / f"{cod}.csv", parse_dates=["data"]).set_index("data")[["umidade", "chuva"]]
        obs = obs[obs.index >= pd.Timestamp(ini)]
        df = avaliar_estacao(s, obs)
        if len(df) < 90:
            NAO_BAIXADOS.append(f"{cod} {m['nome']}: só {len(df)} avaliações (dados incompletos); fora desta rodada")
            print(f"   poucas avaliações ({len(df)}), estação ignorada nesta rodada", flush=True)
            continue
        df["estacao"] = cod
        todas.append(df)
        por_est[cod] = resumir(df)
        print(f"   {len(df)} avaliações", flush=True)

    if not todas:
        print("Nenhuma estação com dados suficientes ainda; rode de novo para continuar o download.")
        return
    tudo = pd.concat(todas, ignore_index=True)
    geral = resumir(tudo)
    tudo.to_csv(SAIDA / "previsao_metricas.csv", index=False, float_format="%.2f")
    saida = {"gerado_em": datetime.now().strftime("%d/%m/%Y"), "modelo": MODELO_PADRAO, "periodo_teste": f"{INICIO_TESTE} em diante",
             "estacoes": sorted(por_est), "horizontes": {str(h): v for h, v in geral.items()}}
    (RAIZ / "validacao_previsao.json").write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
    escrever_relatorio(geral, por_est, meta)
    print("Pronto: validacao_previsao.json e comparacao_modelos/previsao_relatorio.md")


def _f(x, d=1):
    return "-" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.{d}f}".replace(".", ",")


def escrever_relatorio(geral, por_est, meta):
    t = ["# Validação da previsão da FMA por antecedência (ECMWF x estações INMET)\n",
         "Teste de " + INICIO_TESTE + " em diante. Estações: " + ", ".join(c + " " + meta[c]["nome"] for c in sorted(por_est)) + ".\n",
         "A previsão para D+h parte da FMA do dia D e avança com a previsão feita j dias antes para cada dia D+j "
         "(Previous Runs API; para cada dia, toda a janela de chuva usa a previsão de j dias antes, o que é um pouco mais pessimista "
         "que o painel real). *Persistência* = repetir a FMA de hoje (referência ingênua).\n",
         "### Todas as estações juntas\n",
         "| Antecedência | Dias avaliados | Classe exata (%) | ±1 classe (%) | Erro médio da FMA | Persistência: classe exata (%) | Persistência: ±1 classe (%) | Persistência: erro médio | Detecção chuva > 12,9 mm (%) | Alarmes falsos (%) |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for h, r in sorted(geral.items()):
        t.append(f"| D+{h} | {r['dias']} | {_f(r['classe_exata_pct'])} | {_f(r['classe_mais_menos_1_pct'])} | {_f(r['fma_mae'], 2)} | "
                 f"{_f(r['persistencia_classe_exata_pct'])} | {_f(r['persistencia_classe_mais_menos_1_pct'])} | {_f(r['persistencia_fma_mae'], 2)} | "
                 f"{_f(r['pod_12_9mm_pct'])} | {_f(r['alarmes_falsos_12_9mm_pct'])} |")
    t.append("\n### Por estação (classe exata %, ±1 classe %, erro médio da FMA)\n")
    t.append("| Estação | " + " | ".join(f"D+{h}" for h in HORIZONTES) + " |")
    t.append("|---|" + "---|" * len(HORIZONTES))
    for c in sorted(por_est):
        t.append(f"| {c} {meta[c]['nome']} | " + " | ".join(
            f"{_f(por_est[c][h]['classe_exata_pct'])} / {_f(por_est[c][h]['classe_mais_menos_1_pct'])} / {_f(por_est[c][h]['fma_mae'], 2)}"
            if h in por_est[c] else "-" for h in HORIZONTES) + " |")
    if NAO_BAIXADOS:
        t.append("\n## Download incompleto\n\nRodar de novo completa (o que já veio fica guardado):\n")
        t += [f"- {x}" for x in NAO_BAIXADOS]
    (SAIDA / "previsao_relatorio.md").write_text("\n".join(t) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main(n_estacoes=0 if "--todas" in sys.argv else 6)

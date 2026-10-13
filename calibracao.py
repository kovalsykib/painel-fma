"""
Calibração (mapeamento de quantis) dos dados do modelo contra estações do INMET.

Ideia: para cada estação, compara a distribuição da umidade das 13h e da chuva de 24h do modelo com a medida pela estação
no mesmo período e aprende uma função que "corrige" o modelo, por estação do ano (seca: abr-set; úmida: out-mar).
Corrige a distribuição (viés), não a data exata em que a chuva cai: se o modelo errar o dia da chuva, a calibração não conserta.
"""
import numpy as np
import pandas as pd

from fma import calcular_fma

CLASSES_ORDEM = ["Nulo", "Pequeno", "Médio", "Alto", "Muito alto"]
ESTACOES_ANO = {"seca": [4, 5, 6, 7, 8, 9], "umida": [10, 11, 12, 1, 2, 3]}
PROBS_UR = np.round(np.arange(0.01, 1.0, 0.02), 4)
PROBS_CHUVA = np.unique(np.round(np.concatenate([np.arange(0.0, 0.9, 0.02), np.arange(0.9, 0.99, 0.01),
                                                 [0.99, 0.995, 0.999, 1.0]]), 4))
MIN_PARES_ESTACAO_ANO = 250


# ------------------------------------------------------------------ ajuste
def _ajustar_qm(modelo, obs, probs):
    pares = pd.concat([modelo.rename("m"), obs.rename("o")], axis=1).dropna()
    return {"probs": probs.tolist(),
            "qm": np.quantile(pares["m"], probs).round(3).tolist(),
            "qo": np.quantile(pares["o"], probs).round(3).tolist(),
            "n": int(len(pares))}


def ajustar(modelo_df, obs_df):
    """modelo_df e obs_df: indexados por data, com colunas 'umidade' e 'chuva'. Devolve os parâmetros da correção."""
    params = {"umidade": {}, "chuva": {}}
    for var, probs in (("umidade", PROBS_UR), ("chuva", PROBS_CHUVA)):
        params[var]["todas"] = _ajustar_qm(modelo_df[var], obs_df[var], probs)
        for nome, meses in ESTACOES_ANO.items():
            m = modelo_df[var][modelo_df.index.month.isin(meses)]
            o = obs_df[var][obs_df.index.month.isin(meses)]
            p = _ajustar_qm(m, o, probs)
            if p["n"] >= MIN_PARES_ESTACAO_ANO:
                params[var][nome] = p
    return params


# ------------------------------------------------------------------ aplicação
def _mapear(x, p, tipo):
    qm = np.array(p["qm"], float)
    qo = np.array(p["qo"], float)
    um, inv = np.unique(qm, return_inverse=True)            # empates (muitos zeros de chuva): média dos qo
    uo = np.bincount(inv, weights=qo) / np.bincount(inv)
    y = np.interp(x, um, uo)
    if tipo == "razao":                                      # chuva
        r = float(np.clip(uo[-1] / um[-1], 0.5, 3.0)) if um[-1] > 0 else 1.0
        y = np.where(x > um[-1], x * r, y)
        y = np.where(y < 0.1, 0.0, y)
    else:                                                    # umidade
        y = np.where(x > um[-1], x + (uo[-1] - um[-1]), y)
        y = np.where(x < um[0], x + (uo[0] - um[0]), y)
        y = np.clip(y, 5, 100)
    return np.where(np.isnan(x), np.nan, y)


def aplicar(df, params):
    """df indexado por data (DatetimeIndex) com 'umidade' e 'chuva' do modelo. Devolve df corrigido."""
    out = df.copy()
    meses = df.index.month
    for var, tipo in (("umidade", "soma"), ("chuva", "razao")):
        res = np.full(len(df), np.nan)
        for nome, ms in ESTACOES_ANO.items():
            p = params[var].get(nome) or params[var]["todas"]
            m = np.isin(meses, ms)
            if m.any():
                res[m] = _mapear(df[var].to_numpy(float)[m], p, tipo)
        out[var] = res
    return out


# ------------------------------------------------------------------ avaliação
def serie_fma(df):
    """FMA de uma série diária contínua (df indexado por data com 'umidade' e 'chuva')."""
    full = df.reindex(pd.date_range(df.index.min(), df.index.max(), name="data"))
    r = calcular_fma(full.reset_index())
    return r.set_index("data")[["fma", "classe"]]


def metricas(modelo_df, obs_df, inicio_teste):
    """Compara um modelo (bruto ou corrigido) com a estação, só nos dias >= inicio_teste."""
    t = pd.Timestamp(inicio_teste)
    fm, fo = serie_fma(modelo_df), serie_fma(obs_df)
    j = fm.join(fo, lsuffix="_m", rsuffix="_o", how="inner")
    j = j[(j.index >= t) & j["fma_m"].notna() & j["fma_o"].notna()]
    ordem = {c: i for i, c in enumerate(CLASSES_ORDEM)}
    dif_cl = (j["classe_m"].map(ordem) - j["classe_o"].map(ordem)).abs()

    d = modelo_df.join(obs_df, lsuffix="_m", rsuffix="_o", how="inner")
    d = d[d.index >= t]
    ur = d[["umidade_m", "umidade_o"]].dropna()
    ch = d[["chuva_m", "chuva_o"]].dropna()
    ev_o, ev_m = ch["chuva_o"] > 12.9, ch["chuva_m"] > 12.9
    tp, fn, fp = int((ev_o & ev_m).sum()), int((ev_o & ~ev_m).sum()), int((~ev_o & ev_m).sum())
    return {
        "dias_fma": int(len(j)),
        "fma_mae": float((j["fma_m"] - j["fma_o"]).abs().mean()) if len(j) else np.nan,
        "classe_exata_pct": float((dif_cl == 0).mean() * 100) if len(j) else np.nan,
        "classe_mais_menos_1_pct": float((dif_cl <= 1).mean() * 100) if len(j) else np.nan,
        "ur_vies": float((ur["umidade_m"] - ur["umidade_o"]).mean()) if len(ur) else np.nan,
        "ur_mae": float((ur["umidade_m"] - ur["umidade_o"]).abs().mean()) if len(ur) else np.nan,
        "chuva_vies_mm_dia": float((ch["chuva_m"] - ch["chuva_o"]).mean()) if len(ch) else np.nan,
        "eventos_12_9mm": int(ev_o.sum()),
        "pod_12_9mm_pct": float(100 * tp / (tp + fn)) if (tp + fn) else np.nan,
        "alarmes_falsos_12_9mm_pct": float(100 * fp / (tp + fp)) if (tp + fp) else np.nan,
    }

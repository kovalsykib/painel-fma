#!/usr/bin/env python3
"""
Teste de ACESSO ao IMERG (NASA/GPM) a partir do GitHub Actions. Não calcula FMA ainda: só responde 4 perguntas
  1. O GitHub consegue listar os arquivos do IMERG (Early, Late e Final)?
  2. O login do Earthdata funciona?
  3. Dá para ler a chuva de UM ponto (Seropédica) sem baixar o arquivo global inteiro? Quanto tempo leva?
  4. Qual é o atraso de cada versão (quanto tempo depois da chuva o dado aparece)?
Saída: imerg/teste_acesso.md  (mesmo se algo falhar, com o erro, para você colar aqui na conversa).
"""
import os
import time
import traceback
from datetime import datetime, timedelta, timezone
from pathlib import Path

SAIDA = Path(__file__).parent / "imerg"
SAIDA.mkdir(exist_ok=True)
LAT, LON = -22.7578, -43.6847        # estação A601 Seropédica
PRODUTOS = {"Early (HHE)": "GPM_3IMERGHHE", "Late (HHL)": "GPM_3IMERGHHL", "Final (HH)": "GPM_3IMERGHH"}
linhas = ["# Teste de acesso ao IMERG a partir do GitHub\n", f"Rodado em {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC.\n"]


def log(txt=""):
    print(txt, flush=True)
    linhas.append(txt + "\n")


def fim_granulo(g):
    try:
        return datetime.fromisoformat(g["umm"]["TemporalExtent"]["RangeDateTime"]["EndingDateTime"].replace("Z", "+00:00"))
    except Exception:
        return None


def main():
    import earthaccess

    agora = datetime.now(timezone.utc)
    log("## 1. Listagem dos arquivos (CMR, sem login)\n")
    achados = {}
    for nome, short in PRODUTOS.items():
        try:
            if "Final" in nome:
                ini, fim = agora - timedelta(days=200), agora - timedelta(days=198)
            else:
                ini, fim = agora - timedelta(days=3), agora
            gs = earthaccess.search_data(short_name=short, version="07", temporal=(ini.strftime("%Y-%m-%dT%H:%M:%S"), fim.strftime("%Y-%m-%dT%H:%M:%S")), count=400)
            achados[nome] = gs
            fins = [f for f in (fim_granulo(g) for g in gs) if f]
            msg = f"- **{nome}** ({short}): {len(gs)} arquivos encontrados"
            if fins and "Final" not in nome:
                ult = max(fins)
                msg += f"; o mais novo termina em {ult:%Y-%m-%d %H:%M} UTC, **{(agora - ult).total_seconds() / 3600:.1f} h antes de agora**"
            log(msg)
            if gs:
                log(f"  - exemplo: `{gs[0].data_links()[0].split('/')[-1]}`")
        except Exception:
            log(f"- **{nome}**: FALHOU\n```\n{traceback.format_exc()[-900:]}\n```")

    log("\n## 2. Login no Earthdata\n")
    try:
        if not (os.environ.get("EARTHDATA_USERNAME") and os.environ.get("EARTHDATA_PASSWORD")) and not os.environ.get("EARTHDATA_TOKEN"):
            raise RuntimeError("Os segredos EARTHDATA_USERNAME e EARTHDATA_PASSWORD não chegaram ao programa (confira Settings > Secrets and variables > Actions).")
        auth = earthaccess.login(strategy="environment")
        log(f"- Login: {'OK' if auth.authenticated else 'NÃO autenticou'}")
        if not auth.authenticated:
            return
    except Exception:
        log(f"- Login FALHOU\n```\n{traceback.format_exc()[-900:]}\n```")
        return

    log("\n## 3. Leitura da chuva em UM ponto (Seropédica), sem baixar o arquivo inteiro\n")
    import xarray as xr
    for nome, gs in achados.items():
        if not gs:
            continue
        try:
            amostra = gs[:5]
            t0 = time.time()
            arquivos = earthaccess.open(amostra)
            tempos, valores = [], []
            for g, f in zip(amostra, arquivos):
                t1 = time.time()
                with xr.open_dataset(f, group="Grid", engine="h5netcdf") as ds:
                    if "precipitation" not in ds:
                        raise KeyError(f"variável 'precipitation' não existe; variáveis: {list(ds.data_vars)[:12]}")
                    v = ds["precipitation"].sel(lat=LAT, lon=LON, method="nearest").isel(time=0).values
                    valores.append(float(v))
                tempos.append(time.time() - t1)
            log(f"- **{nome}**: {len(amostra)} arquivos lidos em {time.time() - t0:.1f} s no total "
                f"(média {sum(tempos) / len(tempos):.1f} s por arquivo); chuva (mm/h) no ponto: {[round(x, 2) for x in valores]}")
        except Exception:
            log(f"- **{nome}**: leitura FALHOU\n```\n{traceback.format_exc()[-1200:]}\n```")

    log("\n## Como ler\n")
    log("- Se a seção 1 listou arquivos mas a 2 ou a 3 falhou, o problema é login ou autorização no Earthdata (veja o passo a passo).")
    log("- O tempo médio por arquivo diz se dá para baixar um ano inteiro de meia em meia hora (17.520 arquivos por ano).")
    log("- O atraso do Early/Late diz se o dado das 13h já existe quando o painel roda.")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        log(f"ERRO GERAL\n```\n{traceback.format_exc()[-1500:]}\n```")
    finally:
        (SAIDA / "teste_acesso.md").write_text("\n".join(linhas), encoding="utf-8")

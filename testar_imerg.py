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


def listar_cmr(short, ini, fim, n=50, tentativas=4):
    """Lista arquivos direto na API do CMR (sem login). Devolve lista de dicts {url, fim}. Tenta de novo se o CMR falhar."""
    import requests
    params = {"short_name": short, "version": "07", "temporal[]": f"{ini:%Y-%m-%dT%H:%M:%SZ},{fim:%Y-%m-%dT%H:%M:%SZ}",
              "page_size": n, "sort_key": "-start_date"}
    ultimo = ""
    for i in range(tentativas):
        r = requests.get("https://cmr.earthdata.nasa.gov/search/granules.json", params=params, timeout=60)
        if r.status_code == 200:
            saida = []
            for e in r.json()["feed"]["entry"]:
                url = next((l["href"] for l in e.get("links", []) if l.get("rel", "").endswith("/data#") and l["href"].startswith("https")), None)
                fim_e = datetime.fromisoformat(e["time_end"].replace("Z", "+00:00")) if e.get("time_end") else None
                saida.append({"url": url, "fim": fim_e})
            return saida
        ultimo = f"HTTP {r.status_code}: {r.text[:300]}"
        time.sleep(20 * (i + 1))
    # diagnóstico: a mesma consulta sem o filtro de versão, para saber se o problema é a versão
    r = requests.get("https://cmr.earthdata.nasa.gov/search/granules.json", params={k: v for k, v in params.items() if k != "version"}, timeout=60)
    raise RuntimeError(f"CMR recusou {tentativas} vezes. Último erro: {ultimo}. Sem filtro de versão: HTTP {r.status_code} {r.text[:200]}")


def main():
    import earthaccess

    agora = datetime.now(timezone.utc)
    log("## 1. Listagem dos arquivos (CMR da NASA, sem login)\n")
    achados = {}
    for nome, short in PRODUTOS.items():
        try:
            if "Final" in nome:
                ini, fim = agora - timedelta(days=200), agora - timedelta(days=198)
            else:
                ini, fim = agora - timedelta(days=3), agora
            gs = listar_cmr(short, ini, fim)
            achados[nome] = gs
            fins = [g["fim"] for g in gs if g["fim"]]
            msg = f"- **{nome}** ({short}): {len(gs)} arquivos listados (máx. 50 por consulta)"
            if fins and "Final" not in nome:
                ult = max(fins)
                msg += f"; o mais novo termina em {ult:%Y-%m-%d %H:%M} UTC, **{(agora - ult).total_seconds() / 3600:.1f} h antes de agora**"
            log(msg)
            if gs and gs[0]["url"]:
                log(f"  - exemplo: `{gs[0]['url'].split('/')[-1]}`")
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
            amostra = [g["url"] for g in gs[:5] if g["url"]]
            t0 = time.time()
            arquivos = earthaccess.open(amostra)
            tempos, valores = [], []
            for f in arquivos:
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

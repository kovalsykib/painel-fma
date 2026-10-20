# Teste de acesso ao IMERG a partir do GitHub

Rodado em 2026-10-20 11:37 UTC.

## 1. Listagem dos arquivos (CMR, sem login)


- **Early (HHE)**: FALHOU
```
s the direct cause of the following exception:

Traceback (most recent call last):
  File "/home/runner/work/painel-fma/painel-fma/testar_imerg.py", line 47, in main
    gs = earthaccess.search_data(short_name=short, version="07", temporal=(ini.strftime("%Y-%m-%dT%H:%M:%S"), fim.strftime("%Y-%m-%dT%H:%M:%S")), count=400)
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.12.15/x64/lib/python3.12/site-packages/earthaccess/api.py", line 276, in search_data
    granules_found = query.hits()
                     ^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.12.15/x64/lib/python3.12/site-packages/earthaccess/search.py", line 464, in hits
    raise RuntimeError(ex.response.text) from ex
RuntimeError: {"errors":["An Internal Error has occurred."]}

```

- **Late (HHL)**: FALHOU
```
s the direct cause of the following exception:

Traceback (most recent call last):
  File "/home/runner/work/painel-fma/painel-fma/testar_imerg.py", line 47, in main
    gs = earthaccess.search_data(short_name=short, version="07", temporal=(ini.strftime("%Y-%m-%dT%H:%M:%S"), fim.strftime("%Y-%m-%dT%H:%M:%S")), count=400)
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.12.15/x64/lib/python3.12/site-packages/earthaccess/api.py", line 276, in search_data
    granules_found = query.hits()
                     ^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.12.15/x64/lib/python3.12/site-packages/earthaccess/search.py", line 464, in hits
    raise RuntimeError(ex.response.text) from ex
RuntimeError: {"errors":["An Internal Error has occurred."]}

```

- **Final (HH)**: FALHOU
```
s the direct cause of the following exception:

Traceback (most recent call last):
  File "/home/runner/work/painel-fma/painel-fma/testar_imerg.py", line 47, in main
    gs = earthaccess.search_data(short_name=short, version="07", temporal=(ini.strftime("%Y-%m-%dT%H:%M:%S"), fim.strftime("%Y-%m-%dT%H:%M:%S")), count=400)
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.12.15/x64/lib/python3.12/site-packages/earthaccess/api.py", line 276, in search_data
    granules_found = query.hits()
                     ^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.12.15/x64/lib/python3.12/site-packages/earthaccess/search.py", line 464, in hits
    raise RuntimeError(ex.response.text) from ex
RuntimeError: {"errors":["An Internal Error has occurred."]}

```


## 2. Login no Earthdata


- Login: OK


## 3. Leitura da chuva em UM ponto (Seropédica), sem baixar o arquivo inteiro



## Como ler


- Se a seção 1 listou arquivos mas a 2 ou a 3 falhou, o problema é login ou autorização no Earthdata (veja o passo a passo).

- O tempo médio por arquivo diz se dá para baixar um ano inteiro de meia em meia hora (17.520 arquivos por ano).

- O atraso do Early/Late diz se o dado das 13h já existe quando o painel roda.

# Teste de acesso ao IMERG a partir do GitHub

Rodado em 2026-10-20 11:43 UTC.

## 1. Listagem dos arquivos (CMR da NASA, sem login)


- **Early (HHE)**: FALHOU
```
Traceback (most recent call last):
  File "/home/runner/work/painel-fma/painel-fma/testar_imerg.py", line 62, in main
    gs = listar_cmr(short, ini, fim)
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/painel-fma/painel-fma/testar_imerg.py", line 47, in listar_cmr
    raise RuntimeError(f"CMR recusou {tentativas} vezes. Último erro: {ultimo}. Sem filtro de versão: HTTP {r.status_code} {r.text[:200]}")
RuntimeError: CMR recusou 4 vezes. Último erro: HTTP 500: {"errors":["An Internal Error has occurred."]}. Sem filtro de versão: HTTP 500 {"errors":["An Internal Error has occurred."]}

```

- **Late (HHL)**: FALHOU
```
Traceback (most recent call last):
  File "/home/runner/work/painel-fma/painel-fma/testar_imerg.py", line 62, in main
    gs = listar_cmr(short, ini, fim)
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/painel-fma/painel-fma/testar_imerg.py", line 47, in listar_cmr
    raise RuntimeError(f"CMR recusou {tentativas} vezes. Último erro: {ultimo}. Sem filtro de versão: HTTP {r.status_code} {r.text[:200]}")
RuntimeError: CMR recusou 4 vezes. Último erro: HTTP 500: {"errors":["An Internal Error has occurred."]}. Sem filtro de versão: HTTP 500 {"errors":["An Internal Error has occurred."]}

```

- **Final (HH)**: FALHOU
```
Traceback (most recent call last):
  File "/home/runner/work/painel-fma/painel-fma/testar_imerg.py", line 62, in main
    gs = listar_cmr(short, ini, fim)
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/painel-fma/painel-fma/testar_imerg.py", line 47, in listar_cmr
    raise RuntimeError(f"CMR recusou {tentativas} vezes. Último erro: {ultimo}. Sem filtro de versão: HTTP {r.status_code} {r.text[:200]}")
RuntimeError: CMR recusou 4 vezes. Último erro: HTTP 500: {"errors":["An Internal Error has occurred."]}. Sem filtro de versão: HTTP 500 {"errors":["An Internal Error has occurred."]}

```


## 2. Login no Earthdata


- Login: OK


## 3. Leitura da chuva em UM ponto (Seropédica), sem baixar o arquivo inteiro



## Como ler


- Se a seção 1 listou arquivos mas a 2 ou a 3 falhou, o problema é login ou autorização no Earthdata (veja o passo a passo).

- O tempo médio por arquivo diz se dá para baixar um ano inteiro de meia em meia hora (17.520 arquivos por ano).

- O atraso do Early/Late diz se o dado das 13h já existe quando o painel roda.

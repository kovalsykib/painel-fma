# Painel FMA (Fórmula de Monte Alegre) - 15 municípios do PMIF

Todo dia o programa baixa umidade e chuva horárias do modelo **ECMWF IFS 0,25°** (via Open-Meteo, modelo fixo) no ponto de
cálculo de cada um dos 15 municípios, calcula a FMA e atualiza um painel web com **mapa, tabela e gráfico**.

**Por que ECMWF:** em teste com 6 estações do INMET (jan/2025 a out/2026), foi o melhor modelo isolado (erro médio da FMA 7,7;
classe exata em 59,5% dos dias; 91,8% dentro de 1 classe; detecta 46% das chuvas > 12,9 mm). Resultados completos em
`comparacao_modelos/relatorio.md`. Dado de modelo é estimativa, não medição: o painel traz esse aviso.

## Arquivos

| Arquivo | Para que serve |
|---|---|
| `fma.py` | Cálculo da FMA, classes de perigo e download/conversão dos dados do INMET |
| `atualizar.py` | Rotina diária: baixa, atualiza o histórico, recalcula e gera o painel |
| `municipios.json` | Os 15 municípios: contorno (IBGE), código IBGE e ponto de cálculo (gerado por `preparar_municipios.py`) |
| `comparar_modelos.py` | Teste que comparou GFS, ICON e ECMWF com as estações do INMET |
| `painel_template.html` | Modelo do painel (o `atualizar.py` preenche com os dados) |
| `dados/` | Histórico guardado (`<código IBGE>_diario.csv` = entradas; `<código IBGE>_fma.csv` = resultado) |
| `docs/` | Painel pronto (`index.html`) e `dados.json` |
| `.github/workflows/fma.yml` | Agendamento automático no GitHub (14h30 e 17h, horário de Brasília) |

## Testar no seu computador

```
pip install -r requirements.txt
python atualizar.py
```

Depois abra `docs/index.html` no navegador. Na primeira vez ele baixa 90 dias para "aquecer" o acumulado da FMA.

## Colocar para rodar sozinho (GitHub, gratuito)

1. Crie um repositório no GitHub e envie todos os arquivos desta pasta (inclusive a pasta `.github`).
2. Em **Settings > Pages**, escolha *Deploy from a branch*, branch `main`, pasta `/docs`.
3. Em **Actions > Atualizar FMA**, clique em **Run workflow** para a primeira execução.
4. O painel fica em `https://SEU-USUARIO.github.io/NOME-DO-REPOSITORIO/` e atualiza todo dia.

## Pontos de atenção

- **Janela de chuva:** das 14h do dia anterior às 13h do dia do cálculo (horário de Brasília). A UR é a das 13h.
  O INMET fornece as horas em UTC, por isso o código usa 16h UTC (`HORA_UTC_13H_LOCAL` em `fma.py`).
- **Dados faltantes:** dia sem umidade às 13h aparece como "Sem dado" e o acumulado não avança.
  Dia com chuva ausente é calculado como 0 mm e fica sinalizado na coluna `aviso` do CSV de resultados.
  Se na primeira execução real aparecer erro de coluna, o erro lista as colunas recebidas e o ajuste é pontual em `diarizar()`.
- A FMA acumula, então o resultado depende do histórico. Não apague a pasta `dados/` sem necessidade.

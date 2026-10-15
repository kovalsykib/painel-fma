# Painel FMA (Fórmula de Monte Alegre) - 15 municípios do PMIF

Todo dia o programa baixa umidade e chuva horárias do modelo **ECMWF IFS 0,25°** (via Open-Meteo, modelo fixo) no ponto de
cálculo de cada um dos 15 municípios, calcula a FMA e atualiza um painel web com **mapa, tabela e gráfico**.

**Por que ECMWF:** em teste com 6 estações do INMET (jan/2025 a out/2026), foi o melhor modelo isolado (erro médio da FMA 7,7;
classe exata em 59,5% dos dias; 91,8% dentro de 1 classe; detecta 46% das chuvas > 12,9 mm). Resultados completos em
`comparacao_modelos/relatorio.md`. Dado de modelo é estimativa, não medição: o painel traz esse aviso.

## Previsão de 1 a 3 dias

A previsão usa o mesmo modelo (ECMWF): a FMA do último dia observado é continuada com a umidade (13h) e a chuva previstas.
Ela **só aparece no painel depois que a validação rodar** e gravar `validacao_previsao.json` na raiz do repositório:

1. **Actions > Validar previsão da FMA (1 a 3 dias) > Run workflow.** Compara a previsão por antecedência com 6 estações do INMET
   (Previous Runs API do Open-Meteo) e grava `validacao_previsao.json` e `comparacao_modelos/previsao_relatorio.md`.
   Se o relatório trouxer a seção "Download incompleto", rode de novo (o que já veio fica guardado).
2. **Actions > Atualizar FMA > Run workflow.** O painel passa a mostrar os próximos 3 dias (hachurados), com as taxas de acerto por antecedência.

Para desligar a previsão, apague `validacao_previsao.json`.

## Arquivos

| Arquivo | Para que serve |
|---|---|
| `fma.py` | Cálculo da FMA, classes de perigo e download/conversão dos dados do INMET |
| `atualizar.py` | Rotina diária: baixa, atualiza o histórico, recalcula e gera o painel |
| `municipios.json` | Os 15 municípios: contorno (IBGE), código IBGE e ponto de cálculo (gerado por `preparar_municipios.py`) |
| `validar_previsao.py` | Teste que mede o erro da previsão (1 a 3 dias) contra as estações; liga a previsão no painel |
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

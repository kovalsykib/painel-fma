# Painel FMA (Fórmula de Monte Alegre)

Protótipo com a estação INMET **A601 (Seropédica)**. Todo dia o programa baixa os dados do INMET, calcula a FMA
e atualiza um painel web.

## Arquivos

| Arquivo | Para que serve |
|---|---|
| `fma.py` | Cálculo da FMA, classes de perigo e download/conversão dos dados do INMET |
| `atualizar.py` | Rotina diária: baixa, atualiza o histórico, recalcula e gera o painel |
| `estacoes.json` | Lista de estações (para incluir outras, basta acrescentar código, nome e município) |
| `painel_template.html` | Modelo do painel (o `atualizar.py` preenche com os dados) |
| `dados/` | Histórico guardado (`<estação>_diario.csv` = entradas; `<estação>_fma.csv` = resultado) |
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
- **API do INMET:** o formato foi escrito conforme a documentação pública e testado só com dados simulados.
  Se na primeira execução real aparecer erro de coluna, o erro lista as colunas recebidas e o ajuste é pontual em `diarizar()`.
- A FMA acumula, então o resultado depende do histórico. Não apague a pasta `dados/` sem necessidade.

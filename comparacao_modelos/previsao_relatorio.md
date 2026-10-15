# Validação da previsão da FMA por antecedência (ECMWF x estações INMET)

Teste de 2025-01-01 em diante. Estações: A601 Seropedica-Ecologia Agricola, A602 Rio De Janeiro-Marambaia, A609 Resende, A621 Rio De Janeiro - Vila Militar, A626 Rio Claro, A636 Rio De Janeiro - Jacarepagua.

A previsão para D+h parte da FMA do dia D e avança com a previsão feita j dias antes para cada dia D+j (Previous Runs API; para cada dia, toda a janela de chuva usa a previsão de j dias antes, o que é um pouco mais pessimista que o painel real). *Persistência* = repetir a FMA de hoje (referência ingênua).

### Todas as estações juntas

| Antecedência | Dias avaliados | Classe exata (%) | ±1 classe (%) | Erro médio da FMA | Persistência: classe exata (%) | Persistência: ±1 classe (%) | Persistência: erro médio | Detecção chuva > 12,9 mm (%) | Alarmes falsos (%) |
|---|---|---|---|---|---|---|---|---|---|
| D+1 | 3607 | 59,3 | 90,2 | 10,92 | 52,4 | 88,9 | 11,33 | 42,8 | 54,3 |
| D+2 | 3635 | 57,0 | 88,9 | 11,08 | 46,3 | 85,8 | 12,10 | 39,5 | 58,5 |
| D+3 | 3627 | 55,4 | 89,5 | 11,31 | 41,6 | 82,1 | 13,00 | 34,8 | 62,9 |

### Por estação (classe exata %, ±1 classe %, erro médio da FMA)

| Estação | D+1 | D+2 | D+3 |
|---|---|---|---|
| A601 Seropedica-Ecologia Agricola | 64,0 / 92,6 / 9,78 | 61,5 / 89,0 / 9,93 | 59,5 / 90,1 / 10,13 |
| A602 Rio De Janeiro-Marambaia | 50,0 / 88,4 / 25,81 | 47,7 / 89,0 / 25,66 | 47,8 / 90,1 / 25,69 |
| A609 Resende | 56,0 / 87,8 / 9,17 | 52,9 / 86,0 / 9,30 | 50,8 / 87,3 / 9,43 |
| A621 Rio De Janeiro - Vila Militar | 61,8 / 90,7 / 8,80 | 60,2 / 89,1 / 9,11 | 58,6 / 89,4 / 9,36 |
| A626 Rio Claro | 63,8 / 91,1 / 6,91 | 60,0 / 90,0 / 7,30 | 58,4 / 90,6 / 7,87 |
| A636 Rio De Janeiro - Jacarepagua | 59,9 / 91,0 / 5,91 | 59,5 / 90,3 / 6,01 | 57,2 / 89,5 / 6,18 |

## Download incompleto

Rodar de novo completa (o que já veio fica guardado):

- (-22.75777777, -43.68472221) 2025-03-30..2025-04-28: ReadTimeout: HTTPSConnectionPool(host='previous-runs-api.open-meteo.com', port=443): Read timed out. (read timeout=20)
- (-22.75777777, -43.68472221) 2025-10-26..2025-11-24: ReadTimeout: HTTPSConnectionPool(host='previous-runs-api.open-meteo.com', port=443): Read timed out. (read timeout=20)
- (-22.75777777, -43.68472221) 2026-06-23..2026-07-22: ReadTimeout: HTTPSConnectionPool(host='previous-runs-api.open-meteo.com', port=443): Read timed out. (read timeout=20)

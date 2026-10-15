# Validação da previsão da FMA por antecedência (ECMWF x estações INMET)

Teste de 2025-01-01 em diante. Estações: A601 Seropedica-Ecologia Agricola, A602 Rio De Janeiro-Marambaia, A609 Resende, A621 Rio De Janeiro - Vila Militar, A626 Rio Claro, A636 Rio De Janeiro - Jacarepagua.

A previsão para D+h parte da FMA do dia D e avança com a previsão feita j dias antes para cada dia D+j (Previous Runs API; para cada dia, toda a janela de chuva usa a previsão de j dias antes, o que é um pouco mais pessimista que o painel real). *Persistência* = repetir a FMA de hoje (referência ingênua).

### Todas as estações juntas

| Antecedência | Dias avaliados | Classe exata (%) | ±1 classe (%) | Erro médio da FMA | Persistência: classe exata (%) | Persistência: ±1 classe (%) | Persistência: erro médio | Detecção chuva > 12,9 mm (%) | Alarmes falsos (%) |
|---|---|---|---|---|---|---|---|---|---|
| D+1 | 3669 | 59,7 | 90,4 | 10,65 | 52,8 | 89,1 | 11,07 | 42,8 | 54,2 |
| D+2 | 3699 | 57,4 | 89,1 | 10,82 | 46,8 | 85,9 | 11,85 | 39,5 | 58,5 |
| D+3 | 3693 | 55,9 | 89,6 | 11,05 | 42,2 | 82,2 | 12,74 | 34,9 | 62,5 |

### Por estação (classe exata %, ±1 classe %, erro médio da FMA)

| Estação | D+1 | D+2 | D+3 |
|---|---|---|---|
| A601 Seropedica-Ecologia Agricola | 66,3 / 93,4 / 8,18 | 63,5 / 90,2 / 8,39 | 61,9 / 90,9 / 8,60 |
| A602 Rio De Janeiro-Marambaia | 50,0 / 88,4 / 25,81 | 47,7 / 89,0 / 25,66 | 47,8 / 90,1 / 25,69 |
| A609 Resende | 56,0 / 87,8 / 9,17 | 52,9 / 86,0 / 9,30 | 50,8 / 87,3 / 9,43 |
| A621 Rio De Janeiro - Vila Militar | 61,8 / 90,7 / 8,80 | 60,2 / 89,1 / 9,11 | 58,6 / 89,4 / 9,36 |
| A626 Rio Claro | 63,8 / 91,1 / 6,91 | 60,0 / 90,0 / 7,30 | 58,4 / 90,6 / 7,87 |
| A636 Rio De Janeiro - Jacarepagua | 59,9 / 91,0 / 5,91 | 59,5 / 90,3 / 6,01 | 57,2 / 89,5 / 6,18 |

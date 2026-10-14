# Comparação de modelos fixos do Open-Meteo x estações INMET

Período avaliado: a partir de 2025-01-01. Eventos reais de chuva > 12,9 mm: 290 (soma das estações).

Sem correção estatística em nenhum cenário: é o dado do modelo como sai da API.

Só entram dias em que todos os cenários e a estação têm dados, para a comparação ser justa. Dias avaliados por estação: A601 578, A602 509, A609 594, A621 650, A626 649, A636 609.

### Acerto exato da classe da FMA (%) - maior é melhor

| Estação | GFS | ICON | ECMWF | Média dos 3 | Mediana dos 3 | Automático (atual) |
|---|---|---|---|---|---|---|
| A601 Seropedica-Ecologia Agricola | 57,1 | 56,7 | 63,8 | 61,2 | 63,1 | 61,9 |
| A602 Rio De Janeiro-Marambaia | 61,3 | 57,4 | 53,0 | 65,4 | 61,1 | 54,8 |
| A609 Resende | 55,7 | 53,0 | 55,9 | 56,6 | 57,9 | 49,3 |
| A621 Rio De Janeiro - Vila Militar | 55,4 | 54,9 | 61,8 | 66,0 | 65,4 | 65,2 |
| A626 Rio Claro | 54,9 | 55,8 | 62,4 | 59,9 | 60,4 | 56,4 |
| A636 Rio De Janeiro - Jacarepagua | 50,2 | 40,9 | 58,6 | 56,0 | 56,5 | 59,8 |
| **Média ponderada** | **55,6** | **53,0** | **59,5** | **60,8** | **60,8** | **58,1** |

### Acerto com tolerância de 1 classe (%)

| Estação | GFS | ICON | ECMWF | Média dos 3 | Mediana dos 3 | Automático (atual) |
|---|---|---|---|---|---|---|
| A601 Seropedica-Ecologia Agricola | 91,0 | 88,4 | 94,3 | 91,2 | 92,6 | 91,7 |
| A602 Rio De Janeiro-Marambaia | 94,3 | 90,2 | 92,7 | 95,9 | 96,9 | 91,7 |
| A609 Resende | 87,7 | 84,3 | 88,6 | 90,1 | 89,4 | 85,7 |
| A621 Rio De Janeiro - Vila Militar | 88,3 | 89,8 | 90,8 | 92,0 | 92,0 | 92,8 |
| A626 Rio Claro | 85,8 | 85,8 | 92,6 | 92,0 | 90,4 | 89,2 |
| A636 Rio De Janeiro - Jacarepagua | 87,2 | 80,1 | 92,1 | 89,0 | 89,3 | 90,1 |
| **Média ponderada** | **88,9** | **86,4** | **91,8** | **91,6** | **91,6** | **90,2** |

### Erro médio absoluto da FMA - menor é melhor

| Estação | GFS | ICON | ECMWF | Média dos 3 | Mediana dos 3 | Automático (atual) |
|---|---|---|---|---|---|---|
| A601 Seropedica-Ecologia Agricola | 15,46 | 16,27 | 7,98 | 13,90 | 12,48 | 12,08 |
| A602 Rio De Janeiro-Marambaia | 6,91 | 11,43 | 8,62 | 6,58 | 7,43 | 8,00 |
| A609 Resende | 11,01 | 20,07 | 9,58 | 10,10 | 9,61 | 10,51 |
| A621 Rio De Janeiro - Vila Militar | 11,79 | 20,26 | 8,40 | 10,00 | 11,82 | 7,90 |
| A626 Rio Claro | 11,95 | 19,74 | 6,79 | 8,92 | 8,81 | 8,11 |
| A636 Rio De Janeiro - Jacarepagua | 11,04 | 24,58 | 4,94 | 6,36 | 7,24 | 5,29 |
| **Média ponderada** | **11,46** | **18,97** | **7,68** | **9,35** | **9,62** | **8,61** |

### Erro médio absoluto da UR às 13h (p.p.)

| Estação | GFS | ICON | ECMWF | Média dos 3 | Mediana dos 3 | Automático (atual) |
|---|---|---|---|---|---|---|
| A601 Seropedica-Ecologia Agricola | 9,0 | 6,4 | 6,6 | 5,8 | 5,8 | 7,6 |
| A602 Rio De Janeiro-Marambaia | 8,2 | 9,5 | 7,0 | 7,3 | 7,3 | 7,9 |
| A609 Resende | 9,2 | 7,6 | 6,6 | 6,1 | 6,1 | 8,5 |
| A621 Rio De Janeiro - Vila Militar | 8,4 | 6,3 | 6,2 | 5,7 | 5,7 | 7,4 |
| A626 Rio Claro | 9,8 | 6,4 | 5,5 | 5,1 | 5,1 | 6,5 |
| A636 Rio De Janeiro - Jacarepagua | 12,7 | 10,3 | 8,0 | 6,7 | 6,7 | 5,6 |
| **Média ponderada** | **9,6** | **7,7** | **6,6** | **6,1** | **6,1** | **7,2** |

### Detecção de chuva > 12,9 mm (%) - maior é melhor

| Estação | GFS | ICON | ECMWF | Média dos 3 | Mediana dos 3 | Automático (atual) |
|---|---|---|---|---|---|---|
| A601 Seropedica-Ecologia Agricola | 34,8 | 30,4 | 43,5 | 39,1 | 30,4 | 39,1 |
| A602 Rio De Janeiro-Marambaia | 56,0 | 48,0 | 64,0 | 60,0 | 52,0 | 68,0 |
| A609 Resende | 42,6 | 24,6 | 34,4 | 31,1 | 26,2 | 36,1 |
| A621 Rio De Janeiro - Vila Militar | 40,0 | 42,2 | 53,3 | 44,4 | 46,7 | 55,6 |
| A626 Rio Claro | 44,2 | 19,2 | 42,3 | 30,8 | 28,8 | 28,8 |
| A636 Rio De Janeiro - Jacarepagua | 37,7 | 32,8 | 41,0 | 36,1 | 34,4 | 45,9 |
| **Média ponderada** | **42,2** | **32,5** | **46,0** | **39,7** | **36,1** | **45,0** |

### Alarmes falsos de chuva > 12,9 mm (%) - menor é melhor

| Estação | GFS | ICON | ECMWF | Média dos 3 | Mediana dos 3 | Automático (atual) |
|---|---|---|---|---|---|---|
| A601 Seropedica-Ecologia Agricola | 40,7 | 33,3 | 44,4 | 30,8 | 26,3 | 40,0 |
| A602 Rio De Janeiro-Marambaia | 48,1 | 50,0 | 57,9 | 46,4 | 40,9 | 60,5 |
| A609 Resende | 57,4 | 61,5 | 52,3 | 56,8 | 56,8 | 60,0 |
| A621 Rio De Janeiro - Vila Militar | 45,5 | 36,7 | 51,0 | 33,3 | 27,6 | 45,7 |
| A626 Rio Claro | 55,8 | 41,2 | 48,8 | 38,5 | 37,5 | 54,5 |
| A636 Rio De Janeiro - Jacarepagua | 28,1 | 31,0 | 39,0 | 15,4 | 16,0 | 41,7 |
| **Média ponderada** | **46,0** | **42,0** | **48,7** | **36,5** | **33,9** | **50,1** |


## Download

Todos os blocos foram baixados.

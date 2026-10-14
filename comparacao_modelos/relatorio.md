# Comparação de modelos fixos do Open-Meteo x estações INMET

Período avaliado: a partir de 2025-01-01. Eventos reais de chuva > 12,9 mm: 304 (soma das estações).

Sem correção estatística em nenhum cenário: é o dado do modelo como sai da API.

### Acerto exato da classe da FMA (%) - maior é melhor

| Estação | GFS | ICON | ECMWF | Média dos 3 | Mediana dos 3 | Automático (atual) |
|---|---|---|---|---|---|---|
| A601 Seropedica-Ecologia Agricola | 57,4 | 58,4 | 64,4 | 61,8 | 63,4 | 62,3 |
| A602 Rio De Janeiro-Marambaia | 61,4 | 58,5 | 47,6 | 61,9 | 61,4 | 49,5 |
| A609 Resende | 56,8 | 52,5 | 56,6 | 56,0 | 58,3 | 50,0 |
| A621 Rio De Janeiro - Vila Militar | 55,4 | 54,9 | 61,8 | 66,0 | 65,4 | 65,2 |
| A626 Rio Claro | 54,9 | 55,8 | 62,4 | 59,9 | 60,4 | 56,4 |
| A636 Rio De Janeiro - Jacarepagua | 51,7 | 42,4 | 59,7 | 56,2 | 57,0 | 59,2 |
| **Média ponderada** | **56,2** | **53,7** | **58,9** | **60,3** | **61,0** | **57,2** |

### Acerto com tolerância de 1 classe (%)

| Estação | GFS | ICON | ECMWF | Média dos 3 | Mediana dos 3 | Automático (atual) |
|---|---|---|---|---|---|---|
| A601 Seropedica-Ecologia Agricola | 90,9 | 88,9 | 94,3 | 91,3 | 92,3 | 92,1 |
| A602 Rio De Janeiro-Marambaia | 92,2 | 89,5 | 89,3 | 93,7 | 94,1 | 89,8 |
| A609 Resende | 88,2 | 84,7 | 88,5 | 90,7 | 90,0 | 86,2 |
| A621 Rio De Janeiro - Vila Militar | 88,3 | 89,8 | 90,8 | 92,0 | 92,0 | 92,8 |
| A626 Rio Claro | 85,8 | 85,8 | 92,6 | 92,0 | 90,4 | 89,2 |
| A636 Rio De Janeiro - Jacarepagua | 87,8 | 80,5 | 91,7 | 88,7 | 89,2 | 89,5 |
| **Média ponderada** | **88,8** | **86,5** | **91,2** | **91,4** | **91,3** | **90,0** |

### Erro médio absoluto da FMA - menor é melhor

| Estação | GFS | ICON | ECMWF | Média dos 3 | Mediana dos 3 | Automático (atual) |
|---|---|---|---|---|---|---|
| A601 Seropedica-Ecologia Agricola | 15,31 | 15,80 | 7,91 | 13,67 | 12,35 | 11,88 |
| A602 Rio De Janeiro-Marambaia | 22,98 | 25,46 | 25,83 | 23,40 | 23,67 | 24,85 |
| A609 Resende | 10,34 | 20,79 | 8,86 | 9,79 | 9,16 | 9,61 |
| A621 Rio De Janeiro - Vila Militar | 11,79 | 20,26 | 8,40 | 10,00 | 11,82 | 7,90 |
| A626 Rio Claro | 11,95 | 19,74 | 6,79 | 8,92 | 8,81 | 8,11 |
| A636 Rio De Janeiro - Jacarepagua | 11,03 | 24,83 | 5,79 | 6,42 | 7,14 | 6,35 |
| **Média ponderada** | **13,79** | **21,16** | **10,45** | **11,88** | **12,03** | **11,28** |

### Erro médio absoluto da UR às 13h (p.p.)

| Estação | GFS | ICON | ECMWF | Média dos 3 | Mediana dos 3 | Automático (atual) |
|---|---|---|---|---|---|---|
| A601 Seropedica-Ecologia Agricola | 9,0 | 6,4 | 6,6 | 5,8 | 5,8 | 7,6 |
| A602 Rio De Janeiro-Marambaia | 8,2 | 9,3 | 7,1 | 7,2 | 7,2 | 7,9 |
| A609 Resende | 9,2 | 7,6 | 6,6 | 6,1 | 6,1 | 8,5 |
| A621 Rio De Janeiro - Vila Militar | 8,4 | 6,3 | 6,2 | 5,7 | 5,7 | 7,4 |
| A626 Rio Claro | 9,8 | 6,4 | 5,5 | 5,1 | 5,1 | 6,5 |
| A636 Rio De Janeiro - Jacarepagua | 12,7 | 10,4 | 8,0 | 6,7 | 6,7 | 5,7 |
| **Média ponderada** | **9,6** | **7,7** | **6,6** | **6,1** | **6,1** | **7,3** |

### Detecção de chuva > 12,9 mm (%) - maior é melhor

| Estação | GFS | ICON | ECMWF | Média dos 3 | Mediana dos 3 | Automático (atual) |
|---|---|---|---|---|---|---|
| A601 Seropedica-Ecologia Agricola | 38,5 | 34,6 | 48,1 | 42,3 | 34,6 | 44,2 |
| A602 Rio De Janeiro-Marambaia | 57,7 | 50,0 | 65,4 | 61,5 | 53,8 | 65,4 |
| A609 Resende | 42,6 | 25,0 | 39,7 | 30,9 | 27,9 | 41,2 |
| A621 Rio De Janeiro - Vila Militar | 40,0 | 42,2 | 53,3 | 44,4 | 46,7 | 55,6 |
| A626 Rio Claro | 44,2 | 19,2 | 42,3 | 30,8 | 28,8 | 28,8 |
| A636 Rio De Janeiro - Jacarepagua | 37,7 | 32,8 | 41,0 | 36,1 | 34,4 | 45,9 |
| **Média ponderada** | **43,4** | **33,8** | **48,2** | **40,8** | **37,7** | **46,7** |

### Alarmes falsos de chuva > 12,9 mm (%) - menor é melhor

| Estação | GFS | ICON | ECMWF | Média dos 3 | Mediana dos 3 | Automático (atual) |
|---|---|---|---|---|---|---|
| A601 Seropedica-Ecologia Agricola | 39,4 | 30,8 | 44,4 | 29,0 | 25,0 | 39,5 |
| A602 Rio De Janeiro-Marambaia | 46,4 | 48,0 | 56,4 | 44,8 | 39,1 | 60,5 |
| A609 Resende | 54,7 | 58,5 | 48,1 | 54,3 | 52,5 | 56,2 |
| A621 Rio De Janeiro - Vila Militar | 45,5 | 36,7 | 51,0 | 33,3 | 27,6 | 45,7 |
| A626 Rio Claro | 55,8 | 41,2 | 48,8 | 38,5 | 37,5 | 54,5 |
| A636 Rio De Janeiro - Jacarepagua | 28,1 | 31,0 | 39,0 | 15,4 | 16,0 | 41,7 |
| **Média ponderada** | **45,0** | **40,9** | **47,9** | **35,7** | **32,8** | **49,6** |


## Download do Open-Meteo

Todos os blocos foram baixados sem falhas.

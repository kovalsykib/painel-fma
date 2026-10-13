# Relatório de calibração (Open-Meteo x estações INMET)

Teste em dados que o ajuste não viu: de 2025-01-01 até o último dia disponível. O ajuste usa só os dados anteriores a essa data. Eventos de chuva > 12,9 mm (que zeram a FMA) no teste: 552 (soma das estações).

**Como ler:** *Bruto* = Open-Meteo sem correção. *Própria estação* = correção aprendida na própria estação (caso ideal). *Estação vizinha* = correção aprendida na estação mais próxima, aplicada sem olhar a estação-alvo (simula um município sem estação).

### Acerto exato da classe de perigo da FMA (%) - quanto maior, melhor

| Estação | Bruto | Corrigido (própria estação) | Corrigido (estação vizinha) |
|---|---|---|---|
| A601 Seropedica-Ecologia Agricola | 62,3 | 62,2 | 60,1 |
| A602 Rio De Janeiro-Marambaia | 49,5 | 60,7 | 55,4 |
| A603 Duque De Caxias - Xerem | 57,2 | 60,9 | 58,6 |
| A609 Resende | 50,0 | 52,8 | 50,8 |
| A611 Valenca | 66,3 | 61,9 | 63,0 |
| A621 Rio De Janeiro - Vila Militar | 65,2 | 62,0 | 63,8 |
| A626 Rio Claro | 56,4 | 57,5 | 60,2 |
| A628 Angra Dos Reis | 60,4 | 59,0 | 59,6 |
| A636 Rio De Janeiro - Jacarepagua | 59,2 | 58,4 | 59,8 |
| A637 Paty Do Alferes - Avelar | 68,4 | 64,5 | 64,5 |
| **Média (ponderada por dias)** | **59,5** | **60,0** | **59,6** |

### Acerto da classe com tolerância de 1 classe (%)

| Estação | Bruto | Corrigido (própria estação) | Corrigido (estação vizinha) |
|---|---|---|---|
| A601 Seropedica-Ecologia Agricola | 92,1 | 90,8 | 89,9 |
| A602 Rio De Janeiro-Marambaia | 89,8 | 90,8 | 89,2 |
| A603 Duque De Caxias - Xerem | 90,2 | 89,5 | 88,7 |
| A609 Resende | 86,2 | 88,0 | 85,9 |
| A611 Valenca | 91,2 | 88,3 | 90,0 |
| A621 Rio De Janeiro - Vila Militar | 92,8 | 90,2 | 91,2 |
| A626 Rio Claro | 89,2 | 88,1 | 89,7 |
| A628 Angra Dos Reis | 92,6 | 92,0 | 92,1 |
| A636 Rio De Janeiro - Jacarepagua | 89,5 | 88,3 | 88,6 |
| A637 Paty Do Alferes - Avelar | 90,6 | 88,0 | 87,9 |
| **Média (ponderada por dias)** | **90,4** | **89,4** | **89,3** |

### Erro médio absoluto da FMA (pontos de FMA) - quanto menor, melhor

| Estação | Bruto | Corrigido (própria estação) | Corrigido (estação vizinha) |
|---|---|---|---|
| A601 Seropedica-Ecologia Agricola | 11,88 | 12,15 | 17,23 |
| A602 Rio De Janeiro-Marambaia | 24,85 | 22,00 | 23,68 |
| A603 Duque De Caxias - Xerem | 5,20 | 7,36 | 4,71 |
| A609 Resende | 9,61 | 12,65 | 9,47 |
| A611 Valenca | 9,30 | 17,34 | 13,43 |
| A621 Rio De Janeiro - Vila Militar | 7,90 | 12,32 | 9,92 |
| A626 Rio Claro | 8,11 | 8,76 | 7,21 |
| A628 Angra Dos Reis | 2,69 | 3,59 | 2,85 |
| A636 Rio De Janeiro - Jacarepagua | 6,35 | 6,58 | 6,71 |
| A637 Paty Do Alferes - Avelar | 13,18 | 15,77 | 26,77 |
| **Média (ponderada por dias)** | **9,79** | **11,67** | **12,05** |

### Viés da umidade às 13h (pontos percentuais; positivo = modelo mais úmido)

| Estação | Bruto | Corrigido (própria estação) | Corrigido (estação vizinha) |
|---|---|---|---|
| A601 Seropedica-Ecologia Agricola | -5,2 | -2,1 | -2,6 |
| A602 Rio De Janeiro-Marambaia | -0,8 | -3,8 | -3,2 |
| A603 Duque De Caxias - Xerem | 1,3 | -3,1 | 1,8 |
| A609 Resende | 6,1 | -3,0 | 8,6 |
| A611 Valenca | 2,9 | 2,0 | 3,2 |
| A621 Rio De Janeiro - Vila Militar | -3,6 | -0,9 | -6,4 |
| A626 Rio Claro | -2,5 | -0,5 | 0,9 |
| A628 Angra Dos Reis | 3,6 | -1,7 | 7,7 |
| A636 Rio De Janeiro - Jacarepagua | 0,1 | -2,6 | 2,7 |
| A637 Paty Do Alferes - Avelar | 0,2 | -0,2 | -1,1 |
| **Média (ponderada por dias)** | **0,2** | **-1,6** | **1,1** |

### Erro médio absoluto da umidade às 13h (pontos percentuais)

| Estação | Bruto | Corrigido (própria estação) | Corrigido (estação vizinha) |
|---|---|---|---|
| A601 Seropedica-Ecologia Agricola | 7,6 | 6,8 | 6,9 |
| A602 Rio De Janeiro-Marambaia | 7,9 | 9,4 | 8,5 |
| A603 Duque De Caxias - Xerem | 6,6 | 7,0 | 7,1 |
| A609 Resende | 8,5 | 7,5 | 10,2 |
| A611 Valenca | 6,1 | 6,0 | 6,4 |
| A621 Rio De Janeiro - Vila Militar | 7,4 | 7,3 | 8,6 |
| A626 Rio Claro | 6,5 | 6,7 | 6,2 |
| A628 Angra Dos Reis | 7,4 | 6,6 | 10,2 |
| A636 Rio De Janeiro - Jacarepagua | 5,7 | 6,1 | 6,7 |
| A637 Paty Do Alferes - Avelar | 5,9 | 6,1 | 6,5 |
| **Média (ponderada por dias)** | **7,0** | **7,0** | **7,8** |

### Viés da chuva de 24h (mm/dia; negativo = modelo chove menos)

| Estação | Bruto | Corrigido (própria estação) | Corrigido (estação vizinha) |
|---|---|---|---|
| A601 Seropedica-Ecologia Agricola | -0,60 | -0,30 | -0,99 |
| A602 Rio De Janeiro-Marambaia | 0,69 | -0,16 | 0,49 |
| A603 Duque De Caxias - Xerem | 1,26 | 0,01 | 2,19 |
| A609 Resende | 0,07 | -0,96 | 0,37 |
| A611 Valenca | 0,10 | 0,10 | 0,20 |
| A621 Rio De Janeiro - Vila Militar | -0,15 | -0,68 | -0,46 |
| A626 Rio Claro | -0,88 | -0,98 | -0,81 |
| A628 Angra Dos Reis | -0,56 | -1,67 | 0,07 |
| A636 Rio De Janeiro - Jacarepagua | -0,39 | -0,52 | -0,51 |
| A637 Paty Do Alferes - Avelar | -0,28 | -0,33 | -0,51 |
| **Média (ponderada por dias)** | **-0,09** | **-0,57** | **-0,01** |

### Detecção de chuva > 12,9 mm, que zera a FMA (% dos eventos reais que o modelo também marca)

| Estação | Bruto | Corrigido (própria estação) | Corrigido (estação vizinha) |
|---|---|---|---|
| A601 Seropedica-Ecologia Agricola | 44,2 | 48,1 | 46,2 |
| A602 Rio De Janeiro-Marambaia | 65,4 | 57,7 | 65,4 |
| A603 Duque De Caxias - Xerem | 72,6 | 56,5 | 77,4 |
| A609 Resende | 41,2 | 33,8 | 48,5 |
| A611 Valenca | 45,8 | 47,9 | 50,0 |
| A621 Rio De Janeiro - Vila Militar | 55,6 | 51,1 | 57,8 |
| A626 Rio Claro | 28,8 | 36,5 | 42,3 |
| A628 Angra Dos Reis | 64,0 | 48,8 | 67,4 |
| A636 Rio De Janeiro - Jacarepagua | 45,9 | 52,5 | 52,5 |
| A637 Paty Do Alferes - Avelar | 42,3 | 50,0 | 42,3 |
| **Média (ponderada por dias)** | **50,5** | **48,2** | **55,0** |

### Alarmes falsos de chuva > 12,9 mm (% dos eventos do modelo que a estação não confirma)

| Estação | Bruto | Corrigido (própria estação) | Corrigido (estação vizinha) |
|---|---|---|---|
| A601 Seropedica-Ecologia Agricola | 39,5 | 47,9 | 36,8 |
| A602 Rio De Janeiro-Marambaia | 60,5 | 59,5 | 62,2 |
| A603 Duque De Caxias - Xerem | 45,1 | 39,7 | 50,5 |
| A609 Resende | 56,2 | 47,7 | 56,6 |
| A611 Valenca | 40,5 | 43,9 | 44,2 |
| A621 Rio De Janeiro - Vila Militar | 45,7 | 48,9 | 46,9 |
| A626 Rio Claro | 54,5 | 48,6 | 45,0 |
| A628 Angra Dos Reis | 42,1 | 32,3 | 44,8 |
| A636 Rio De Janeiro - Jacarepagua | 41,7 | 45,8 | 40,7 |
| A637 Paty Do Alferes - Avelar | 43,6 | 48,0 | 48,8 |
| **Média (ponderada por dias)** | **47,0** | **46,2** | **47,6** |


## Download do Open-Meteo

Todos os blocos foram baixados sem falhas.


## Limites

- A correção ajusta a **distribuição** (viés) do modelo. Se o modelo errar o **dia** da chuva, ela não conserta.
- Chuvas convectivas localizadas são o ponto mais frágil, e justamente uma chuva > 12,9 mm zera a FMA.
- Dado calibrado continua sendo estimativa de modelo, não medição de estação.

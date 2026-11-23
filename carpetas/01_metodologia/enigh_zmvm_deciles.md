# ENIGH 2024: hogares de la ZMVM por decil de ingreso

Generado por `scripts/04a_carpetas.py` el 2026-11-23 desde `data/processed/enigh_decil_cortes.parquet` y `enigh_gasto.parquet`. Fuente: INEGI, ENIGH 2024 Nueva Serie, microdatos (https://www.inegi.org.mx/programas/enigh/nc/2024/). Ámbito `zmvm`: submuestra de 3 767 hogares urbanos de 48 municipios; no es representativa por municipio. Pesos corrientes de 2024. Los deciles son de la ZMVM (decil 1 = 10 % más pobre de la ZMVM).

## Ingreso y rasgos del hogar por decil

| Decil | Ingreso corriente mensual prom. (pesos) | Ingreso trim. máx. del decil | Escolaridad del jefe (años) | % con auto | % con internet | % con PC/tablet | Integrantes |
|---|---|---|---|---|---|---|---|
| 1 | 7,966 | 31,234 | 8.5 | 9.9 | 49.8 | 17.0 | 2.1 |
| 2 | 12,209 | 41,129 | 8.6 | 23.0 | 63.7 | 25.5 | 2.7 |
| 3 | 15,148 | 49,940 | 9.1 | 25.2 | 73.2 | 28.0 | 3.0 |
| 4 | 18,002 | 58,546 | 9.6 | 31.2 | 78.1 | 39.6 | 3.0 |
| 5 | 21,130 | 68,576 | 10.4 | 37.9 | 83.5 | 44.9 | 3.5 |
| 6 | 24,925 | 81,540 | 10.7 | 42.9 | 89.4 | 57.0 | 3.6 |
| 7 | 29,795 | 97,995 | 11.3 | 53.9 | 91.4 | 67.3 | 3.6 |
| 8 | 37,045 | 126,332 | 11.8 | 62.0 | 93.6 | 71.9 | 3.7 |
| 9 | 48,836 | 172,900 | 13.3 | 73.4 | 97.2 | 81.9 | 3.6 |
| 10 | 94,139 | 1,347,817 | 15.1 | 83.8 | 98.7 | 91.0 | 3.4 |

## Gasto trimestral promedio del hogar por rubro y decil (pesos de 2024)

Promedio contando como cero a los hogares que no gastaron. Rubros con pocos hogares que gastan (helados, gimnasio) dan promedios ruidosos.

| Decil | Comida fuera del hogar | Restaurantes | Comida rápida | Antojitos y tacos | Café y bebidas |
|---|---|---|---|---|---|
| 1 | 2,317 | 1,749 | 232 | 317 | 85 |
| 2 | 3,339 | 2,229 | 436 | 550 | 97 |
| 3 | 3,567 | 2,563 | 408 | 501 | 97 |
| 4 | 4,262 | 3,076 | 399 | 631 | 116 |
| 5 | 5,445 | 3,955 | 567 | 878 | 116 |
| 6 | 5,843 | 4,620 | 462 | 750 | 92 |
| 7 | 7,546 | 5,979 | 618 | 868 | 140 |
| 8 | 9,462 | 7,766 | 559 | 1,020 | 125 |
| 9 | 12,892 | 10,654 | 788 | 1,224 | 295 |
| 10 | 21,254 | 18,668 | 760 | 1,699 | 303 |

| Decil | Helados (compra) | Pan y pasteles | Alimentos dentro del hogar | Medicamentos | Educación |
|---|---|---|---|---|---|
| 1 | 7 | 450 | 9,511 | 278 | 627 |
| 2 | 17 | 566 | 12,527 | 350 | 1,128 |
| 3 | 20 | 634 | 14,299 | 369 | 1,511 |
| 4 | 22 | 769 | 14,820 | 440 | 1,440 |
| 5 | 25 | 760 | 17,218 | 492 | 2,413 |
| 6 | 24 | 870 | 17,337 | 472 | 2,805 |
| 7 | 31 | 874 | 18,323 | 696 | 3,151 |
| 8 | 46 | 918 | 19,776 | 702 | 3,597 |
| 9 | 75 | 891 | 21,009 | 834 | 6,088 |
| 10 | 107 | 885 | 25,083 | 2,006 | 14,582 |

| Decil | Esparcimiento | Cuidado personal | Vestido y calzado | Gimnasio y deporte |
|---|---|---|---|---|
| 1 | 238 | 1,036 | 573 | 5 |
| 2 | 375 | 1,409 | 855 | 7 |
| 3 | 557 | 1,789 | 1,287 | 39 |
| 4 | 798 | 1,986 | 1,390 | 48 |
| 5 | 1,052 | 2,373 | 1,874 | 115 |
| 6 | 1,000 | 2,471 | 2,081 | 49 |
| 7 | 1,573 | 2,812 | 2,432 | 147 |
| 8 | 2,373 | 3,568 | 2,831 | 165 |
| 9 | 3,336 | 4,308 | 3,706 | 305 |
| 10 | 6,120 | 6,381 | 6,556 | 853 |

## Porcentaje de hogares que reportó gasto en el rubro

| Decil | Comida fuera del hogar | Restaurantes | Comida rápida | Antojitos y tacos | Café y bebidas | Helados (compra) | Pan y pasteles |
|---|---|---|---|---|---|---|---|
| 1 | 63.5 | 48.9 | 14.1 | 25.8 | 18.4 | 1.7 | 68.0 |
| 2 | 68.3 | 51.3 | 18.6 | 26.2 | 20.0 | 3.3 | 70.6 |
| 3 | 69.5 | 49.8 | 21.2 | 25.9 | 19.6 | 4.7 | 70.4 |
| 4 | 77.9 | 59.4 | 20.6 | 28.3 | 17.5 | 4.9 | 78.0 |
| 5 | 77.1 | 62.8 | 26.2 | 30.7 | 16.6 | 3.5 | 76.6 |
| 6 | 81.1 | 68.2 | 22.0 | 27.0 | 12.6 | 5.1 | 75.5 |
| 7 | 82.0 | 69.8 | 24.7 | 26.4 | 15.9 | 5.9 | 72.8 |
| 8 | 86.0 | 73.0 | 21.7 | 29.5 | 15.2 | 5.4 | 72.5 |
| 9 | 87.6 | 76.8 | 25.6 | 35.1 | 19.4 | 4.9 | 66.5 |
| 10 | 91.5 | 85.1 | 21.0 | 34.1 | 19.0 | 7.1 | 57.5 |

# Ficha de alcaldía: Milpa Alta (Ciudad de México), clave 09009

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 128,710 habitantes (lugar 40 de 76 en la ZMVM). Fuente: INEGI, Censo de Poblacion y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 32,999. AGEB urbanas: 42. Superficie urbana de esas AGEB: 27.8 km².
- Densidad: 4,631 hab/km² (lugar 42 de 76).
- Edad: 0-14 años 23.2 %; 15-24 17.4 %; 25-59 47.9 %; 60 o más 11.5 %.
- Escolaridad promedio de la población de 15 y más: 10.1 años (lugar 41 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 40.1 %; con internet: 53.9 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 49.5 %, medio 50.5 %, alto 0.0 %.
- Decil estimado típico (mediana ponderada por población): 5.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Bajo 16.9 %; Medio 64.5 %; Alto 17.7 %; Muy alto 0.9 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 7,576 (58.9 por cada 1 000 habitantes, lugar 37 de 76). Fuente: INEGI, DENUE (corte 05/2026; historico 11/2020).
- Establecimientos en el DENUE 11/2020: 7,714. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 28,863.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 4,129 | 54.5 % |
| 81 Otros servicios excepto actividades gubernamentales | 1,031 | 13.6 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 770 | 10.2 % |
| 31 Industrias manufactureras | 409 | 5.4 % |
| 62 Servicios de salud y de asistencia social | 314 | 4.1 % |
| 61 Servicios educativos | 173 | 2.3 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 1,242 |
| 812110 | Salones y clínicas de belleza y peluquerías | 358 |
| 465311 | Comercio al por menor de artículos de papelería | 289 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 230 |
| 465912 | Comercio al por menor de regalos | 212 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 193 |
| 461130 | Comercio al por menor de frutas y verduras frescas | 182 |
| 461122 | Comercio al por menor de carne de aves | 173 |
| 461140 | Comercio al por menor de semillas y granos alimenticios, especias y chiles secos | 156 |
| 722514 | Restaurantes con servicio de preparación de tacos y tortas | 151 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 1,244 | 96.7 |
| barberia_estetica | 358 | 27.8 |
| carniceria | 302 | 23.5 |
| papeleria | 289 | 22.5 |
| tienda_ropa | 230 | 17.9 |
| fruteria | 182 | 14.1 |
| farmacia | 168 | 13.1 |
| taqueria | 151 | 11.7 |
| fonda | 143 | 11.1 |
| tortilleria | 140 | 10.9 |
| taller_mecanico | 136 | 10.6 |
| consultorio_dental | 117 | 9.1 |
| ferreteria | 112 | 8.7 |
| panaderia | 77 | 6.0 |
| cafeteria | 73 | 5.7 |
| purificadora | 67 | 5.2 |
| lavanderia | 58 | 4.5 |
| cafe_internet | 51 | 4.0 |
| zapateria | 46 | 3.6 |
| tienda_mascotas | 44 | 3.4 |
| tienda_celulares | 43 | 3.3 |
| consultorio_medico | 41 | 3.2 |
| heladeria | 37 | 2.9 |
| pizzeria | 36 | 2.8 |
| pasteleria | 32 | 2.5 |
| floreria | 31 | 2.4 |
| gimnasio | 30 | 2.3 |
| optica | 24 | 1.9 |
| veterinaria | 17 | 1.3 |
| cerrajeria | 14 | 1.1 |
| laboratorio_clinico | 13 | 1.0 |
| spa | 11 | 0.9 |
| bar | 6 | 0.5 |
| escuela_idiomas | 5 | 0.4 |
| guarderia | 4 | 0.3 |
| sushi | 4 | 0.3 |
| libreria | 3 | 0.2 |
| comida_china | 0 | 0.0 |
| coworking | 0 | 0.0 |
| renta_bicicletas | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| SAN ANTONIO TECOMITL | 6 | 27,768 | 1,901 | medio |
| VILLA MILPA ALTA | 8 | 18,213 | 1,564 | medio |
| SAN PABLO OZTOTEPEC | 7 | 17,715 | 835 | bajo |
| SAN SALVADOR CUAUHTENCO | 3 | 16,847 | 637 | medio |
| SAN PEDRO ATOCPAN | 5 | 9,234 | 615 | bajo |
| SAN FRANCISCO TECOXPA | 2 | 8,320 | 431 | medio |
| SANTA ANA TLACOTENCO | 3 | 11,715 | 421 | bajo |
| SAN BARTOLOME XICOMULCO | 1 | 4,933 | 233 | medio |
| SAN NICOLAS TETELCO | 2 | 4,078 | 228 | bajo |
| SAN JERONIMO MIACATLAN | 1 | 3,799 | 197 | bajo |

## Colonias de mayor y menor nivel socioeconómico estimado

Solo colonias con 3 000 habitantes o más en sus AGEB. «Decil esperado» es el promedio ponderado por población del decil estimado (1 = más bajo, 10 = más alto de la ZMVM). Es estimación.

Mayor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| SAN ANTONIO TECOMITL | 27,768 | 5.1 |
| VILLA MILPA ALTA | 18,213 | 5.0 |
| SAN BARTOLOME XICOMULCO | 4,933 | 4.7 |
| SAN SALVADOR CUAUHTENCO | 16,847 | 4.7 |
| SAN JERONIMO MIACATLAN | 3,799 | 4.7 |

Menor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| SAN LORENZO TLACOYUCAN | 4,288 | 3.3 |
| SANTA ANA TLACOTENCO | 11,715 | 3.9 |
| SAN PEDRO ATOCPAN | 9,234 | 4.2 |
| SAN NICOLAS TETELCO | 4,078 | 4.3 |
| SAN FRANCISCO TECOXPA | 8,320 | 4.4 |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 191.1 millones de pesos por trimestre.
- Por hogar: 5,792 pesos por trimestre (lugar 42 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.

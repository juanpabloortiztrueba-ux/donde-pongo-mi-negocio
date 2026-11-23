# Ficha de municipio: Tizayuca (Hidalgo), clave 13069

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 158,965 habitantes (lugar 37 de 76 en la ZMVM). Fuente: INEGI, Censo de Poblacion y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 44,872. AGEB urbanas: 105. Superficie urbana de esas AGEB: 40.0 km².
- Densidad: 3,978 hab/km² (lugar 49 de 76).
- Edad: 0-14 años 27.4 %; 15-24 17.0 %; 25-59 47.6 %; 60 o más 7.8 %.
- Escolaridad promedio de la población de 15 y más: 10.3 años (lugar 34 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 45.0 %; con internet: 55.0 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 60.2 %, medio 39.8 %, alto 0.0 %, sin estimación 0.0 %.
- Decil estimado típico (mediana ponderada por población): 4.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Muy bajo 8.1 %; Bajo 52.0 %; Medio 32.4 %; Alto 6.3 %; Muy alto 1.2 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 9,611 (60.5 por cada 1 000 habitantes, lugar 34 de 76). Fuente: INEGI, DENUE (corte 05/2026; historico 11/2020).
- Establecimientos en el DENUE 11/2020: 7,122. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 45,873.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 4,519 | 47.0 % |
| 81 Otros servicios excepto actividades gubernamentales | 1,543 | 16.1 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 1,216 | 12.7 % |
| 31 Industrias manufactureras | 429 | 4.5 % |
| 62 Servicios de salud y de asistencia social | 366 | 3.8 % |
| 33 Industrias manufactureras | 241 | 2.5 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 1,151 |
| 812110 | Salones y clínicas de belleza y peluquerías | 574 |
| 465311 | Comercio al por menor de artículos de papelería | 356 |
| 467115 | Comercio al por menor de artículos para la limpieza | 255 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 240 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 207 |
| 467111 | Comercio al por menor en ferreterías y tlapalerías | 189 |
| 722514 | Restaurantes con servicio de preparación de tacos y tortas | 183 |
| 464111 | Farmacias sin minisúper | 183 |
| 461122 | Comercio al por menor de carne de aves | 183 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 1,200 | 75.5 |
| barberia_estetica | 574 | 36.1 |
| papeleria | 356 | 22.4 |
| carniceria | 257 | 16.2 |
| taller_mecanico | 234 | 14.7 |
| fonda | 216 | 13.6 |
| tienda_ropa | 207 | 13.0 |
| farmacia | 198 | 12.5 |
| ferreteria | 189 | 11.9 |
| taqueria | 183 | 11.5 |
| fruteria | 150 | 9.4 |
| cafeteria | 147 | 9.2 |
| tortilleria | 131 | 8.2 |
| panaderia | 119 | 7.5 |
| consultorio_dental | 89 | 5.6 |
| purificadora | 71 | 4.5 |
| tienda_celulares | 71 | 4.5 |
| cafe_internet | 67 | 4.2 |
| heladeria | 55 | 3.5 |
| consultorio_medico | 54 | 3.4 |
| bar | 54 | 3.4 |
| lavanderia | 53 | 3.3 |
| gimnasio | 46 | 2.9 |
| tienda_mascotas | 44 | 2.8 |
| zapateria | 42 | 2.6 |
| floreria | 39 | 2.5 |
| spa | 26 | 1.6 |
| laboratorio_clinico | 24 | 1.5 |
| pasteleria | 23 | 1.4 |
| cerrajeria | 21 | 1.3 |
| optica | 21 | 1.3 |
| pizzeria | 20 | 1.3 |
| veterinaria | 15 | 0.9 |
| escuela_idiomas | 10 | 0.6 |
| sushi | 9 | 0.6 |
| comida_china | 6 | 0.4 |
| guarderia | 4 | 0.3 |
| libreria | 2 | 0.1 |
| coworking | 0 | 0.0 |
| renta_bicicletas | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| CENTRO | 12 | 18,921 | 1,183 | bajo |
| CUXTITLA | 2 | 2,287 | 974 | medio |
| HACIENDAS DE TIZAYUCA | 21 | 23,298 | 813 | bajo |
| ATEMPA | 2 | 5,530 | 811 | bajo |
| EL PEDREGAL | 2 | 8,829 | 761 | bajo |
| NACOZARI | 2 | 5,257 | 668 | medio |
| TIZAYUCA | 4 | 5,837 | 491 | bajo |
| LOS HEROES DE TIZAYUCA | 4 | 11,619 | 467 | medio |
| NUEVO TIZAYUCA | 2 | 5,830 | 451 | medio |
| RANCHO DON ANTONIO | 7 | 10,179 | 437 | bajo |

## Colonias de mayor y menor nivel socioeconómico estimado

Solo colonias con 3 000 habitantes o más en sus AGEB. «Decil esperado» es el promedio ponderado por población del decil estimado (1 = más bajo, 10 = más alto de la ZMVM). Es estimación.

Mayor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| EL TEPEYAC | 4,172 | 6.2 |
| NACOZARI | 5,257 | 5.6 |
| NUEVO TIZAYUCA | 5,830 | 5.3 |
| TIZAYUCA | 5,837 | 5.3 |
| LOS HEROES DE TIZAYUCA | 11,619 | 5.3 |

Menor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| EL CARMEN | 7,029 | 3.5 |
| DON ANTONIO | 9,526 | 4.1 |
| FUENTES DE TIZAYUCA | 6,160 | 4.2 |
| CENTRO | 18,921 | 4.2 |
| EL PEDREGAL | 8,829 | 4.2 |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 267.2 millones de pesos por trimestre.
- Por hogar: 5,955 pesos por trimestre (lugar 38 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.

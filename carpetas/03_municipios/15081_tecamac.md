# Ficha de municipio: Tecámac (Estado de México), clave 15081

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 536,414 habitantes (lugar 13 de 76 en la ZMVM). Fuente: INEGI, Censo de Poblacion y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 161,409. AGEB urbanas: 132. Superficie urbana de esas AGEB: 69.7 km².
- Densidad: 7,696 hab/km² (lugar 25 de 76).
- Edad: 0-14 años 23.9 %; 15-24 16.9 %; 25-59 50.7 %; 60 o más 8.4 %.
- Escolaridad promedio de la población de 15 y más: 11.0 años (lugar 16 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 48.7 %; con internet: 65.1 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 39.3 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 31.7 %, medio 64.3 %, alto 4.0 %.
- Decil estimado típico (mediana ponderada por población): 6.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Muy bajo 23.2 %; Bajo 44.4 %; Medio 24.3 %; Alto 7.5 %; Muy alto 0.6 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 21,582 (40.2 por cada 1 000 habitantes, lugar 71 de 76). Fuente: INEGI, DENUE (corte 05/2026; historico 11/2020).
- Establecimientos en el DENUE 11/2020: 17,534. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 82,804.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 10,949 | 50.7 % |
| 81 Otros servicios excepto actividades gubernamentales | 3,328 | 15.4 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 2,641 | 12.2 % |
| 31 Industrias manufactureras | 999 | 4.6 % |
| 62 Servicios de salud y de asistencia social | 859 | 4.0 % |
| 61 Servicios educativos | 662 | 3.1 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 2,476 |
| 812110 | Salones y clínicas de belleza y peluquerías | 1,394 |
| 465311 | Comercio al por menor de artículos de papelería | 870 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 547 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 531 |
| 467115 | Comercio al por menor de artículos para la limpieza | 495 |
| 464111 | Farmacias sin minisúper | 478 |
| 461122 | Comercio al por menor de carne de aves | 466 |
| 461130 | Comercio al por menor de frutas y verduras frescas | 459 |
| 722514 | Restaurantes con servicio de preparación de tacos y tortas | 413 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 2,629 | 49.0 |
| barberia_estetica | 1,394 | 26.0 |
| papeleria | 870 | 16.2 |
| carniceria | 706 | 13.2 |
| tienda_ropa | 531 | 9.9 |
| farmacia | 530 | 9.9 |
| fonda | 460 | 8.6 |
| fruteria | 459 | 8.6 |
| taller_mecanico | 434 | 8.1 |
| taqueria | 413 | 7.7 |
| ferreteria | 402 | 7.5 |
| tortilleria | 370 | 6.9 |
| cafeteria | 345 | 6.4 |
| consultorio_dental | 284 | 5.3 |
| panaderia | 254 | 4.7 |
| purificadora | 218 | 4.1 |
| tienda_celulares | 198 | 3.7 |
| lavanderia | 173 | 3.2 |
| tienda_mascotas | 159 | 3.0 |
| heladeria | 156 | 2.9 |
| cafe_internet | 148 | 2.8 |
| consultorio_medico | 137 | 2.6 |
| floreria | 124 | 2.3 |
| gimnasio | 121 | 2.3 |
| veterinaria | 89 | 1.7 |
| zapateria | 87 | 1.6 |
| pizzeria | 67 | 1.2 |
| spa | 66 | 1.2 |
| optica | 63 | 1.2 |
| cerrajeria | 60 | 1.1 |
| pasteleria | 54 | 1.0 |
| bar | 47 | 0.9 |
| laboratorio_clinico | 38 | 0.7 |
| escuela_idiomas | 17 | 0.3 |
| sushi | 16 | 0.3 |
| guarderia | 11 | 0.2 |
| comida_china | 10 | 0.2 |
| libreria | 9 | 0.2 |
| coworking | 0 | 0.0 |
| renta_bicicletas | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| LOS HÉROES SECCIÓN BOSQUES | 4 | 72,917 | 1,989 | medio |
| TECAMAC CENTRO | 4 | 9,363 | 1,983 | bajo |
| OJO DE AGUA | 7 | 28,131 | 1,898 | alto |
| LOS HÉROES TECÁMAC | 5 | 53,709 | 1,570 | medio |
| LOMAS DE TECAMAC | 4 | 18,698 | 1,006 | bajo |
| LOS HÉROES SECCIÓN JARDINES | 2 | 27,925 | 811 | bajo |
| SAN MARTIN AZCATEPEC | 4 | 9,263 | 746 | bajo |
| REYES ACOZAC | 2 | 7,106 | 718 | bajo |
| SAN PEDRO ATZOMPA | 2 | 10,381 | 661 | bajo |
| SANTA MARÍA OZUMBILLA | 2 | 7,884 | 599 | bajo |

## Colonias de mayor y menor nivel socioeconómico estimado

Solo colonias con 3 000 habitantes o más en sus AGEB. «Decil esperado» es el promedio ponderado por población del decil estimado (1 = más bajo, 10 = más alto de la ZMVM). Es estimación.

Mayor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| REAL DEL SOL | 5,411 | 8.3 |
| OJO DE AGUA | 28,131 | 8.0 |
| PUNTA PALERMO | 4,710 | 7.5 |
| REAL VERONA | 14,677 | 6.9 |
| VILLA DEL REAL PRIMERA, SEGUNDA Y TERCERA SECCIÓN | 9,640 | 6.8 |

Menor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| RANCHO SANTA CRUZ | 9,084 | 2.5 |
| SANTO DOMINGO AJOLOAPAN | 4,298 | 2.6 |
| SANTA MARIA AJOLOAPAN | 5,002 | 3.5 |
| LOMAS DE TECAMAC | 18,698 | 3.7 |
| SAN MARTIN | 4,620 | 3.7 |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 1,205.9 millones de pesos por trimestre.
- Por hogar: 7,471 pesos por trimestre (lugar 24 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.

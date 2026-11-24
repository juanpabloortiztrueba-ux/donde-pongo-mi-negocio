# Ficha de alcaldía: Álvaro Obregón (Ciudad de México), clave 09010

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 759,003 habitantes (lugar 6 de 76 en la ZMVM). Fuente: INEGI, Censo de Población y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 219,322. AGEB urbanas: 199. Superficie urbana de esas AGEB: 69.4 km².
- Densidad: 10,936 hab/km² (lugar 16 de 76).
- Edad: 0-14 años 17.9 %; 15-24 15.1 %; 25-59 50.7 %; 60 o más 16.1 %.
- Escolaridad promedio de la población de 15 y más: 11.2 años (lugar 14 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 48.5 %; con internet: 76.5 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 22.8 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 14.8 %, medio 65.8 %, alto 19.4 %.
- Decil estimado típico (mediana ponderada por población): 6.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Muy bajo 22.4 %; Bajo 46.3 %; Medio 30.1 %; Alto 1.1 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 24,594 (32.4 por cada 1 000 habitantes, lugar 76 de 76). Fuente: INEGI, DENUE (corte 05/2026; histórico 11/2020).
- Establecimientos en el DENUE 11/2020: 26,228. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 237,532.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 10,498 | 42.7 % |
| 81 Otros servicios excepto actividades gubernamentales | 3,760 | 15.3 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 3,047 | 12.4 % |
| 62 Servicios de salud y de asistencia social | 1,523 | 6.2 % |
| 31 Industrias manufactureras | 984 | 4.0 % |
| 61 Servicios educativos | 787 | 3.2 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 2,846 |
| 812110 | Salones y clínicas de belleza y peluquerías | 1,421 |
| 465311 | Comercio al por menor de artículos de papelería | 882 |
| 722514 | Restaurantes con servicio de preparación de tacos y tortas | 580 |
| 722511 | Restaurantes con servicio de preparación de alimentos a la carta o de comida corrida | 524 |
| 461122 | Comercio al por menor de carne de aves | 515 |
| 722515 | Cafeterías, fuentes de sodas, neverías, refresquerías y similares | 466 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 464 |
| 461160 | Comercio al por menor de dulces y materias primas para repostería | 458 |
| 461130 | Comercio al por menor de frutas y verduras frescas | 426 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 3,057 | 40.3 |
| barberia_estetica | 1,421 | 18.7 |
| papeleria | 882 | 11.6 |
| carniceria | 836 | 11.0 |
| fonda | 683 | 9.0 |
| taqueria | 580 | 7.6 |
| taller_mecanico | 551 | 7.3 |
| consultorio_medico | 537 | 7.1 |
| cafeteria | 466 | 6.1 |
| fruteria | 426 | 5.6 |
| tortilleria | 416 | 5.5 |
| farmacia | 415 | 5.5 |
| consultorio_dental | 408 | 5.4 |
| tienda_ropa | 369 | 4.9 |
| ferreteria | 323 | 4.3 |
| lavanderia | 290 | 3.8 |
| panaderia | 280 | 3.7 |
| veterinaria | 153 | 2.0 |
| gimnasio | 147 | 1.9 |
| tienda_celulares | 138 | 1.8 |
| floreria | 137 | 1.8 |
| cafe_internet | 127 | 1.7 |
| heladeria | 124 | 1.6 |
| tienda_mascotas | 109 | 1.4 |
| cerrajeria | 92 | 1.2 |
| pizzeria | 86 | 1.1 |
| zapateria | 81 | 1.1 |
| pasteleria | 77 | 1.0 |
| purificadora | 77 | 1.0 |
| optica | 71 | 0.9 |
| laboratorio_clinico | 63 | 0.8 |
| spa | 50 | 0.7 |
| sushi | 46 | 0.6 |
| bar | 43 | 0.6 |
| guarderia | 37 | 0.5 |
| escuela_idiomas | 19 | 0.3 |
| libreria | 17 | 0.2 |
| comida_china | 11 | 0.1 |
| coworking | 2 | 0.0 |
| renta_bicicletas | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| SAN ÁNGEL | 3 | 2,478 | 1,080 | alto |
| GUADALUPE INN | 2 | 5,114 | 929 | alto |
| JARDINES DEL PEDREGAL | 5 | 15,200 | 920 | alto |
| SANTA FE | 4 | 9,229 | 914 | medio |
| SAN BARTOLO AMEYALCO | 3 | 25,819 | 832 | medio |
| TORRES DE POTRERO | 4 | 22,565 | 699 | medio |
| LOMAS DE LA ERA | 3 | 21,181 | 678 | medio |
| MERCED GÓMEZ | 6 | 10,683 | 607 | medio |
| OLIVAR DEL CONDE PRIMERA SECCIÓN | 5 | 16,265 | 586 | medio |
| TIZAPAN | 2 | 7,868 | 562 | medio |

## Colonias de mayor y menor nivel socioeconómico estimado

Solo colonias con 3 000 habitantes o más en sus AGEB. «Decil esperado» es el promedio ponderado por población del decil estimado (1 = más bajo, 10 = más alto de la ZMVM). Es estimación.

Mayor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| JARDINES DEL PEDREGAL | 15,200 | 9.5 |
| LOMAS AXOMIATLA | 5,277 | 9.3 |
| FLORIDA | 5,707 | 9.3 |
| EL RINCÓN | 4,044 | 9.1 |
| SANTA FE LA LOMA | 6,617 | 9.0 |

Menor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| DESARROLLO URBANO | 6,009 | 3.4 |
| CALZADA JALALPA | 5,259 | 3.4 |
| JALALPA TEPITO | 9,377 | 3.9 |
| GOLONDRINAS SEGUNDA SECCIÓN | 4,355 | 4.0 |
| GOLONDRINAS PRIMERA SECCIÓN | 3,528 | 4.0 |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 2,016.3 millones de pesos por trimestre.
- Por hogar: 9,193 pesos por trimestre (lugar 8 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.

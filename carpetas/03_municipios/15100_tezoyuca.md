# Ficha de municipio: Tezoyuca (Estado de México), clave 15100

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 44,280 habitantes (lugar 47 de 76 en la ZMVM). Fuente: INEGI, Censo de Población y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 11,493. AGEB urbanas: 21. Superficie urbana de esas AGEB: 10.8 km².
- Densidad: 4,111 hab/km² (lugar 48 de 76).
- Edad: 0-14 años 25.4 %; 15-24 18.6 %; 25-59 46.9 %; 60 o más 9.0 %.
- Escolaridad promedio de la población de 15 y más: 9.3 años (lugar 66 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 39.4 %; con internet: 41.4 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 75.6 %, medio 24.4 %, alto 0.0 %, sin estimación 0.0 %.
- Decil estimado típico (mediana ponderada por población): 3.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Bajo 14.1 %; Medio 40.8 %; Alto 2.8 %; Muy alto 42.4 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 3,009 (68.0 por cada 1 000 habitantes, lugar 25 de 76). Fuente: INEGI, DENUE (corte 05/2026; histórico 11/2020).
- Establecimientos en el DENUE 11/2020: 2,330. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 11,000.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 1,576 | 52.4 % |
| 81 Otros servicios excepto actividades gubernamentales | 465 | 15.5 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 313 | 10.4 % |
| 31 Industrias manufactureras | 159 | 5.3 % |
| 43 Comercio al por mayor | 118 | 3.9 % |
| 33 Industrias manufactureras | 96 | 3.2 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 497 |
| 812110 | Salones y clínicas de belleza y peluquerías | 155 |
| 465311 | Comercio al por menor de artículos de papelería | 132 |
| 467115 | Comercio al por menor de artículos para la limpieza | 92 |
| 461160 | Comercio al por menor de dulces y materias primas para repostería | 72 |
| 461122 | Comercio al por menor de carne de aves | 67 |
| 467111 | Comercio al por menor en ferreterías y tlapalerías | 65 |
| 464111 | Farmacias sin minisúper | 65 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 63 |
| 461190 | Comercio al por menor de otros alimentos | 57 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 509 | 115.0 |
| barberia_estetica | 155 | 35.0 |
| papeleria | 132 | 29.8 |
| carniceria | 102 | 23.0 |
| taller_mecanico | 76 | 17.2 |
| farmacia | 72 | 16.3 |
| ferreteria | 65 | 14.7 |
| tortilleria | 54 | 12.2 |
| fruteria | 50 | 11.3 |
| fonda | 47 | 10.6 |
| taqueria | 43 | 9.7 |
| purificadora | 43 | 9.7 |
| panaderia | 37 | 8.4 |
| tienda_ropa | 34 | 7.7 |
| cafeteria | 31 | 7.0 |
| heladeria | 22 | 5.0 |
| consultorio_dental | 21 | 4.7 |
| lavanderia | 20 | 4.5 |
| tienda_celulares | 17 | 3.8 |
| gimnasio | 17 | 3.8 |
| cafe_internet | 17 | 3.8 |
| tienda_mascotas | 15 | 3.4 |
| floreria | 15 | 3.4 |
| bar | 13 | 2.9 |
| pizzeria | 11 | 2.5 |
| zapateria | 11 | 2.5 |
| consultorio_medico | 9 | 2.0 |
| pasteleria | 8 | 1.8 |
| veterinaria | 7 | 1.6 |
| cerrajeria | 5 | 1.1 |
| optica | 4 | 0.9 |
| spa | 3 | 0.7 |
| laboratorio_clinico | 2 | 0.5 |
| guarderia | 1 | 0.2 |
| libreria | 0 | 0.0 |
| comida_china | 0 | 0.0 |
| sushi | 0 | 0.0 |
| escuela_idiomas | 0 | 0.0 |
| coworking | 0 | 0.0 |
| renta_bicicletas | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| BUENOS AIRES | 4 | 11,656 | 667 | bajo |
| TEQUISISTLAN PRIMERO | 5 | 10,369 | 563 | bajo |
| PUEBLO DE TEQUISISTLAN | 2 | 4,540 | 539 | medio |
| EJIDOS DE TEQUISISTLAN | 4 | 9,600 | 494 | bajo |
| LA ASCENSION | 1 | 3,447 | 376 | medio |
| SANTIAGO | 2 | 2,789 | 213 | medio |
| SANTA ISABEL IXTAPAN | 1 | 1,840 | 114 | bajo |
| TEQUISISTLAN | 2 | 39 | 38 | medio |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 54.4 millones de pesos por trimestre.
- Por hogar: 4,733 pesos por trimestre (lugar 64 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.

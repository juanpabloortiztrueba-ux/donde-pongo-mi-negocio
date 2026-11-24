# Ficha de municipio: Chiconcuac (Estado de México), clave 15030

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 25,868 habitantes (lugar 56 de 76 en la ZMVM). Fuente: INEGI, Censo de Población y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 5,731. AGEB urbanas: 6. Superficie urbana de esas AGEB: 5.2 km².
- Densidad: 4,954 hab/km² (lugar 40 de 76).
- Edad: 0-14 años 25.6 %; 15-24 17.9 %; 25-59 46.3 %; 60 o más 10.2 %.
- Escolaridad promedio de la población de 15 y más: 10.1 años (lugar 43 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 40.5 %; con internet: 44.4 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 34.3 %, medio 65.7 %, alto 0.0 %.
- Decil estimado típico (mediana ponderada por población): 5.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Medio 72.0 %; Alto 28.0 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 4,438 (171.6 por cada 1 000 habitantes, lugar 1 de 76). Fuente: INEGI, DENUE (corte 05/2026; histórico 11/2020).
- Establecimientos en el DENUE 11/2020: 2,950. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 12,844.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 2,909 | 65.5 % |
| 81 Otros servicios excepto actividades gubernamentales | 336 | 7.6 % |
| 31 Industrias manufactureras | 327 | 7.4 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 297 | 6.7 % |
| 43 Comercio al por mayor | 221 | 5.0 % |
| 32 Industrias manufactureras | 100 | 2.3 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 1,590 |
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 215 |
| 463111 | Comercio al por menor de telas | 147 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 101 |
| 463112 | Comercio al por menor de blancos | 94 |
| 465215 | Comercio al por menor de artículos y aparatos deportivos | 84 |
| 315229 | Confección en serie de otra ropa exterior de materiales textiles | 83 |
| 812110 | Salones y clínicas de belleza y peluquerías | 81 |
| 432111 | Comercio al por mayor de fibras, hilos y telas | 75 |
| 812130 | Sanitarios públicos y bolerías | 71 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| tienda_ropa | 1,590 | 614.7 |
| abarrotes | 224 | 86.6 |
| barberia_estetica | 81 | 31.3 |
| papeleria | 65 | 25.1 |
| carniceria | 62 | 24.0 |
| tortilleria | 48 | 18.6 |
| fonda | 44 | 17.0 |
| fruteria | 38 | 14.7 |
| farmacia | 32 | 12.4 |
| panaderia | 31 | 12.0 |
| cafeteria | 30 | 11.6 |
| taqueria | 29 | 11.2 |
| ferreteria | 27 | 10.4 |
| bar | 24 | 9.3 |
| taller_mecanico | 23 | 8.9 |
| heladeria | 21 | 8.1 |
| tienda_celulares | 17 | 6.6 |
| consultorio_medico | 17 | 6.6 |
| lavanderia | 15 | 5.8 |
| consultorio_dental | 15 | 5.8 |
| floreria | 14 | 5.4 |
| purificadora | 13 | 5.0 |
| zapateria | 12 | 4.6 |
| cafe_internet | 11 | 4.3 |
| pasteleria | 10 | 3.9 |
| pizzeria | 8 | 3.1 |
| gimnasio | 7 | 2.7 |
| tienda_mascotas | 6 | 2.3 |
| veterinaria | 4 | 1.5 |
| cerrajeria | 3 | 1.2 |
| laboratorio_clinico | 3 | 1.2 |
| optica | 2 | 0.8 |
| guarderia | 1 | 0.4 |
| sushi | 1 | 0.4 |
| coworking | 0 | 0.0 |
| renta_bicicletas | 0 | 0.0 |
| comida_china | 0 | 0.0 |
| libreria | 0 | 0.0 |
| escuela_idiomas | 0 | 0.0 |
| spa | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| SAN MIGUEL | 2 | 10,579 | 1,961 | medio |
| SAN PEDRO | 1 | 5,988 | 1,630 | bajo |
| SAN PABLITO CALMIMILOLCO | 1 | 6,418 | 696 | medio |
| LAS JOYAS | 1 | 2,394 | 123 | bajo |
| SAN PABLITO | 1 | 489 | 26 | bajo |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 33.7 millones de pesos por trimestre.
- Por hogar: 5,877 pesos por trimestre (lugar 40 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.

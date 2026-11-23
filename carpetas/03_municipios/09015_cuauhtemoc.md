# Ficha de alcaldía: Cuauhtémoc (Ciudad de México), clave 09015

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 545,884 habitantes (lugar 11 de 76 en la ZMVM). Fuente: INEGI, Censo de Poblacion y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 196,466. AGEB urbanas: 153. Superficie urbana de esas AGEB: 32.3 km².
- Densidad: 16,882 hab/km² (lugar 3 de 76).
- Edad: 0-14 años 15.3 %; 15-24 12.8 %; 25-59 54.7 %; 60 o más 17.2 %.
- Escolaridad promedio de la población de 15 y más: 12.3 años (lugar 4 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 37.7 %; con internet: 80.3 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 97.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 14.8 %, medio 75.3 %, alto 9.9 %, sin estimación 0.0 %.
- Decil estimado típico (mediana ponderada por población): 6.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Muy bajo 25.9 %; Bajo 60.7 %; Medio 10.1 %; Alto 3.3 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 67,535 (123.7 por cada 1 000 habitantes, lugar 3 de 76). Fuente: INEGI, DENUE (corte 05/2026; historico 11/2020).
- Establecimientos en el DENUE 11/2020: 67,920. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 533,206.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 34,304 | 50.8 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 8,675 | 12.8 % |
| 81 Otros servicios excepto actividades gubernamentales | 7,324 | 10.8 % |
| 43 Comercio al por mayor | 2,934 | 4.3 % |
| 62 Servicios de salud y de asistencia social | 2,727 | 4.0 % |
| 54 Servicios profesionales, científicos y técnicos | 2,267 | 3.4 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 4,022 |
| 722511 | Restaurantes con servicio de preparación de alimentos a la carta o de comida corrida | 2,005 |
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 1,967 |
| 466212 | Comercio al por menor de teléfonos y otros aparatos de comunicación | 1,800 |
| 812110 | Salones y clínicas de belleza y peluquerías | 1,759 |
| 722515 | Cafeterías, fuentes de sodas, neverías, refresquerías y similares | 1,577 |
| 323119 | Impresión de formas continuas y otros impresos | 1,496 |
| 465912 | Comercio al por menor de regalos | 1,397 |
| 722514 | Restaurantes con servicio de preparación de tacos y tortas | 1,391 |
| 463215 | Comercio al por menor de bisutería y accesorios de vestir | 1,335 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| tienda_ropa | 4,022 | 73.7 |
| abarrotes | 2,436 | 44.6 |
| fonda | 2,218 | 40.6 |
| tienda_celulares | 1,800 | 33.0 |
| barberia_estetica | 1,759 | 32.2 |
| cafeteria | 1,577 | 28.9 |
| taqueria | 1,391 | 25.5 |
| papeleria | 1,207 | 22.1 |
| consultorio_medico | 1,195 | 21.9 |
| zapateria | 1,187 | 21.7 |
| optica | 1,144 | 21.0 |
| ferreteria | 887 | 16.2 |
| fruteria | 761 | 13.9 |
| carniceria | 718 | 13.2 |
| consultorio_dental | 585 | 10.7 |
| taller_mecanico | 516 | 9.5 |
| farmacia | 455 | 8.3 |
| lavanderia | 360 | 6.6 |
| bar | 322 | 5.9 |
| tortilleria | 310 | 5.7 |
| libreria | 279 | 5.1 |
| cafe_internet | 264 | 4.8 |
| floreria | 250 | 4.6 |
| tienda_mascotas | 192 | 3.5 |
| heladeria | 188 | 3.4 |
| panaderia | 186 | 3.4 |
| cerrajeria | 175 | 3.2 |
| gimnasio | 151 | 2.8 |
| veterinaria | 130 | 2.4 |
| pizzeria | 124 | 2.3 |
| sushi | 124 | 2.3 |
| spa | 122 | 2.2 |
| laboratorio_clinico | 96 | 1.8 |
| purificadora | 88 | 1.6 |
| pasteleria | 59 | 1.1 |
| comida_china | 36 | 0.7 |
| escuela_idiomas | 35 | 0.6 |
| guarderia | 18 | 0.3 |
| coworking | 11 | 0.2 |
| renta_bicicletas | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| CENTRO | 19 | 57,004 | 28,559 | bajo |
| MORELOS | 5 | 38,076 | 4,571 | bajo |
| ROMA NORTE | 9 | 26,196 | 3,945 | medio |
| DOCTORES | 8 | 47,864 | 3,348 | medio |
| JUÁREZ | 6 | 8,542 | 2,932 | medio |
| ROMA SUR | 8 | 20,253 | 2,718 | medio |
| OBRERA | 8 | 36,961 | 2,425 | medio |
| GUERRERO | 6 | 40,858 | 2,116 | medio |
| SANTA MARÍA LA RIBERA | 6 | 42,355 | 2,106 | medio |
| PERALVILLO | 6 | 25,581 | 1,927 | medio |

## Colonias de mayor y menor nivel socioeconómico estimado

Solo colonias con 3 000 habitantes o más en sus AGEB. «Decil esperado» es el promedio ponderado por población del decil estimado (1 = más bajo, 10 = más alto de la ZMVM). Es estimación.

Mayor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| HIPÓDROMO CONDESA | 5,014 | 8.5 |
| CUAUHTÉMOC | 11,558 | 8.4 |
| HIPÓDROMO | 11,272 | 8.3 |
| CONDESA | 6,268 | 8.2 |
| ROMA SUR | 20,253 | 7.8 |

Menor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| MORELOS | 38,076 | 3.3 |
| CENTRO | 57,004 | 4.4 |
| GUERRERO | 40,858 | 5.0 |
| OBRERA | 36,961 | 5.3 |
| BUENAVISTA | 21,494 | 5.3 |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 1,664.4 millones de pesos por trimestre.
- Por hogar: 8,472 pesos por trimestre (lugar 13 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.

# Ficha de municipio: Zumpango (Estado de México), clave 15120

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 255,278 habitantes (lugar 29 de 76 en la ZMVM). Fuente: INEGI, Censo de Población y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 71,306. AGEB urbanas: 76. Superficie urbana de esas AGEB: 57.7 km².
- Densidad: 4,423 hab/km² (lugar 44 de 76).
- Edad: 0-14 años 27.6 %; 15-24 16.8 %; 25-59 48.0 %; 60 o más 7.6 %.
- Escolaridad promedio de la población de 15 y más: 9.8 años (lugar 55 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 33.5 %; con internet: 50.4 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 1.2 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 77.1 %, medio 22.0 %, alto 0.8 %.
- Decil estimado típico (mediana ponderada por población): 3.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Muy bajo 1.2 %; Bajo 13.4 %; Medio 64.0 %; Alto 19.9 %; Muy alto 1.5 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 12,587 (49.3 por cada 1 000 habitantes, lugar 53 de 76). Fuente: INEGI, DENUE (corte 05/2026; histórico 11/2020).
- Establecimientos en el DENUE 11/2020: 8,390. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 48,028.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 6,699 | 53.2 % |
| 81 Otros servicios excepto actividades gubernamentales | 1,680 | 13.3 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 1,259 | 10.0 % |
| 31 Industrias manufactureras | 798 | 6.3 % |
| 62 Servicios de salud y de asistencia social | 442 | 3.5 % |
| 61 Servicios educativos | 318 | 2.5 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 1,798 |
| 812110 | Salones y clínicas de belleza y peluquerías | 635 |
| 465311 | Comercio al por menor de artículos de papelería | 584 |
| 311830 | Elaboración de tortillas de maíz y molienda de nixtamal | 436 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 379 |
| 467115 | Comercio al por menor de artículos para la limpieza | 349 |
| 464111 | Farmacias sin minisúper | 317 |
| 461122 | Comercio al por menor de carne de aves | 270 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 251 |
| 461190 | Comercio al por menor de otros alimentos | 242 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 1,860 | 72.9 |
| barberia_estetica | 635 | 24.9 |
| papeleria | 584 | 22.9 |
| carniceria | 463 | 18.1 |
| tortilleria | 438 | 17.2 |
| tienda_ropa | 379 | 14.8 |
| farmacia | 334 | 13.1 |
| taller_mecanico | 237 | 9.3 |
| fruteria | 230 | 9.0 |
| ferreteria | 221 | 8.7 |
| cafeteria | 187 | 7.3 |
| taqueria | 186 | 7.3 |
| fonda | 164 | 6.4 |
| panaderia | 134 | 5.2 |
| consultorio_dental | 110 | 4.3 |
| cafe_internet | 105 | 4.1 |
| purificadora | 101 | 4.0 |
| heladeria | 89 | 3.5 |
| tienda_celulares | 79 | 3.1 |
| consultorio_medico | 70 | 2.7 |
| bar | 67 | 2.6 |
| floreria | 62 | 2.4 |
| gimnasio | 62 | 2.4 |
| zapateria | 56 | 2.2 |
| pizzeria | 45 | 1.8 |
| tienda_mascotas | 42 | 1.6 |
| lavanderia | 42 | 1.6 |
| pasteleria | 34 | 1.3 |
| veterinaria | 30 | 1.2 |
| laboratorio_clinico | 27 | 1.1 |
| optica | 25 | 1.0 |
| spa | 16 | 0.6 |
| cerrajeria | 15 | 0.6 |
| guarderia | 8 | 0.3 |
| escuela_idiomas | 3 | 0.1 |
| libreria | 3 | 0.1 |
| comida_china | 3 | 0.1 |
| sushi | 3 | 0.1 |
| coworking | 0 | 0.0 |
| renta_bicicletas | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| DE SAN JUAN | 1 | 5,463 | 1,586 | medio |
| DE SAN MIGUEL | 2 | 10,360 | 1,361 | medio |
| SAN BARTOLO CUAUTLALPAN | 3 | 7,879 | 711 | bajo |
| DE SAN LORENZO | 5 | 10,073 | 677 | bajo |
| SAN LORENZO | 1 | 9,172 | 631 | medio |
| SAN SEBASTIAN | 2 | 5,329 | 625 | bajo |
| DE SAN PEDRO DE LA LAGUNA | 2 | 9,143 | 568 | bajo |
| SAN MIGUEL | 1 | 6,508 | 425 | medio |
| VILLAS DE LA LAGUNA | 2 | 15,306 | 419 | bajo |
| DE SANTA MARÍA EL LLANO | 1 | 4,980 | 419 | medio |

## Colonias de mayor y menor nivel socioeconómico estimado

Solo colonias con 3 000 habitantes o más en sus AGEB. «Decil esperado» es el promedio ponderado por población del decil estimado (1 = más bajo, 10 = más alto de la ZMVM). Es estimación.

Mayor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| DE SAN JUAN | 5,463 | 5.2 |
| DE SANTA MARÍA EL LLANO | 4,980 | 5.1 |
| SAN LORENZO | 9,172 | 5.0 |
| DE SAN LORENZO | 10,073 | 5.0 |
| SAN MIGUEL | 6,508 | 4.9 |

Menor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| SANTA ISABEL | 4,196 | 2.4 |
| LA ESMERALDA | 9,057 | 2.8 |
| ARBOLADA LOS SAUCES | 12,388 | 2.8 |
| LA TRINIDAD | 14,721 | 2.8 |
| VILLAS DE LA LAGUNA | 15,306 | 2.9 |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 349.5 millones de pesos por trimestre.
- Por hogar: 4,902 pesos por trimestre (lugar 61 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.

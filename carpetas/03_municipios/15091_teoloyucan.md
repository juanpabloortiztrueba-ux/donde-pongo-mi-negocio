# Ficha de municipio: Teoloyucan (Estado de México), clave 15091

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 58,891 habitantes (lugar 44 de 76 en la ZMVM). Fuente: INEGI, Censo de Población y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 14,582. AGEB urbanas: 15. Superficie urbana de esas AGEB: 16.3 km².
- Densidad: 3,610 hab/km² (lugar 52 de 76).
- Edad: 0-14 años 25.8 %; 15-24 17.4 %; 25-59 45.9 %; 60 o más 10.8 %.
- Escolaridad promedio de la población de 15 y más: 9.7 años (lugar 57 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 40.8 %; con internet: 49.0 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 73.0 %, medio 27.0 %, alto 0.0 %.
- Decil estimado típico (mediana ponderada por población): 4.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Medio 67.0 %; Alto 33.0 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 3,753 (63.7 por cada 1 000 habitantes, lugar 30 de 76). Fuente: INEGI, DENUE (corte 05/2026; histórico 11/2020).
- Establecimientos en el DENUE 11/2020: 3,059. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 13,702.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 1,946 | 51.9 % |
| 81 Otros servicios excepto actividades gubernamentales | 568 | 15.1 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 350 | 9.3 % |
| 31 Industrias manufactureras | 216 | 5.8 % |
| 62 Servicios de salud y de asistencia social | 160 | 4.3 % |
| 61 Servicios educativos | 96 | 2.6 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 466 |
| 812110 | Salones y clínicas de belleza y peluquerías | 210 |
| 465311 | Comercio al por menor de artículos de papelería | 140 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 123 |
| 311830 | Elaboración de tortillas de maíz y molienda de nixtamal | 108 |
| 464111 | Farmacias sin minisúper | 85 |
| 467111 | Comercio al por menor en ferreterías y tlapalerías | 84 |
| 461130 | Comercio al por menor de frutas y verduras frescas | 83 |
| 465912 | Comercio al por menor de regalos | 83 |
| 467115 | Comercio al por menor de artículos para la limpieza | 82 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 484 | 82.2 |
| barberia_estetica | 210 | 35.7 |
| carniceria | 148 | 25.1 |
| papeleria | 140 | 23.8 |
| tienda_ropa | 123 | 20.9 |
| tortilleria | 108 | 18.3 |
| taller_mecanico | 93 | 15.8 |
| farmacia | 91 | 15.5 |
| ferreteria | 84 | 14.3 |
| fruteria | 83 | 14.1 |
| fonda | 68 | 11.5 |
| cafeteria | 56 | 9.5 |
| consultorio_dental | 54 | 9.2 |
| cafe_internet | 41 | 7.0 |
| taqueria | 36 | 6.1 |
| panaderia | 36 | 6.1 |
| purificadora | 28 | 4.8 |
| zapateria | 28 | 4.8 |
| consultorio_medico | 22 | 3.7 |
| tienda_celulares | 22 | 3.7 |
| heladeria | 21 | 3.6 |
| floreria | 18 | 3.1 |
| gimnasio | 17 | 2.9 |
| bar | 15 | 2.5 |
| tienda_mascotas | 13 | 2.2 |
| lavanderia | 13 | 2.2 |
| pizzeria | 11 | 1.9 |
| pasteleria | 11 | 1.9 |
| cerrajeria | 7 | 1.2 |
| veterinaria | 7 | 1.2 |
| optica | 7 | 1.2 |
| laboratorio_clinico | 6 | 1.0 |
| spa | 5 | 0.8 |
| guarderia | 2 | 0.3 |
| comida_china | 1 | 0.2 |
| sushi | 1 | 0.2 |
| escuela_idiomas | 1 | 0.2 |
| renta_bicicletas | 0 | 0.0 |
| coworking | 0 | 0.0 |
| libreria | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| TLATILCO | 2 | 10,773 | 943 | medio |
| TEPANQUIAHUAC | 1 | 7,085 | 517 | medio |
| SANTA CRUZ | 2 | 7,205 | 432 | bajo |
| ZIMAPAN | 1 | 5,472 | 377 | bajo |
| CUAXOXOCA | 2 | 5,931 | 369 | bajo |
| SAN BARTOLO | 1 | 6,063 | 303 | bajo |
| SANTA MARIA | 1 | 7,107 | 291 | bajo |
| SANTO TOMAS | 1 | 3,742 | 220 | bajo |
| SAN JUAN | 1 | 2,534 | 129 | medio |
| LA ERA | 1 | 1,264 | 86 | bajo |

## Colonias de mayor y menor nivel socioeconómico estimado

Solo colonias con 3 000 habitantes o más en sus AGEB. «Decil esperado» es el promedio ponderado por población del decil estimado (1 = más bajo, 10 = más alto de la ZMVM). Es estimación.

Mayor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| TEPANQUIAHUAC | 7,085 | 5.0 |
| TLATILCO | 10,773 | 4.8 |
| SANTA CRUZ | 7,205 | 4.6 |
| ZIMAPAN | 5,472 | 4.4 |
| CUAXOXOCA | 5,931 | 4.3 |

Menor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| SAN BARTOLO | 6,063 | 3.4 |
| SANTO TOMAS | 3,742 | 3.5 |
| SANTA MARIA | 7,107 | 3.8 |
| CUAXOXOCA | 5,931 | 4.3 |
| ZIMAPAN | 5,472 | 4.4 |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 79.6 millones de pesos por trimestre.
- Por hogar: 5,457 pesos por trimestre (lugar 48 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.

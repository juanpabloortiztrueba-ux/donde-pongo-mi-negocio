# Ficha de municipio: Temamatla (Estado de México), clave 15083

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 6,364 habitantes (lugar 73 de 76 en la ZMVM). Fuente: INEGI, Censo de Poblacion y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 1,725. AGEB urbanas: 5. Superficie urbana de esas AGEB: 1.9 km².
- Densidad: 3,350 hab/km² (lugar 55 de 76).
- Edad: 0-14 años 26.9 %; 15-24 16.4 %; 25-59 46.3 %; 60 o más 10.4 %.
- Escolaridad promedio de la población de 15 y más: 10.2 años (lugar 39 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 33.1 %; con internet: 45.4 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 97.9 %, medio 2.1 %, alto 0.0 %.
- Decil estimado típico (mediana ponderada por población): 4.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Bajo 63.7 %; Medio 36.3 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 480 (75.4 por cada 1 000 habitantes, lugar 17 de 76). Fuente: INEGI, DENUE (corte 05/2026; historico 11/2020).
- Establecimientos en el DENUE 11/2020: 395. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 1,666.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 257 | 53.5 % |
| 81 Otros servicios excepto actividades gubernamentales | 71 | 14.8 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 56 | 11.7 % |
| 31 Industrias manufactureras | 26 | 5.4 % |
| 43 Comercio al por mayor | 13 | 2.7 % |
| 62 Servicios de salud y de asistencia social | 12 | 2.5 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 61 |
| 465311 | Comercio al por menor de artículos de papelería | 20 |
| 812110 | Salones y clínicas de belleza y peluquerías | 19 |
| 461130 | Comercio al por menor de frutas y verduras frescas | 15 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 14 |
| 311830 | Elaboración de tortillas de maíz y molienda de nixtamal | 12 |
| 461121 | Comercio al por menor de carnes rojas | 11 |
| 467111 | Comercio al por menor en ferreterías y tlapalerías | 11 |
| 812210 | Lavanderías y tintorerías | 11 |
| 461122 | Comercio al por menor de carne de aves | 11 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 65 | 102.1 |
| carniceria | 22 | 34.6 |
| papeleria | 20 | 31.4 |
| barberia_estetica | 19 | 29.9 |
| fruteria | 15 | 23.6 |
| tienda_ropa | 14 | 22.0 |
| tortilleria | 12 | 18.9 |
| lavanderia | 11 | 17.3 |
| ferreteria | 11 | 17.3 |
| taqueria | 10 | 15.7 |
| farmacia | 10 | 15.7 |
| cafeteria | 8 | 12.6 |
| taller_mecanico | 7 | 11.0 |
| purificadora | 6 | 9.4 |
| fonda | 6 | 9.4 |
| panaderia | 5 | 7.9 |
| bar | 4 | 6.3 |
| cafe_internet | 4 | 6.3 |
| heladeria | 4 | 6.3 |
| gimnasio | 4 | 6.3 |
| pizzeria | 3 | 4.7 |
| consultorio_medico | 3 | 4.7 |
| consultorio_dental | 3 | 4.7 |
| floreria | 3 | 4.7 |
| cerrajeria | 2 | 3.1 |
| pasteleria | 2 | 3.1 |
| guarderia | 1 | 1.6 |
| tienda_celulares | 1 | 1.6 |
| tienda_mascotas | 1 | 1.6 |
| spa | 0 | 0.0 |
| escuela_idiomas | 0 | 0.0 |
| libreria | 0 | 0.0 |
| veterinaria | 0 | 0.0 |
| comida_china | 0 | 0.0 |
| sushi | 0 | 0.0 |
| renta_bicicletas | 0 | 0.0 |
| coworking | 0 | 0.0 |
| zapateria | 0 | 0.0 |
| laboratorio_clinico | 0 | 0.0 |
| optica | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| TEMAMATLA | 4 | 6,255 | 473 | bajo |
| XALPA | 1 | 109 | 3 | bajo |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 8.4 millones de pesos por trimestre.
- Por hogar: 4,881 pesos por trimestre (lugar 62 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.

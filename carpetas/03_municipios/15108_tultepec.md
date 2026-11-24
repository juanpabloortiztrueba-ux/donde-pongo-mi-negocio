# Ficha de municipio: Tultepec (Estado de México), clave 15108

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 150,869 habitantes (lugar 38 de 76 en la ZMVM). Fuente: INEGI, Censo de Población y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 41,036. AGEB urbanas: 42. Superficie urbana de esas AGEB: 17.0 km².
- Densidad: 8,878 hab/km² (lugar 24 de 76).
- Edad: 0-14 años 24.1 %; 15-24 16.7 %; 25-59 49.7 %; 60 o más 9.4 %.
- Escolaridad promedio de la población de 15 y más: 10.7 años (lugar 23 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 48.5 %; con internet: 67.6 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 36.5 %, medio 61.4 %, alto 2.1 %.
- Decil estimado típico (mediana ponderada por población): 6.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Muy bajo 20.6 %; Bajo 29.0 %; Medio 37.8 %; Alto 12.5 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 7,466 (49.5 por cada 1 000 habitantes, lugar 51 de 76). Fuente: INEGI, DENUE (corte 05/2026; histórico 11/2020).
- Establecimientos en el DENUE 11/2020: 5,700. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 26,984.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 3,621 | 48.5 % |
| 81 Otros servicios excepto actividades gubernamentales | 1,129 | 15.1 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 929 | 12.4 % |
| 31 Industrias manufactureras | 381 | 5.1 % |
| 62 Servicios de salud y de asistencia social | 282 | 3.8 % |
| 32 Industrias manufactureras | 240 | 3.2 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 945 |
| 812110 | Salones y clínicas de belleza y peluquerías | 450 |
| 465311 | Comercio al por menor de artículos de papelería | 306 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 194 |
| 467115 | Comercio al por menor de artículos para la limpieza | 193 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 176 |
| 464111 | Farmacias sin minisúper | 159 |
| 461130 | Comercio al por menor de frutas y verduras frescas | 151 |
| 461122 | Comercio al por menor de carne de aves | 150 |
| 461160 | Comercio al por menor de dulces y materias primas para repostería | 138 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 967 | 64.1 |
| barberia_estetica | 450 | 29.8 |
| papeleria | 306 | 20.3 |
| carniceria | 248 | 16.4 |
| taller_mecanico | 191 | 12.7 |
| tienda_ropa | 176 | 11.7 |
| farmacia | 171 | 11.3 |
| fonda | 167 | 11.1 |
| fruteria | 151 | 10.0 |
| cafeteria | 129 | 8.6 |
| taqueria | 124 | 8.2 |
| tortilleria | 118 | 7.8 |
| ferreteria | 116 | 7.7 |
| panaderia | 110 | 7.3 |
| consultorio_dental | 83 | 5.5 |
| purificadora | 72 | 4.8 |
| lavanderia | 60 | 4.0 |
| cafe_internet | 52 | 3.4 |
| consultorio_medico | 46 | 3.0 |
| floreria | 45 | 3.0 |
| tienda_celulares | 44 | 2.9 |
| heladeria | 41 | 2.7 |
| gimnasio | 39 | 2.6 |
| tienda_mascotas | 38 | 2.5 |
| zapateria | 29 | 1.9 |
| veterinaria | 27 | 1.8 |
| bar | 26 | 1.7 |
| optica | 26 | 1.7 |
| pasteleria | 23 | 1.5 |
| pizzeria | 19 | 1.3 |
| cerrajeria | 14 | 0.9 |
| spa | 11 | 0.7 |
| laboratorio_clinico | 11 | 0.7 |
| guarderia | 6 | 0.4 |
| escuela_idiomas | 4 | 0.3 |
| sushi | 4 | 0.3 |
| comida_china | 2 | 0.1 |
| libreria | 1 | 0.1 |
| renta_bicicletas | 0 | 0.0 |
| coworking | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| SANTIAGO TEYAHUALCO | 1 | 15,037 | 921 | medio |
| SAN JUAN XOCOTLA | 2 | 10,695 | 711 | bajo |
| SANTA ISABEL | 1 | 4,770 | 693 | medio |
| HACIENDA REAL DE TULTEPEC | 4 | 19,027 | 682 | medio |
| SAN ANTONIO EL CUADRO | 1 | 3,591 | 571 | medio |
| EL MIRADOR | 2 | 11,390 | 452 | bajo |
| SAN PABLO CTM | 9 | 10,319 | 447 | medio |
| LA PIEDAD | 1 | 10,424 | 433 | bajo |
| SAN MARTIN | 1 | 4,473 | 429 | medio |
| JARDINES SANTA CRUZ | 2 | 6,746 | 313 | bajo |

## Colonias de mayor y menor nivel socioeconómico estimado

Solo colonias con 3 000 habitantes o más en sus AGEB. «Decil esperado» es el promedio ponderado por población del decil estimado (1 = más bajo, 10 = más alto de la ZMVM). Es estimación.

Mayor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| EL DORADO | 3,190 | 8.5 |
| HACIENDA DEL JARDIN | 7,013 | 7.8 |
| PASEOS DE TULTEPEC | 8,667 | 7.6 |
| HACIENDA EL JARDIN 1 | 4,968 | 7.4 |
| HACIENDA REAL DE TULTEPEC | 19,027 | 7.4 |

Menor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| SAN ANTONIO XAHUENTO | 3,470 | 3.0 |
| AMADO NERVO | 4,073 | 3.4 |
| EL MIRADOR | 11,390 | 3.8 |
| TLAMELACA | 3,367 | 3.9 |
| JARDINES SANTA CRUZ | 6,746 | 3.9 |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 328.0 millones de pesos por trimestre.
- Por hogar: 7,993 pesos por trimestre (lugar 19 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.

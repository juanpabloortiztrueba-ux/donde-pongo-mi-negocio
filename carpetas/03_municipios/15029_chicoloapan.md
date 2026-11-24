# Ficha de municipio: Chicoloapan (Estado de México), clave 15029

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 193,532 habitantes (lugar 34 de 76 en la ZMVM). Fuente: INEGI, Censo de Población y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 52,813. AGEB urbanas: 27. Superficie urbana de esas AGEB: 14.0 km².
- Densidad: 13,796 hab/km² (lugar 7 de 76).
- Edad: 0-14 años 24.7 %; 15-24 18.3 %; 25-59 48.2 %; 60 o más 8.8 %.
- Escolaridad promedio de la población de 15 y más: 10.2 años (lugar 38 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 35.6 %; con internet: 64.6 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 9.6 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 52.1 %, medio 47.9 %, alto 0.0 %.
- Decil estimado típico (mediana ponderada por población): 4.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Bajo 48.9 %; Medio 40.4 %; Alto 10.7 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 9,550 (49.3 por cada 1 000 habitantes, lugar 52 de 76). Fuente: INEGI, DENUE (corte 05/2026; histórico 11/2020).
- Establecimientos en el DENUE 11/2020: 7,482. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 34,736.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 5,105 | 53.5 % |
| 81 Otros servicios excepto actividades gubernamentales | 1,547 | 16.2 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 991 | 10.4 % |
| 31 Industrias manufactureras | 424 | 4.4 % |
| 62 Servicios de salud y de asistencia social | 294 | 3.1 % |
| 61 Servicios educativos | 246 | 2.6 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 1,246 |
| 812110 | Salones y clínicas de belleza y peluquerías | 575 |
| 465311 | Comercio al por menor de artículos de papelería | 423 |
| 461130 | Comercio al por menor de frutas y verduras frescas | 287 |
| 464111 | Farmacias sin minisúper | 263 |
| 467115 | Comercio al por menor de artículos para la limpieza | 246 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 230 |
| 461160 | Comercio al por menor de dulces y materias primas para repostería | 209 |
| 461122 | Comercio al por menor de carne de aves | 199 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 186 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 1,309 | 67.6 |
| barberia_estetica | 575 | 29.7 |
| papeleria | 423 | 21.9 |
| carniceria | 322 | 16.6 |
| fruteria | 287 | 14.8 |
| farmacia | 285 | 14.7 |
| taller_mecanico | 229 | 11.8 |
| tienda_ropa | 186 | 9.6 |
| ferreteria | 158 | 8.2 |
| tortilleria | 154 | 8.0 |
| taqueria | 149 | 7.7 |
| fonda | 148 | 7.6 |
| cafeteria | 134 | 6.9 |
| panaderia | 93 | 4.8 |
| purificadora | 91 | 4.7 |
| consultorio_dental | 88 | 4.5 |
| lavanderia | 85 | 4.4 |
| cafe_internet | 69 | 3.6 |
| tienda_mascotas | 64 | 3.3 |
| heladeria | 64 | 3.3 |
| tienda_celulares | 59 | 3.0 |
| floreria | 55 | 2.8 |
| gimnasio | 45 | 2.3 |
| consultorio_medico | 38 | 2.0 |
| bar | 36 | 1.9 |
| pizzeria | 35 | 1.8 |
| cerrajeria | 28 | 1.4 |
| zapateria | 24 | 1.2 |
| veterinaria | 24 | 1.2 |
| optica | 23 | 1.2 |
| pasteleria | 16 | 0.8 |
| spa | 14 | 0.7 |
| laboratorio_clinico | 9 | 0.5 |
| guarderia | 8 | 0.4 |
| escuela_idiomas | 4 | 0.2 |
| comida_china | 3 | 0.2 |
| sushi | 1 | 0.1 |
| libreria | 1 | 0.1 |
| coworking | 0 | 0.0 |
| renta_bicicletas | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| CABECERA MUNICIPAL | 2 | 18,419 | 1,555 | bajo |
| SANTA ROSA | 5 | 17,383 | 950 | bajo |
| BONITO SAN VICENTE | 1 | 21,584 | 723 | bajo |
| FRANCISCO VILLA B | 2 | 11,456 | 681 | bajo |
| EJÉRCITO DEL TRABAJO | 1 | 8,698 | 645 | bajo |
| SAN JOSÉ | 1 | 8,271 | 629 | bajo |
| EL ARENAL I | 1 | 10,630 | 594 | medio |
| REAL DE COSTITLÁN I | 3 | 20,056 | 573 | medio |
| REAL DE SAN VICENTE I | 1 | 11,474 | 498 | medio |
| REVOLUCIÓN | 1 | 5,275 | 498 | bajo |

## Colonias de mayor y menor nivel socioeconómico estimado

Solo colonias con 3 000 habitantes o más en sus AGEB. «Decil esperado» es el promedio ponderado por población del decil estimado (1 = más bajo, 10 = más alto de la ZMVM). Es estimación.

Mayor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| BONITO EL MANZANO | 3,494 | 6.9 |
| PRESIDENTES | 5,333 | 6.8 |
| LOMAS CHICOLOAPAN | 10,333 | 5.4 |
| REAL DE SAN VICENTE I | 11,474 | 5.1 |
| VENUSTIANO CARRANZA | 4,882 | 4.9 |

Menor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| SANTA ROSA | 17,383 | 3.9 |
| REVOLUCIÓN | 5,275 | 4.0 |
| FRANCISCO VILLA B | 11,456 | 4.0 |
| CABECERA MUNICIPAL | 18,419 | 4.2 |
| EJÉRCITO DEL TRABAJO | 8,698 | 4.3 |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 312.9 millones de pesos por trimestre.
- Por hogar: 5,924 pesos por trimestre (lugar 39 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.

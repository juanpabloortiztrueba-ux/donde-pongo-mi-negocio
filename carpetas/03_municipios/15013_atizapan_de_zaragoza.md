# Ficha de municipio: Atizapán de Zaragoza (Estado de México), clave 15013

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 523,065 habitantes (lugar 15 de 76 en la ZMVM). Fuente: INEGI, Censo de Poblacion y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 150,170. AGEB urbanas: 137. Superficie urbana de esas AGEB: 75.0 km².
- Densidad: 6,971 hab/km² (lugar 30 de 76).
- Edad: 0-14 años 20.7 %; 15-24 15.3 %; 25-59 49.4 %; 60 o más 14.3 %.
- Escolaridad promedio de la población de 15 y más: 11.0 años (lugar 17 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 55.6 %; con internet: 72.8 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 34.1 %, medio 41.1 %, alto 24.8 %, sin estimación 0.0 %.
- Decil estimado típico (mediana ponderada por población): 5.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Muy bajo 16.3 %; Bajo 26.8 %; Medio 56.2 %; Alto 0.8 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 22,655 (43.3 por cada 1 000 habitantes, lugar 64 de 76). Fuente: INEGI, DENUE (corte 05/2026; historico 11/2020).
- Establecimientos en el DENUE 11/2020: 19,337. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 115,429.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 10,282 | 45.4 % |
| 81 Otros servicios excepto actividades gubernamentales | 3,844 | 17.0 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 2,852 | 12.6 % |
| 31 Industrias manufactureras | 1,029 | 4.5 % |
| 62 Servicios de salud y de asistencia social | 972 | 4.3 % |
| 43 Comercio al por mayor | 672 | 3.0 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 2,660 |
| 812110 | Salones y clínicas de belleza y peluquerías | 1,567 |
| 465311 | Comercio al por menor de artículos de papelería | 820 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 506 |
| 722514 | Restaurantes con servicio de preparación de tacos y tortas | 486 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 478 |
| 464111 | Farmacias sin minisúper | 467 |
| 461130 | Comercio al por menor de frutas y verduras frescas | 420 |
| 461160 | Comercio al por menor de dulces y materias primas para repostería | 411 |
| 811111 | Reparación mecánica en general de automóviles y camiones | 410 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 2,812 | 53.8 |
| barberia_estetica | 1,567 | 30.0 |
| papeleria | 820 | 15.7 |
| carniceria | 685 | 13.1 |
| taller_mecanico | 623 | 11.9 |
| fonda | 537 | 10.3 |
| farmacia | 514 | 9.8 |
| taqueria | 486 | 9.3 |
| tienda_ropa | 478 | 9.1 |
| fruteria | 420 | 8.0 |
| cafeteria | 400 | 7.6 |
| ferreteria | 358 | 6.8 |
| consultorio_dental | 349 | 6.7 |
| tortilleria | 330 | 6.3 |
| panaderia | 264 | 5.0 |
| lavanderia | 230 | 4.4 |
| cafe_internet | 173 | 3.3 |
| purificadora | 168 | 3.2 |
| gimnasio | 159 | 3.0 |
| tienda_celulares | 149 | 2.8 |
| consultorio_medico | 143 | 2.7 |
| heladeria | 131 | 2.5 |
| veterinaria | 128 | 2.4 |
| bar | 116 | 2.2 |
| floreria | 115 | 2.2 |
| zapateria | 87 | 1.7 |
| tienda_mascotas | 78 | 1.5 |
| cerrajeria | 75 | 1.4 |
| optica | 62 | 1.2 |
| pizzeria | 57 | 1.1 |
| pasteleria | 49 | 0.9 |
| spa | 46 | 0.9 |
| laboratorio_clinico | 38 | 0.7 |
| sushi | 22 | 0.4 |
| guarderia | 19 | 0.4 |
| escuela_idiomas | 10 | 0.2 |
| libreria | 8 | 0.2 |
| comida_china | 5 | 0.1 |
| renta_bicicletas | 0 | 0.0 |
| coworking | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| ATIZAPAN CENTRO | 3 | 10,934 | 1,203 | medio |
| SAN JOSE DEL JARAL | 4 | 26,685 | 1,181 | medio |
| MEXICO NUEVO | 7 | 14,908 | 935 | medio |
| EMILIANO ZAPATA | 4 | 17,708 | 917 | bajo |
| SAN MATEO TECOLOAPAN | 2 | 12,936 | 856 | medio |
| PROFESOR CRISTOBAL HIGUERA | 2 | 15,637 | 856 | bajo |
| SAN JUAN IXTACALA PLANO NORTE | 2 | 11,712 | 720 | medio |
| SAN MIGUEL XOCHIMANGA | 3 | 12,839 | 656 | medio |
| LOMAS DE ATIZAPAN | 4 | 19,077 | 634 | alto |
| AMPLIACION EMILIANO ZAPATA | 3 | 16,450 | 603 | bajo |

## Colonias de mayor y menor nivel socioeconómico estimado

Solo colonias con 3 000 habitantes o más en sus AGEB. «Decil esperado» es el promedio ponderado por población del decil estimado (1 = más bajo, 10 = más alto de la ZMVM). Es estimación.

Mayor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| VALLE DEL CLUB | 6,549 | 9.6 |
| BOSQUE ESMERALDA | 8,949 | 9.6 |
| VALLE ESCONDIDO | 3,010 | 9.5 |
| CONDADO DE SAYAVEDRA | 6,269 | 9.5 |
| CLUB DE GOLF BELLAVISTA | 3,071 | 9.4 |

Menor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| LOMAS DE LAS TORRES | 3,188 | 3.6 |
| PROF CRISTOBAL HIGUERA | 6,011 | 3.6 |
| ATIZAPAN 2000 | 3,793 | 3.8 |
| MIRA FLORES | 4,866 | 3.9 |
| EMILIANO ZAPATA | 17,708 | 3.9 |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 1,377.4 millones de pesos por trimestre.
- Por hogar: 9,172 pesos por trimestre (lugar 9 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.

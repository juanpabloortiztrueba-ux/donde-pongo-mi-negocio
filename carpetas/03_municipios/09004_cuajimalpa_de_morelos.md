# Ficha de alcaldía: Cuajimalpa de Morelos (Ciudad de México), clave 09004

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 212,735 habitantes (lugar 33 de 76 en la ZMVM). Fuente: INEGI, Censo de Población y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 59,151. AGEB urbanas: 31. Superficie urbana de esas AGEB: 32.0 km².
- Densidad: 6,642 hab/km² (lugar 32 de 76).
- Edad: 0-14 años 20.7 %; 15-24 16.0 %; 25-59 51.2 %; 60 o más 12.0 %.
- Escolaridad promedio de la población de 15 y más: 11.4 años (lugar 9 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 52.7 %; con internet: 75.5 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 8.9 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 5.6 %, medio 69.6 %, alto 24.8 %.
- Decil estimado típico (mediana ponderada por población): 7.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Muy bajo 12.2 %; Bajo 61.7 %; Medio 24.7 %; Alto 1.4 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 8,931 (42.0 por cada 1 000 habitantes, lugar 69 de 76). Fuente: INEGI, DENUE (corte 05/2026; histórico 11/2020).
- Establecimientos en el DENUE 11/2020: 9,265. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 101,859.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 3,871 | 43.3 % |
| 81 Otros servicios excepto actividades gubernamentales | 1,244 | 13.9 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 1,098 | 12.3 % |
| 62 Servicios de salud y de asistencia social | 513 | 5.7 % |
| 31 Industrias manufactureras | 332 | 3.7 % |
| 43 Comercio al por mayor | 308 | 3.4 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 913 |
| 812110 | Salones y clínicas de belleza y peluquerías | 487 |
| 465311 | Comercio al por menor de artículos de papelería | 282 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 255 |
| 722514 | Restaurantes con servicio de preparación de tacos y tortas | 192 |
| 722511 | Restaurantes con servicio de preparación de alimentos a la carta o de comida corrida | 179 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 176 |
| 722515 | Cafeterías, fuentes de sodas, neverías, refresquerías y similares | 165 |
| 621113 | Consultorios de medicina especializada del sector privado | 151 |
| 461130 | Comercio al por menor de frutas y verduras frescas | 138 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 985 | 46.3 |
| barberia_estetica | 487 | 22.9 |
| papeleria | 282 | 13.3 |
| tienda_ropa | 255 | 12.0 |
| carniceria | 244 | 11.5 |
| fonda | 243 | 11.4 |
| consultorio_medico | 210 | 9.9 |
| taqueria | 192 | 9.0 |
| cafeteria | 165 | 7.8 |
| taller_mecanico | 154 | 7.2 |
| fruteria | 138 | 6.5 |
| farmacia | 131 | 6.2 |
| ferreteria | 126 | 5.9 |
| consultorio_dental | 110 | 5.2 |
| tortilleria | 110 | 5.2 |
| panaderia | 104 | 4.9 |
| lavanderia | 96 | 4.5 |
| floreria | 70 | 3.3 |
| tienda_celulares | 69 | 3.2 |
| zapateria | 55 | 2.6 |
| gimnasio | 52 | 2.4 |
| tienda_mascotas | 49 | 2.3 |
| heladeria | 43 | 2.0 |
| pasteleria | 42 | 2.0 |
| optica | 42 | 2.0 |
| veterinaria | 40 | 1.9 |
| cerrajeria | 34 | 1.6 |
| cafe_internet | 34 | 1.6 |
| pizzeria | 32 | 1.5 |
| spa | 28 | 1.3 |
| purificadora | 27 | 1.3 |
| laboratorio_clinico | 26 | 1.2 |
| bar | 19 | 0.9 |
| guarderia | 13 | 0.6 |
| sushi | 13 | 0.6 |
| libreria | 6 | 0.3 |
| escuela_idiomas | 5 | 0.2 |
| comida_china | 5 | 0.2 |
| renta_bicicletas | 0 | 0.0 |
| coworking | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| CUAJIMALPA | 4 | 32,620 | 1,550 | medio |
| SANTA FE CUAJIMALPA | 1 | 14,609 | 1,286 | alto |
| SAN JOSÉ DE LOS CEDROS | 4 | 20,940 | 1,283 | medio |
| SAN MATEO TLALTENANGO | 4 | 29,016 | 907 | medio |
| LOMAS DE CHAMIZAL | 2 | 15,766 | 521 | alto |
| BOSQUES DE LAS LOMAS | 1 | 10,984 | 469 | alto |
| GRANJAS NAVIDAD | 2 | 8,979 | 407 | medio |
| LA MANZANITA | 1 | 10,533 | 392 | medio |
| SAN LORENZO ACOPILCO | 2 | 10,955 | 354 | medio |
| LA PILA | 1 | 15,087 | 304 | medio |

## Colonias de mayor y menor nivel socioeconómico estimado

Solo colonias con 3 000 habitantes o más en sus AGEB. «Decil esperado» es el promedio ponderado por población del decil estimado (1 = más bajo, 10 = más alto de la ZMVM). Es estimación.

Mayor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| SANTA FE CUAJIMALPA | 14,609 | 9.4 |
| LOMAS DE CHAMIZAL | 15,766 | 8.6 |
| BOSQUES DE LAS LOMAS | 10,984 | 8.5 |
| LOMAS DE VISTA HERMOSA | 7,494 | 8.5 |
| LAS TINAJAS | 4,941 | 7.5 |

Menor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| SAN PABLO CHIMALPA | 9,466 | 4.3 |
| LA PILA | 15,087 | 4.7 |
| LOMA DEL PADRE | 7,804 | 4.9 |
| GRANJAS NAVIDAD | 8,979 | 5.2 |
| SAN LORENZO ACOPILCO | 10,955 | 5.4 |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 600.2 millones de pesos por trimestre.
- Por hogar: 10,146 pesos por trimestre (lugar 4 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.

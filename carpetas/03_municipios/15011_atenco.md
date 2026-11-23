# Ficha de municipio: Atenco (Estado de México), clave 15011

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 64,683 habitantes (lugar 42 de 76 en la ZMVM). Fuente: INEGI, Censo de Poblacion y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 16,065. AGEB urbanas: 29. Superficie urbana de esas AGEB: 12.3 km².
- Densidad: 5,251 hab/km² (lugar 38 de 76).
- Edad: 0-14 años 25.6 %; 15-24 18.3 %; 25-59 46.8 %; 60 o más 9.3 %.
- Escolaridad promedio de la población de 15 y más: 9.6 años (lugar 60 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 35.8 %; con internet: 47.3 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 75.7 %, medio 24.3 %, alto 0.0 %.
- Decil estimado típico (mediana ponderada por población): 4.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Bajo 15.4 %; Medio 48.9 %; Alto 24.5 %; Muy alto 11.1 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 3,236 (50.0 por cada 1 000 habitantes, lugar 49 de 76). Fuente: INEGI, DENUE (corte 05/2026; historico 11/2020).
- Establecimientos en el DENUE 11/2020: 2,748. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 10,706.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 1,697 | 52.4 % |
| 81 Otros servicios excepto actividades gubernamentales | 454 | 14.0 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 270 | 8.3 % |
| 31 Industrias manufactureras | 236 | 7.3 % |
| 62 Servicios de salud y de asistencia social | 108 | 3.3 % |
| 33 Industrias manufactureras | 86 | 2.7 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 523 |
| 812110 | Salones y clínicas de belleza y peluquerías | 157 |
| 465311 | Comercio al por menor de artículos de papelería | 118 |
| 467115 | Comercio al por menor de artículos para la limpieza | 94 |
| 465912 | Comercio al por menor de regalos | 88 |
| 311830 | Elaboración de tortillas de maíz y molienda de nixtamal | 83 |
| 467111 | Comercio al por menor en ferreterías y tlapalerías | 74 |
| 461122 | Comercio al por menor de carne de aves | 73 |
| 464111 | Farmacias sin minisúper | 69 |
| 461190 | Comercio al por menor de otros alimentos | 61 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 530 | 81.9 |
| barberia_estetica | 157 | 24.3 |
| carniceria | 119 | 18.4 |
| papeleria | 118 | 18.2 |
| tortilleria | 84 | 13.0 |
| farmacia | 75 | 11.6 |
| ferreteria | 74 | 11.4 |
| taller_mecanico | 60 | 9.3 |
| fruteria | 58 | 9.0 |
| purificadora | 50 | 7.7 |
| tienda_ropa | 45 | 7.0 |
| fonda | 38 | 5.9 |
| panaderia | 36 | 5.6 |
| taqueria | 35 | 5.4 |
| cafe_internet | 30 | 4.6 |
| lavanderia | 28 | 4.3 |
| consultorio_dental | 27 | 4.2 |
| cafeteria | 27 | 4.2 |
| tienda_mascotas | 22 | 3.4 |
| gimnasio | 22 | 3.4 |
| consultorio_medico | 21 | 3.2 |
| heladeria | 21 | 3.2 |
| tienda_celulares | 18 | 2.8 |
| bar | 17 | 2.6 |
| zapateria | 13 | 2.0 |
| pasteleria | 12 | 1.9 |
| floreria | 11 | 1.7 |
| pizzeria | 10 | 1.5 |
| guarderia | 7 | 1.1 |
| cerrajeria | 6 | 0.9 |
| optica | 4 | 0.6 |
| laboratorio_clinico | 4 | 0.6 |
| veterinaria | 3 | 0.5 |
| renta_bicicletas | 0 | 0.0 |
| escuela_idiomas | 0 | 0.0 |
| spa | 0 | 0.0 |
| libreria | 0 | 0.0 |
| comida_china | 0 | 0.0 |
| sushi | 0 | 0.0 |
| coworking | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| SAN SALVADOR ATENCO | 4 | 13,908 | 820 | medio |
| SANTA ROSA | 2 | 6,010 | 509 | bajo |
| GRANJAS EL ARENAL | 5 | 8,992 | 477 | bajo |
| SAN CRISTOBAL NEXQUIPAYAC | 5 | 7,744 | 440 | bajo |
| SANTA ISABEL IXTAPAN | 3 | 5,548 | 341 | bajo |
| EL SALADO | 3 | 8,445 | 256 | bajo |
| ZAPOTLAN ATENCO | 1 | 4,137 | 187 | bajo |
| LA PASTORIA | 1 | 3,649 | 147 | bajo |
| EJIDOS DE SANTA ISABEL IXTAPA | 1 | 335 | 18 | bajo |
| SAN SALVADOR | 1 | 306 | 17 | bajo |

## Colonias de mayor y menor nivel socioeconómico estimado

Solo colonias con 3 000 habitantes o más en sus AGEB. «Decil esperado» es el promedio ponderado por población del decil estimado (1 = más bajo, 10 = más alto de la ZMVM). Es estimación.

Mayor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| SAN SALVADOR ATENCO | 13,908 | 5.0 |
| San Salvador Atenco | 3,066 | 4.4 |
| SANTA ISABEL IXTAPAN | 5,548 | 4.2 |
| LA PASTORIA | 3,649 | 4.2 |
| SAN CRISTOBAL NEXQUIPAYAC | 7,744 | 4.1 |

Menor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| EL SALADO | 8,445 | 2.7 |
| GRANJAS EL ARENAL | 8,992 | 2.8 |
| SANTA ROSA | 6,010 | 3.6 |
| ZAPOTLAN ATENCO | 4,137 | 4.0 |
| SAN CRISTOBAL NEXQUIPAYAC | 7,744 | 4.1 |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 80.5 millones de pesos por trimestre.
- Por hogar: 5,011 pesos por trimestre (lugar 57 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.

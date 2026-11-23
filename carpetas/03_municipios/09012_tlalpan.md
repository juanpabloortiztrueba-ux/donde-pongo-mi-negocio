# Ficha de alcaldía: Tlalpan (Ciudad de México), clave 09012

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 681,501 habitantes (lugar 8 de 76 en la ZMVM). Fuente: INEGI, Censo de Poblacion y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 197,448. AGEB urbanas: 207. Superficie urbana de esas AGEB: 93.2 km².
- Densidad: 7,310 hab/km² (lugar 27 de 76).
- Edad: 0-14 años 18.2 %; 15-24 15.7 %; 25-59 50.2 %; 60 o más 15.8 %.
- Escolaridad promedio de la población de 15 y más: 11.5 años (lugar 7 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 54.2 %; con internet: 75.9 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 20.5 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 14.2 %, medio 66.4 %, alto 19.4 %, sin estimación 0.0 %.
- Decil estimado típico (mediana ponderada por población): 7.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Muy bajo 19.3 %; Bajo 52.8 %; Medio 16.0 %; Alto 10.8 %; Muy alto 1.0 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 26,643 (39.1 por cada 1 000 habitantes, lugar 74 de 76). Fuente: INEGI, DENUE (corte 05/2026; historico 11/2020).
- Establecimientos en el DENUE 11/2020: 27,976. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 163,363.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 11,693 | 43.9 % |
| 81 Otros servicios excepto actividades gubernamentales | 4,557 | 17.1 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 3,367 | 12.6 % |
| 62 Servicios de salud y de asistencia social | 1,739 | 6.5 % |
| 31 Industrias manufactureras | 1,214 | 4.6 % |
| 61 Servicios educativos | 741 | 2.8 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 2,944 |
| 812110 | Salones y clínicas de belleza y peluquerías | 1,604 |
| 465311 | Comercio al por menor de artículos de papelería | 834 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 557 |
| 722514 | Restaurantes con servicio de preparación de tacos y tortas | 555 |
| 461122 | Comercio al por menor de carne de aves | 545 |
| 722515 | Cafeterías, fuentes de sodas, neverías, refresquerías y similares | 529 |
| 311830 | Elaboración de tortillas de maíz y molienda de nixtamal | 514 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 509 |
| 621211 | Consultorios dentales del sector privado | 502 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 3,133 | 46.0 |
| barberia_estetica | 1,604 | 23.5 |
| carniceria | 894 | 13.1 |
| papeleria | 834 | 12.2 |
| fonda | 657 | 9.6 |
| taller_mecanico | 585 | 8.6 |
| farmacia | 564 | 8.3 |
| taqueria | 555 | 8.1 |
| cafeteria | 529 | 7.8 |
| tortilleria | 519 | 7.6 |
| consultorio_medico | 513 | 7.5 |
| tienda_ropa | 509 | 7.5 |
| consultorio_dental | 502 | 7.4 |
| fruteria | 471 | 6.9 |
| lavanderia | 437 | 6.4 |
| ferreteria | 394 | 5.8 |
| panaderia | 289 | 4.2 |
| purificadora | 188 | 2.8 |
| tienda_mascotas | 178 | 2.6 |
| tienda_celulares | 176 | 2.6 |
| cafe_internet | 172 | 2.5 |
| floreria | 167 | 2.5 |
| veterinaria | 162 | 2.4 |
| gimnasio | 144 | 2.1 |
| zapateria | 136 | 2.0 |
| heladeria | 134 | 2.0 |
| cerrajeria | 116 | 1.7 |
| optica | 95 | 1.4 |
| pasteleria | 88 | 1.3 |
| pizzeria | 88 | 1.3 |
| laboratorio_clinico | 58 | 0.9 |
| spa | 54 | 0.8 |
| sushi | 54 | 0.8 |
| bar | 48 | 0.7 |
| guarderia | 40 | 0.6 |
| libreria | 19 | 0.3 |
| escuela_idiomas | 11 | 0.2 |
| comida_china | 6 | 0.1 |
| renta_bicicletas | 0 | 0.0 |
| coworking | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| SAN MIGUEL TOPILEJO | 9 | 41,087 | 1,758 | bajo |
| LOMAS DE PADIERNA | 5 | 18,465 | 978 | medio |
| SAN MIGUEL AJUSCO | 8 | 22,367 | 958 | medio |
| PEDREGAL DE SAN NICOLÁS PRIMERA SECCIÓN | 4 | 20,170 | 906 | medio |
| TORIELLO GUERRA | 4 | 9,494 | 852 | medio |
| SAN ANDRÉS TOTOLTEPEC | 4 | 23,244 | 747 | medio |
| PEDREGAL DE SAN NICOLÁS CUARTA SECCIÓN | 5 | 21,976 | 734 | medio |
| HÉROES DE PADIERNA | 5 | 13,731 | 707 | medio |
| SAN PEDRO MÁRTIR | 4 | 16,606 | 703 | medio |
| SAN LORENZO HUIPULCO | 5 | 10,476 | 647 | medio |

## Colonias de mayor y menor nivel socioeconómico estimado

Solo colonias con 3 000 habitantes o más en sus AGEB. «Decil esperado» es el promedio ponderado por población del decil estimado (1 = más bajo, 10 = más alto de la ZMVM). Es estimación.

Mayor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| JARDINES EN LA MONTAÑA | 5,316 | 9.5 |
| VERGEL COAPA | 3,761 | 9.2 |
| FUENTES DEL PEDREGAL | 3,524 | 9.2 |
| RINCONADA LAS HADAS | 3,367 | 9.1 |
| MAGISTERIAL | 3,015 | 9.0 |

Menor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| PARRES EL GUARDA | 3,197 | 3.4 |
| PEDREGAL DE SAN NICOLÁS QUINTA SECCIÓN | 8,186 | 3.8 |
| BOSQUES DEL PEDREGAL | 5,341 | 4.0 |
| SAN MIGUEL TOPILEJO | 41,087 | 4.1 |
| SANTO TOMÁS AJUSCO | 7,742 | 4.2 |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 1,883.7 millones de pesos por trimestre.
- Por hogar: 9,540 pesos por trimestre (lugar 6 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.

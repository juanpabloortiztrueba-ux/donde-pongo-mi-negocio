# Ficha de alcaldía: Iztapalapa (Ciudad de México), clave 09007

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 1,835,486 habitantes (lugar 1 de 76 en la ZMVM). Fuente: INEGI, Censo de Poblacion y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 504,365. AGEB urbanas: 458. Superficie urbana de esas AGEB: 112.4 km².
- Densidad: 16,325 hab/km² (lugar 5 de 76).
- Edad: 0-14 años 20.0 %; 15-24 16.0 %; 25-59 49.7 %; 60 o más 14.3 %.
- Escolaridad promedio de la población de 15 y más: 10.4 años (lugar 31 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 39.1 %; con internet: 69.3 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 59.3 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 37.0 %, medio 60.0 %, alto 3.0 %, sin estimación 0.0 %.
- Decil estimado típico (mediana ponderada por población): 5.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Muy bajo 5.2 %; Bajo 38.9 %; Medio 51.1 %; Alto 4.9 %; Muy alto 0.0 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 88,580 (48.3 por cada 1 000 habitantes, lugar 55 de 76). Fuente: INEGI, DENUE (corte 05/2026; historico 11/2020).
- Establecimientos en el DENUE 11/2020: 85,359. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 440,225.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 43,459 | 49.1 % |
| 81 Otros servicios excepto actividades gubernamentales | 13,953 | 15.8 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 9,570 | 10.8 % |
| 31 Industrias manufactureras | 4,600 | 5.2 % |
| 43 Comercio al por mayor | 3,496 | 3.9 % |
| 62 Servicios de salud y de asistencia social | 3,460 | 3.9 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 9,502 |
| 812110 | Salones y clínicas de belleza y peluquerías | 5,251 |
| 461130 | Comercio al por menor de frutas y verduras frescas | 5,096 |
| 465311 | Comercio al por menor de artículos de papelería | 2,835 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 1,858 |
| 722514 | Restaurantes con servicio de preparación de tacos y tortas | 1,787 |
| 461160 | Comercio al por menor de dulces y materias primas para repostería | 1,693 |
| 464111 | Farmacias sin minisúper | 1,634 |
| 461122 | Comercio al por menor de carne de aves | 1,604 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 1,543 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 9,867 | 53.8 |
| barberia_estetica | 5,251 | 28.6 |
| fruteria | 5,096 | 27.8 |
| carniceria | 2,910 | 15.9 |
| papeleria | 2,835 | 15.4 |
| taller_mecanico | 2,078 | 11.3 |
| farmacia | 1,826 | 9.9 |
| taqueria | 1,787 | 9.7 |
| tienda_ropa | 1,543 | 8.4 |
| fonda | 1,519 | 8.3 |
| cafeteria | 1,508 | 8.2 |
| tortilleria | 1,493 | 8.1 |
| consultorio_dental | 1,296 | 7.1 |
| ferreteria | 1,255 | 6.8 |
| purificadora | 1,187 | 6.5 |
| lavanderia | 946 | 5.2 |
| floreria | 863 | 4.7 |
| panaderia | 831 | 4.5 |
| cafe_internet | 700 | 3.8 |
| consultorio_medico | 587 | 3.2 |
| tienda_mascotas | 541 | 2.9 |
| tienda_celulares | 517 | 2.8 |
| heladeria | 419 | 2.3 |
| zapateria | 396 | 2.2 |
| gimnasio | 396 | 2.2 |
| veterinaria | 364 | 2.0 |
| optica | 270 | 1.5 |
| pizzeria | 269 | 1.5 |
| cerrajeria | 235 | 1.3 |
| pasteleria | 211 | 1.1 |
| spa | 148 | 0.8 |
| bar | 111 | 0.6 |
| laboratorio_clinico | 87 | 0.5 |
| sushi | 50 | 0.3 |
| guarderia | 47 | 0.3 |
| libreria | 26 | 0.1 |
| escuela_idiomas | 22 | 0.1 |
| comida_china | 21 | 0.1 |
| renta_bicicletas | 1 | 0.0 |
| coworking | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| CENTRAL DE ABASTO | 2 | 361 | 8,049 | bajo |
| DESARROLLO URBANO QUETZALCOATL | 12 | 68,354 | 3,079 | bajo |
| SANTA MARÍA AZTAHUACAN | 6 | 33,700 | 2,239 | medio |
| SANTA CRUZ MEYEHUALCO | 10 | 31,640 | 1,995 | medio |
| LOMAS DE SAN LORENZO | 7 | 57,039 | 1,936 | bajo |
| JUAN ESCUTIA | 8 | 22,711 | 1,928 | medio |
| LEYES DE REFORMA TERCERA SECCIÓN | 5 | 31,848 | 1,804 | medio |
| SANTA MARTHA ACATITLA NORTE | 11 | 35,638 | 1,733 | medio |
| SANTIAGO ACAHUALTEPEC SEGUNDA AMPLIACIÓN | 5 | 29,072 | 1,623 | bajo |
| BUENAVISTA | 7 | 43,001 | 1,590 | bajo |

## Colonias de mayor y menor nivel socioeconómico estimado

Solo colonias con 3 000 habitantes o más en sus AGEB. «Decil esperado» es el promedio ponderado por población del decil estimado (1 = más bajo, 10 = más alto de la ZMVM). Es estimación.

Mayor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| CARLOS JONGUITUD BARRIOS | 4,151 | 8.7 |
| PASEOS DE CHURUBUSCO | 8,909 | 8.7 |
| LOMAS ESTRELLA | 16,122 | 8.4 |
| UNIDAD MODELO | 5,815 | 8.3 |
| BANJIDAL | 6,164 | 8.3 |

Menor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| DEGOLLADO | 9,571 | 3.1 |
| SAN MIGUEL TEOTONGO SECCIÓN LOMA ALTA | 3,862 | 3.2 |
| SAN MIGUEL TEOTONGO SECCIÓN IZTLAHUACA | 3,414 | 3.4 |
| SANTA MARTHA ACATITLA | 11,796 | 3.5 |
| SAN MIGUEL TEOTONGO SECCIÓN CORRALES | 3,240 | 3.6 |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 3,474.7 millones de pesos por trimestre.
- Por hogar: 6,890 pesos por trimestre (lugar 26 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.

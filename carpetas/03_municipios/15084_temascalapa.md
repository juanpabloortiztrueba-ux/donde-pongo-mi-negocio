# Ficha de municipio: Temascalapa (Estado de México), clave 15084

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 31,687 habitantes (lugar 53 de 76 en la ZMVM). Fuente: INEGI, Censo de Población y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 8,398. AGEB urbanas: 24. Superficie urbana de esas AGEB: 14.9 km².
- Densidad: 2,126 hab/km² (lugar 65 de 76).
- Edad: 0-14 años 26.1 %; 15-24 17.9 %; 25-59 44.4 %; 60 o más 11.2 %.
- Escolaridad promedio de la población de 15 y más: 9.1 años (lugar 71 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 36.8 %; con internet: 28.0 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 99.9 %, medio 0.0 %, alto 0.0 %, sin estimación 0.0 %.
- Decil estimado típico (mediana ponderada por población): 2.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Bajo 5.7 %; Medio 30.3 %; Alto 55.3 %; Muy alto 8.7 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 2,367 (74.7 por cada 1 000 habitantes, lugar 19 de 76). Fuente: INEGI, DENUE (corte 05/2026; histórico 11/2020).
- Establecimientos en el DENUE 11/2020: 1,959. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 7,706.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 1,279 | 54.0 % |
| 81 Otros servicios excepto actividades gubernamentales | 301 | 12.7 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 232 | 9.8 % |
| 31 Industrias manufactureras | 151 | 6.4 % |
| 62 Servicios de salud y de asistencia social | 87 | 3.7 % |
| 61 Servicios educativos | 65 | 2.7 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 347 |
| 465311 | Comercio al por menor de artículos de papelería | 112 |
| 812110 | Salones y clínicas de belleza y peluquerías | 102 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 70 |
| 465912 | Comercio al por menor de regalos | 69 |
| 311830 | Elaboración de tortillas de maíz y molienda de nixtamal | 57 |
| 467115 | Comercio al por menor de artículos para la limpieza | 55 |
| 467111 | Comercio al por menor en ferreterías y tlapalerías | 53 |
| 461122 | Comercio al por menor de carne de aves | 51 |
| 461160 | Comercio al por menor de dulces y materias primas para repostería | 48 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 353 | 111.4 |
| papeleria | 112 | 35.3 |
| barberia_estetica | 102 | 32.2 |
| carniceria | 82 | 25.9 |
| tienda_ropa | 70 | 22.1 |
| tortilleria | 57 | 18.0 |
| ferreteria | 53 | 16.7 |
| farmacia | 45 | 14.2 |
| taller_mecanico | 45 | 14.2 |
| fruteria | 41 | 12.9 |
| taqueria | 36 | 11.4 |
| panaderia | 32 | 10.1 |
| cafeteria | 31 | 9.8 |
| fonda | 26 | 8.2 |
| floreria | 21 | 6.6 |
| cafe_internet | 19 | 6.0 |
| purificadora | 16 | 5.0 |
| consultorio_medico | 14 | 4.4 |
| tienda_mascotas | 13 | 4.1 |
| bar | 13 | 4.1 |
| consultorio_dental | 13 | 4.1 |
| tienda_celulares | 12 | 3.8 |
| pizzeria | 11 | 3.5 |
| lavanderia | 11 | 3.5 |
| zapateria | 11 | 3.5 |
| heladeria | 9 | 2.8 |
| pasteleria | 4 | 1.3 |
| gimnasio | 4 | 1.3 |
| laboratorio_clinico | 3 | 0.9 |
| cerrajeria | 3 | 0.9 |
| veterinaria | 2 | 0.6 |
| escuela_idiomas | 2 | 0.6 |
| guarderia | 2 | 0.6 |
| spa | 1 | 0.3 |
| sushi | 1 | 0.3 |
| optica | 1 | 0.3 |
| libreria | 0 | 0.0 |
| comida_china | 0 | 0.0 |
| coworking | 0 | 0.0 |
| renta_bicicletas | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| SANTA ANA TLACHIAHUALPA | 4 | 7,171 | 557 | bajo |
| SAN LUIS TECUAUTITLAN | 5 | 6,058 | 410 | bajo |
| IXTLAHUACA DE CUAUHTEMOC | 2 | 3,783 | 263 | bajo |
| DOLORES | 1 | 2,695 | 196 | bajo |
| COYOTEPEC | 1 | 1,886 | 192 | bajo |
| SAN ANTONIO | 1 | 1,792 | 191 | bajo |
| DE LA CRUZ | 1 | 1,422 | 160 | bajo |
| SAN JUAN TEACALCO | 2 | 3,307 | 156 | bajo |
| TEMASCALAPA | 1 | 1,203 | 134 | bajo |
| BUENAVISTA | 1 | 2,184 | 94 | bajo |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 33.6 millones de pesos por trimestre.
- Por hogar: 4,000 pesos por trimestre (lugar 72 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.

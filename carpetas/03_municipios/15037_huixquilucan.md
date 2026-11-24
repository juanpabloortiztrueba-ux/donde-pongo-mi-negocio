# Ficha de municipio: Huixquilucan (Estado de México), clave 15037

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 250,204 habitantes (lugar 30 de 76 en la ZMVM). Fuente: INEGI, Censo de Población y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 73,238. AGEB urbanas: 61. Superficie urbana de esas AGEB: 43.1 km².
- Densidad: 5,812 hab/km² (lugar 37 de 76).
- Edad: 0-14 años 21.7 %; 15-24 16.3 %; 25-59 49.8 %; 60 o más 12.1 %.
- Escolaridad promedio de la población de 15 y más: 11.4 años (lugar 12 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 56.3 %; con internet: 69.6 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 37.0 %, medio 30.7 %, alto 32.3 %.
- Decil estimado típico (mediana ponderada por población): 5.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Muy bajo 31.8 %; Bajo 7.1 %; Medio 46.6 %; Alto 12.8 %; Muy alto 1.7 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 10,551 (42.2 por cada 1 000 habitantes, lugar 68 de 76). Fuente: INEGI, DENUE (corte 05/2026; histórico 11/2020).
- Establecimientos en el DENUE 11/2020: 8,831. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 57,536.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 4,966 | 47.1 % |
| 81 Otros servicios excepto actividades gubernamentales | 1,573 | 14.9 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 1,135 | 10.8 % |
| 62 Servicios de salud y de asistencia social | 751 | 7.1 % |
| 31 Industrias manufactureras | 429 | 4.1 % |
| 61 Servicios educativos | 242 | 2.3 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 1,316 |
| 812110 | Salones y clínicas de belleza y peluquerías | 593 |
| 465311 | Comercio al por menor de artículos de papelería | 389 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 280 |
| 621113 | Consultorios de medicina especializada del sector privado | 237 |
| 722514 | Restaurantes con servicio de preparación de tacos y tortas | 214 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 203 |
| 461122 | Comercio al por menor de carne de aves | 198 |
| 621211 | Consultorios dentales del sector privado | 186 |
| 461160 | Comercio al por menor de dulces y materias primas para repostería | 183 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 1,376 | 55.0 |
| barberia_estetica | 593 | 23.7 |
| papeleria | 389 | 15.5 |
| carniceria | 336 | 13.4 |
| consultorio_medico | 305 | 12.2 |
| tienda_ropa | 280 | 11.2 |
| taller_mecanico | 248 | 9.9 |
| taqueria | 214 | 8.6 |
| fonda | 206 | 8.2 |
| farmacia | 191 | 7.6 |
| consultorio_dental | 186 | 7.4 |
| fruteria | 180 | 7.2 |
| cafeteria | 162 | 6.5 |
| ferreteria | 153 | 6.1 |
| tortilleria | 146 | 5.8 |
| panaderia | 136 | 5.4 |
| lavanderia | 96 | 3.8 |
| cafe_internet | 80 | 3.2 |
| floreria | 69 | 2.8 |
| tienda_celulares | 65 | 2.6 |
| gimnasio | 62 | 2.5 |
| zapateria | 50 | 2.0 |
| heladeria | 49 | 2.0 |
| tienda_mascotas | 43 | 1.7 |
| pasteleria | 40 | 1.6 |
| laboratorio_clinico | 37 | 1.5 |
| purificadora | 33 | 1.3 |
| cerrajeria | 33 | 1.3 |
| bar | 32 | 1.3 |
| optica | 31 | 1.2 |
| veterinaria | 30 | 1.2 |
| pizzeria | 29 | 1.2 |
| spa | 25 | 1.0 |
| guarderia | 12 | 0.5 |
| libreria | 10 | 0.4 |
| sushi | 8 | 0.3 |
| escuela_idiomas | 5 | 0.2 |
| coworking | 1 | 0.0 |
| renta_bicicletas | 0 | 0.0 |
| comida_china | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| SAN FERNANDO | 4 | 24,234 | 1,004 | medio |
| JESUS DEL MONTE | 3 | 30,396 | 911 | alto |
| SAN MARTIN | 1 | 4,375 | 695 | medio |
| HUIXQUILUCAN | 1 | 4,309 | 676 | medio |
| PASEO DE LA HERRADURA | 1 | 5,629 | 567 | alto |
| SANTIAGO YANCUICTLALPAN | 1 | 12,776 | 517 | bajo |
| EL PEDREGAL | 1 | 8,358 | 506 | medio |
| ZACAMULPA | 1 | 8,662 | 442 | bajo |
| FEDERAL BUROCRATICA | 2 | 13,610 | 408 | bajo |
| PIRULES | 1 | 5,128 | 346 | bajo |

## Colonias de mayor y menor nivel socioeconómico estimado

Solo colonias con 3 000 habitantes o más en sus AGEB. «Decil esperado» es el promedio ponderado por población del decil estimado (1 = más bajo, 10 = más alto de la ZMVM). Es estimación.

Mayor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| BOSQUE DE MOCTEZUMA | 3,949 | 9.5 |
| PASEO DE LA HERRADURA | 5,629 | 9.4 |
| FUENTE DEL MIRADOR | 4,404 | 9.4 |
| LA HERRADURA | 3,473 | 9.3 |
| LOMAS ANAHUAC | 4,688 | 9.3 |

Menor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| LA UNIDAD | 4,434 | 3.5 |
| SANTA CRUZ AYOTUXCO | 5,792 | 3.5 |
| BARRIO LAS MAQUINAS | 6,258 | 3.7 |
| EL HIELO | 3,794 | 3.7 |
| SANTIAGO YANCUICTLALPAN | 12,776 | 3.8 |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 742.8 millones de pesos por trimestre.
- Por hogar: 10,142 pesos por trimestre (lugar 5 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.

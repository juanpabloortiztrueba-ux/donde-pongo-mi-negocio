# Ficha de municipio: Tlalnepantla de Baz (Estado de México), clave 15104

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 671,937 habitantes (lugar 9 de 76 en la ZMVM). Fuente: INEGI, Censo de Poblacion y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 199,729. AGEB urbanas: 204. Superficie urbana de esas AGEB: 70.2 km².
- Densidad: 9,572 hab/km² (lugar 22 de 76).
- Edad: 0-14 años 18.7 %; 15-24 15.0 %; 25-59 49.7 %; 60 o más 16.3 %.
- Escolaridad promedio de la población de 15 y más: 10.9 años (lugar 18 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 46.9 %; con internet: 70.5 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 26.6 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 40.7 %, medio 44.5 %, alto 14.8 %, sin estimación 0.0 %.
- Decil estimado típico (mediana ponderada por población): 5.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Muy bajo 15.9 %; Bajo 36.0 %; Medio 39.6 %; Alto 8.6 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 33,393 (49.7 por cada 1 000 habitantes, lugar 50 de 76). Fuente: INEGI, DENUE (corte 05/2026; historico 11/2020).
- Establecimientos en el DENUE 11/2020: 31,175. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 242,912.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 14,112 | 42.3 % |
| 81 Otros servicios excepto actividades gubernamentales | 5,310 | 15.9 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 4,273 | 12.8 % |
| 62 Servicios de salud y de asistencia social | 1,733 | 5.2 % |
| 43 Comercio al por mayor | 1,376 | 4.1 % |
| 31 Industrias manufactureras | 1,354 | 4.1 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 3,435 |
| 812110 | Salones y clínicas de belleza y peluquerías | 1,993 |
| 465311 | Comercio al por menor de artículos de papelería | 948 |
| 722514 | Restaurantes con servicio de preparación de tacos y tortas | 824 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 775 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 675 |
| 722515 | Cafeterías, fuentes de sodas, neverías, refresquerías y similares | 615 |
| 461130 | Comercio al por menor de frutas y verduras frescas | 600 |
| 722518 | Restaurantes que preparan otro tipo de alimentos para llevar | 572 |
| 621211 | Consultorios dentales del sector privado | 569 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 3,642 | 54.2 |
| barberia_estetica | 1,993 | 29.7 |
| carniceria | 1,064 | 15.8 |
| papeleria | 948 | 14.1 |
| taqueria | 824 | 12.3 |
| taller_mecanico | 804 | 12.0 |
| fonda | 730 | 10.9 |
| tienda_ropa | 675 | 10.0 |
| cafeteria | 615 | 9.2 |
| fruteria | 600 | 8.9 |
| farmacia | 577 | 8.6 |
| consultorio_dental | 569 | 8.5 |
| tortilleria | 494 | 7.4 |
| ferreteria | 459 | 6.8 |
| consultorio_medico | 430 | 6.4 |
| lavanderia | 359 | 5.3 |
| panaderia | 278 | 4.1 |
| cafe_internet | 268 | 4.0 |
| tienda_celulares | 226 | 3.4 |
| purificadora | 207 | 3.1 |
| heladeria | 192 | 2.9 |
| bar | 179 | 2.7 |
| gimnasio | 175 | 2.6 |
| zapateria | 162 | 2.4 |
| veterinaria | 155 | 2.3 |
| floreria | 138 | 2.1 |
| tienda_mascotas | 113 | 1.7 |
| optica | 111 | 1.7 |
| cerrajeria | 96 | 1.4 |
| spa | 84 | 1.3 |
| pasteleria | 75 | 1.1 |
| pizzeria | 72 | 1.1 |
| laboratorio_clinico | 69 | 1.0 |
| sushi | 20 | 0.3 |
| guarderia | 16 | 0.2 |
| libreria | 13 | 0.2 |
| escuela_idiomas | 11 | 0.2 |
| comida_china | 9 | 0.1 |
| coworking | 1 | 0.0 |
| renta_bicicletas | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| CENTRO | 3 | 5,549 | 2,383 | medio |
| SAN JUAN IXHUATEPEC | 6 | 31,512 | 1,490 | bajo |
| LAZARO CARDENAS | 8 | 29,755 | 1,250 | bajo |
| CENTRO HISTORICO | 2 | 4,286 | 871 | medio |
| VALLE CEYLAN | 4 | 13,642 | 760 | alto |
| VISTA HERMOSA | 3 | 7,833 | 663 | medio |
| CENTRO INDUSTRIAL | 1 | 284 | 630 | medio |
| SAN LORENZO | 1 | 3,609 | 627 | alto |
| SAN LUCAS TEPETLACALCO | 2 | 4,792 | 615 | medio |
| EX EJIDO DE TEPEOLULCO | 4 | 13,030 | 593 | bajo |

## Colonias de mayor y menor nivel socioeconómico estimado

Solo colonias con 3 000 habitantes o más en sus AGEB. «Decil esperado» es el promedio ponderado por población del decil estimado (1 = más bajo, 10 = más alto de la ZMVM). Es estimación.

Mayor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| FUENTES DE SATELITE 1 JARDIN DE BELLAVISTA | 3,737 | 9.4 |
| MAGISTERIAL VISTA BELLA | 4,030 | 9.2 |
| LOMAS DE VALLE DORADO | 5,812 | 9.2 |
| VALLE DORADO | 10,014 | 9.1 |
| VALLE DE LOS PINOS | 4,503 | 8.9 |

Menor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| LAZARO CARDENAS 2A SECCION | 5,190 | 1.8 |
| LAZARO CARDENAS 2A | 4,659 | 2.6 |
| EX EJIDO DE TEPEOLULCO | 13,030 | 2.8 |
| LAZARO CARDENAS SEGUNDA SECCION | 3,191 | 2.9 |
| LAZARO CARDENAS PRIMERA SECCION | 5,666 | 3.0 |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 1,609.3 millones de pesos por trimestre.
- Por hogar: 8,057 pesos por trimestre (lugar 17 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.

# Ficha de alcaldía: Coyoacán (Ciudad de México), clave 09003

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 614,447 habitantes (lugar 10 de 76 en la ZMVM). Fuente: INEGI, Censo de Población y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 191,517. AGEB urbanas: 156. Superficie urbana de esas AGEB: 53.6 km².
- Densidad: 11,459 hab/km² (lugar 15 de 76).
- Edad: 0-14 años 14.9 %; 15-24 14.1 %; 25-59 50.4 %; 60 o más 20.6 %.
- Escolaridad promedio de la población de 15 y más: 12.5 años (lugar 3 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 56.9 %; con internet: 82.4 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 61.7 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 3.3 %, medio 57.1 %, alto 39.6 %.
- Decil estimado típico (mediana ponderada por población): 8.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Muy bajo 40.4 %; Bajo 49.2 %; Medio 10.3 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 25,011 (40.7 por cada 1 000 habitantes, lugar 70 de 76). Fuente: INEGI, DENUE (corte 05/2026; histórico 11/2020).
- Establecimientos en el DENUE 11/2020: 25,790. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 197,390.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 9,897 | 39.6 % |
| 81 Otros servicios excepto actividades gubernamentales | 4,330 | 17.3 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 3,681 | 14.7 % |
| 62 Servicios de salud y de asistencia social | 1,542 | 6.2 % |
| 61 Servicios educativos | 927 | 3.7 % |
| 31 Industrias manufactureras | 890 | 3.6 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 1,880 |
| 812110 | Salones y clínicas de belleza y peluquerías | 1,619 |
| 722515 | Cafeterías, fuentes de sodas, neverías, refresquerías y similares | 786 |
| 722514 | Restaurantes con servicio de preparación de tacos y tortas | 586 |
| 465311 | Comercio al por menor de artículos de papelería | 570 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 568 |
| 621211 | Consultorios dentales del sector privado | 559 |
| 722511 | Restaurantes con servicio de preparación de alimentos a la carta o de comida corrida | 530 |
| 812210 | Lavanderías y tintorerías | 486 |
| 461122 | Comercio al por menor de carne de aves | 419 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 2,096 | 34.1 |
| barberia_estetica | 1,619 | 26.3 |
| cafeteria | 786 | 12.8 |
| carniceria | 744 | 12.1 |
| fonda | 715 | 11.6 |
| taqueria | 586 | 9.5 |
| papeleria | 570 | 9.3 |
| consultorio_dental | 559 | 9.1 |
| taller_mecanico | 535 | 8.7 |
| lavanderia | 486 | 7.9 |
| farmacia | 427 | 6.9 |
| tienda_ropa | 415 | 6.8 |
| fruteria | 385 | 6.3 |
| tortilleria | 361 | 5.9 |
| consultorio_medico | 315 | 5.1 |
| ferreteria | 278 | 4.5 |
| cafe_internet | 221 | 3.6 |
| panaderia | 204 | 3.3 |
| tienda_celulares | 178 | 2.9 |
| veterinaria | 169 | 2.8 |
| tienda_mascotas | 161 | 2.6 |
| zapateria | 151 | 2.5 |
| heladeria | 150 | 2.4 |
| optica | 125 | 2.0 |
| floreria | 117 | 1.9 |
| cerrajeria | 117 | 1.9 |
| gimnasio | 117 | 1.9 |
| purificadora | 115 | 1.9 |
| pizzeria | 104 | 1.7 |
| spa | 94 | 1.5 |
| laboratorio_clinico | 76 | 1.2 |
| bar | 71 | 1.2 |
| libreria | 63 | 1.0 |
| pasteleria | 52 | 0.8 |
| sushi | 41 | 0.7 |
| guarderia | 22 | 0.4 |
| escuela_idiomas | 21 | 0.3 |
| comida_china | 11 | 0.2 |
| renta_bicicletas | 0 | 0.0 |
| coworking | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| PEDREGAL DE SANTO DOMINGO | 9 | 95,048 | 2,937 | medio |
| AJUSCO | 4 | 35,688 | 2,286 | medio |
| PEDREGAL DE SANTA ÚRSULA | 7 | 47,031 | 1,834 | medio |
| DEL CARMEN | 5 | 11,556 | 1,142 | alto |
| VILLA COYOACÁN | 2 | 4,261 | 958 | alto |
| CAMPESTRE CHURUBUSCO | 5 | 12,678 | 923 | alto |
| UNIVERSIDAD NACIONAL AUTÓNOMA DE MÉXICO CIUDAD UNIVERSITARIA | 1 | 326 | 770 | alto |
| EX-EJIDO DE SAN FRANCISCO CULHUACÁN | 4 | 10,849 | 544 | medio |
| AVANTE | 3 | 11,638 | 511 | alto |
| ADOLFO RUIZ CORTINES | 3 | 17,071 | 498 | medio |

## Colonias de mayor y menor nivel socioeconómico estimado

Solo colonias con 3 000 habitantes o más en sus AGEB. «Decil esperado» es el promedio ponderado por población del decil estimado (1 = más bajo, 10 = más alto de la ZMVM). Es estimación.

Mayor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| SANTA CECILIA | 3,249 | 9.3 |
| PRESIDENTES EJIDALES SEGUNDA SECCIÓN | 5,005 | 9.1 |
| INSURGENTES CUICUILCO | 8,493 | 9.0 |
| VILLA QUIETUD | 5,787 | 9.0 |
| SANTA CATARINA | 3,183 | 9.0 |

Menor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| SAN FRANCISCO CULHUACÁN BARRIO DE SAN FRANCISCO | 7,695 | 4.0 |
| CARMEN SERDÁN | 7,824 | 4.3 |
| SAN FRANCISCO CULHUACÁN BARRIO DE SANTA ANA | 7,676 | 4.8 |
| PEDREGAL DE SANTO DOMINGO | 95,048 | 5.3 |
| EMILIANO ZAPATA | 6,044 | 5.3 |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 2,120.2 millones de pesos por trimestre.
- Por hogar: 11,070 pesos por trimestre (lugar 3 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.

# Ficha de alcaldía: Venustiano Carranza (Ciudad de México), clave 09017

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 443,704 habitantes (lugar 17 de 76 en la ZMVM). Fuente: INEGI, Censo de Poblacion y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 135,767. AGEB urbanas: 151. Superficie urbana de esas AGEB: 33.7 km².
- Densidad: 13,180 hab/km² (lugar 12 de 76).
- Edad: 0-14 años 17.6 %; 15-24 14.2 %; 25-59 50.3 %; 60 o más 17.8 %.
- Escolaridad promedio de la población de 15 y más: 11.4 años (lugar 10 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 40.5 %; con internet: 75.1 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 98.4 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 15.9 %, medio 80.1 %, alto 3.9 %, sin estimación 0.0 %.
- Decil estimado típico (mediana ponderada por población): 6.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Muy bajo 13.4 %; Bajo 63.1 %; Medio 22.3 %; Alto 1.0 %; Muy alto 0.2 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 30,734 (69.3 por cada 1 000 habitantes, lugar 24 de 76). Fuente: INEGI, DENUE (corte 05/2026; historico 11/2020).
- Establecimientos en el DENUE 11/2020: 31,590. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 169,484.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 16,859 | 54.9 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 4,159 | 13.5 % |
| 81 Otros servicios excepto actividades gubernamentales | 3,566 | 11.6 % |
| 31 Industrias manufactureras | 994 | 3.2 % |
| 62 Servicios de salud y de asistencia social | 992 | 3.2 % |
| 43 Comercio al por mayor | 716 | 2.3 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 2,043 |
| 461130 | Comercio al por menor de frutas y verduras frescas | 1,935 |
| 812110 | Salones y clínicas de belleza y peluquerías | 1,211 |
| 461121 | Comercio al por menor de carnes rojas | 964 |
| 722514 | Restaurantes con servicio de preparación de tacos y tortas | 867 |
| 461160 | Comercio al por menor de dulces y materias primas para repostería | 841 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 823 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 782 |
| 465212 | Comercio al por menor de juguetes | 711 |
| 722515 | Cafeterías, fuentes de sodas, neverías, refresquerías y similares | 691 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 2,252 | 50.8 |
| fruteria | 1,935 | 43.6 |
| carniceria | 1,381 | 31.1 |
| barberia_estetica | 1,211 | 27.3 |
| taqueria | 867 | 19.5 |
| tienda_ropa | 823 | 18.5 |
| cafeteria | 691 | 15.6 |
| fonda | 671 | 15.1 |
| papeleria | 579 | 13.0 |
| floreria | 509 | 11.5 |
| taller_mecanico | 496 | 11.2 |
| tienda_mascotas | 445 | 10.0 |
| consultorio_dental | 367 | 8.3 |
| farmacia | 365 | 8.2 |
| zapateria | 351 | 7.9 |
| tortilleria | 319 | 7.2 |
| lavanderia | 302 | 6.8 |
| ferreteria | 248 | 5.6 |
| tienda_celulares | 216 | 4.9 |
| purificadora | 171 | 3.9 |
| panaderia | 163 | 3.7 |
| consultorio_medico | 154 | 3.5 |
| cafe_internet | 145 | 3.3 |
| veterinaria | 127 | 2.9 |
| heladeria | 124 | 2.8 |
| optica | 90 | 2.0 |
| bar | 85 | 1.9 |
| gimnasio | 79 | 1.8 |
| cerrajeria | 76 | 1.7 |
| pizzeria | 58 | 1.3 |
| spa | 46 | 1.0 |
| pasteleria | 33 | 0.7 |
| laboratorio_clinico | 28 | 0.6 |
| sushi | 23 | 0.5 |
| libreria | 20 | 0.5 |
| comida_china | 13 | 0.3 |
| guarderia | 9 | 0.2 |
| escuela_idiomas | 8 | 0.2 |
| renta_bicicletas | 1 | 0.0 |
| coworking | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| ZONA CENTRO | 6 | 18,079 | 6,933 | bajo |
| MOCTEZUMA SEGUNDA SECCIÓN | 11 | 46,231 | 2,265 | medio |
| JARDÍN BALBUENA | 33 | 44,410 | 1,536 | medio |
| JAMAICA | 1 | 4,440 | 1,381 | medio |
| MORELOS | 4 | 35,178 | 1,361 | bajo |
| GENERAL IGNACIO ZARAGOZA | 5 | 14,632 | 1,051 | medio |
| FELIPE ÁNGELES | 1 | 3,850 | 978 | medio |
| ADOLFO LÓPEZ MATEOS | 2 | 7,612 | 883 | medio |
| MERCED BALBUENA | 2 | 4,439 | 845 | medio |
| PENSADOR MEXICANO | 4 | 11,866 | 780 | medio |

## Colonias de mayor y menor nivel socioeconómico estimado

Solo colonias con 3 000 habitantes o más en sus AGEB. «Decil esperado» es el promedio ponderado por población del decil estimado (1 = más bajo, 10 = más alto de la ZMVM). Es estimación.

Mayor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| JARDÍN BALBUENA | 44,410 | 7.6 |
| DEL PARQUE | 3,172 | 7.3 |
| JAMAICA | 4,440 | 7.2 |
| POPULAR RASTRO | 10,277 | 7.1 |
| ÁLVARO OBREGÓN | 3,109 | 7.0 |

Menor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| MORELOS | 35,178 | 3.7 |
| ZONA CENTRO | 18,079 | 4.0 |
| AMPLIACIÓN PENITENCIARIA | 4,947 | 4.2 |
| DAMIÁN CARMONA | 3,631 | 4.4 |
| PEÑÓN DE LOS BAÑOS | 7,700 | 4.7 |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 1,072.1 millones de pesos por trimestre.
- Por hogar: 7,897 pesos por trimestre (lugar 20 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.

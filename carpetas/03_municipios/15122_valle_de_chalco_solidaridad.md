# Ficha de municipio: Valle de Chalco Solidaridad (Estado de México), clave 15122

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 390,901 habitantes (lugar 23 de 76 en la ZMVM). Fuente: INEGI, Censo de Población y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 104,207. AGEB urbanas: 113. Superficie urbana de esas AGEB: 28.5 km².
- Densidad: 13,709 hab/km² (lugar 8 de 76).
- Edad: 0-14 años 26.7 %; 15-24 17.1 %; 25-59 46.3 %; 60 o más 9.9 %.
- Escolaridad promedio de la población de 15 y más: 9.1 años (lugar 70 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 26.8 %; con internet: 55.8 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 98.2 %, medio 1.8 %, alto 0.0 %.
- Decil estimado típico (mediana ponderada por población): 3.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Bajo 1.4 %; Medio 27.9 %; Alto 67.3 %; Muy alto 3.3 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 20,279 (51.9 por cada 1 000 habitantes, lugar 47 de 76). Fuente: INEGI, DENUE (corte 05/2026; histórico 11/2020).
- Establecimientos en el DENUE 11/2020: 18,712. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 69,190.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 10,516 | 51.9 % |
| 81 Otros servicios excepto actividades gubernamentales | 3,187 | 15.7 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 2,164 | 10.7 % |
| 31 Industrias manufactureras | 1,163 | 5.7 % |
| 62 Servicios de salud y de asistencia social | 644 | 3.2 % |
| 61 Servicios educativos | 473 | 2.3 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 3,014 |
| 812110 | Salones y clínicas de belleza y peluquerías | 1,142 |
| 465311 | Comercio al por menor de artículos de papelería | 867 |
| 467115 | Comercio al por menor de artículos para la limpieza | 543 |
| 461160 | Comercio al por menor de dulces y materias primas para repostería | 471 |
| 461130 | Comercio al por menor de frutas y verduras frescas | 420 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 406 |
| 464111 | Farmacias sin minisúper | 398 |
| 461122 | Comercio al por menor de carne de aves | 391 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 382 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 3,080 | 78.8 |
| barberia_estetica | 1,142 | 29.2 |
| papeleria | 867 | 22.2 |
| carniceria | 637 | 16.3 |
| farmacia | 437 | 11.2 |
| taller_mecanico | 432 | 11.1 |
| fruteria | 420 | 10.7 |
| fonda | 418 | 10.7 |
| tienda_ropa | 382 | 9.8 |
| taqueria | 354 | 9.1 |
| ferreteria | 354 | 9.1 |
| tortilleria | 346 | 8.9 |
| cafeteria | 334 | 8.5 |
| purificadora | 324 | 8.3 |
| panaderia | 244 | 6.2 |
| cafe_internet | 219 | 5.6 |
| consultorio_dental | 170 | 4.3 |
| gimnasio | 120 | 3.1 |
| lavanderia | 119 | 3.0 |
| heladeria | 112 | 2.9 |
| tienda_celulares | 106 | 2.7 |
| tienda_mascotas | 103 | 2.6 |
| consultorio_medico | 90 | 2.3 |
| floreria | 85 | 2.2 |
| pizzeria | 73 | 1.9 |
| zapateria | 72 | 1.8 |
| bar | 63 | 1.6 |
| veterinaria | 47 | 1.2 |
| pasteleria | 44 | 1.1 |
| optica | 44 | 1.1 |
| cerrajeria | 35 | 0.9 |
| spa | 22 | 0.6 |
| laboratorio_clinico | 21 | 0.5 |
| sushi | 10 | 0.3 |
| guarderia | 9 | 0.2 |
| libreria | 6 | 0.2 |
| escuela_idiomas | 6 | 0.2 |
| comida_china | 4 | 0.1 |
| renta_bicicletas | 0 | 0.0 |
| coworking | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| SAN ISIDRO | 8 | 26,950 | 1,700 | bajo |
| SANTA CRUZ | 9 | 28,037 | 1,545 | bajo |
| SAN MIGUEL XICO SEGUNDA SECCIÓN | 3 | 18,792 | 1,157 | bajo |
| PROVIDENCIA | 4 | 19,439 | 1,131 | bajo |
| MARÍA ISABEL | 6 | 20,520 | 953 | bajo |
| INDEPENDENCIA | 5 | 15,867 | 898 | bajo |
| GUADALUPANA SEGUNDA SECCIÓN | 4 | 15,782 | 849 | bajo |
| NIÑOS HÉROES PRIMERA SECCIÓN | 5 | 15,978 | 831 | bajo |
| CONCEPCIÓN | 6 | 15,744 | 794 | bajo |
| SANTIAGO | 4 | 14,356 | 771 | bajo |

## Colonias de mayor y menor nivel socioeconómico estimado

Solo colonias con 3 000 habitantes o más en sus AGEB. «Decil esperado» es el promedio ponderado por población del decil estimado (1 = más bajo, 10 = más alto de la ZMVM). Es estimación.

Mayor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| LA ASUNCIÓN | 5,566 | 5.4 |
| SAN JUAN TLALPIZÁHUAC | 5,303 | 4.0 |
| AVÁNDARO | 7,217 | 3.9 |
| DARIO MARTÍNEZ PRIMERA SECCIÓN | 12,495 | 3.9 |
| DARIO MARTÍNEZ SEGUNDA SECCIÓN | 14,120 | 3.9 |

Menor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| SAN MIGUEL LAS TABLAS | 5,681 | 2.6 |
| CERRO DEL MARQUEZ | 6,806 | 2.6 |
| GUADALUPANA PRIMERA SECCIÓN | 16,397 | 2.8 |
| SAN MARTÍN XICO LA LAGUNA | 3,073 | 2.9 |
| GUADALUPANA SEGUNDA SECCIÓN | 15,782 | 3.0 |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 462.2 millones de pesos por trimestre.
- Por hogar: 4,435 pesos por trimestre (lugar 69 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.

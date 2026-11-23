# Ficha de municipio: Tlalmanalco (Estado de México), clave 15103

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 39,728 habitantes (lugar 50 de 76 en la ZMVM). Fuente: INEGI, Censo de Poblacion y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 10,344. AGEB urbanas: 25. Superficie urbana de esas AGEB: 9.5 km².
- Densidad: 4,174 hab/km² (lugar 46 de 76).
- Edad: 0-14 años 22.8 %; 15-24 16.1 %; 25-59 47.0 %; 60 o más 13.9 %.
- Escolaridad promedio de la población de 15 y más: 10.5 años (lugar 29 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 34.4 %; con internet: 52.7 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 56.3 %, medio 43.7 %, alto 0.0 %.
- Decil estimado típico (mediana ponderada por población): 4.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Bajo 58.4 %; Medio 31.8 %; Alto 9.7 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 2,245 (56.5 por cada 1 000 habitantes, lugar 40 de 76). Fuente: INEGI, DENUE (corte 05/2026; historico 11/2020).
- Establecimientos en el DENUE 11/2020: 1,929. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 8,026.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 1,217 | 54.2 % |
| 81 Otros servicios excepto actividades gubernamentales | 307 | 13.7 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 246 | 11.0 % |
| 31 Industrias manufactureras | 91 | 4.1 % |
| 62 Servicios de salud y de asistencia social | 75 | 3.3 % |
| 61 Servicios educativos | 68 | 3.0 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 351 |
| 812110 | Salones y clínicas de belleza y peluquerías | 114 |
| 465311 | Comercio al por menor de artículos de papelería | 102 |
| 461130 | Comercio al por menor de frutas y verduras frescas | 64 |
| 461160 | Comercio al por menor de dulces y materias primas para repostería | 64 |
| 461122 | Comercio al por menor de carne de aves | 64 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 58 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 51 |
| 722514 | Restaurantes con servicio de preparación de tacos y tortas | 50 |
| 465912 | Comercio al por menor de regalos | 42 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 362 | 91.1 |
| barberia_estetica | 114 | 28.7 |
| carniceria | 106 | 26.7 |
| papeleria | 102 | 25.7 |
| fruteria | 64 | 16.1 |
| tienda_ropa | 58 | 14.6 |
| taqueria | 50 | 12.6 |
| farmacia | 42 | 10.6 |
| ferreteria | 39 | 9.8 |
| fonda | 39 | 9.8 |
| taller_mecanico | 38 | 9.6 |
| cafeteria | 35 | 8.8 |
| tortilleria | 35 | 8.8 |
| consultorio_dental | 23 | 5.8 |
| panaderia | 23 | 5.8 |
| cafe_internet | 22 | 5.5 |
| purificadora | 21 | 5.3 |
| gimnasio | 18 | 4.5 |
| consultorio_medico | 15 | 3.8 |
| heladeria | 15 | 3.8 |
| tienda_celulares | 15 | 3.8 |
| tienda_mascotas | 13 | 3.3 |
| lavanderia | 12 | 3.0 |
| floreria | 11 | 2.8 |
| zapateria | 10 | 2.5 |
| pizzeria | 9 | 2.3 |
| bar | 8 | 2.0 |
| veterinaria | 6 | 1.5 |
| optica | 6 | 1.5 |
| spa | 5 | 1.3 |
| pasteleria | 5 | 1.3 |
| laboratorio_clinico | 4 | 1.0 |
| libreria | 2 | 0.5 |
| guarderia | 2 | 0.5 |
| escuela_idiomas | 1 | 0.3 |
| sushi | 1 | 0.3 |
| cerrajeria | 1 | 0.3 |
| renta_bicicletas | 0 | 0.0 |
| comida_china | 0 | 0.0 |
| coworking | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| CENTRO | 2 | 4,435 | 571 | medio |
| TLALMANALCO | 1 | 4,760 | 417 | medio |
| SAN RAFAEL CENTRO | 1 | 2,940 | 236 | bajo |
| PUEBLO NUEVO | 1 | 3,785 | 191 | bajo |
| SAN JUAN ATZACUALOYA | 2 | 4,520 | 161 | medio |
| SAN LORENZO TLALMIMILOLPAN | 2 | 2,853 | 126 | bajo |
| OBRERA | 2 | 1,869 | 122 | medio |
| BARRIO ALTO | 1 | 3,867 | 107 | bajo |
| TEZOPILO | 1 | 2,188 | 79 | medio |
| SAN PEDRO | 1 | 1,344 | 45 | bajo |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 58.2 millones de pesos por trimestre.
- Por hogar: 5,630 pesos por trimestre (lugar 44 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.

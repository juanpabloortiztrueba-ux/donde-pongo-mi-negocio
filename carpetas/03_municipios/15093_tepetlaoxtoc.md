# Ficha de municipio: Tepetlaoxtoc (Estado de México), clave 15093

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 17,510 habitantes (lugar 62 de 76 en la ZMVM). Fuente: INEGI, Censo de Población y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 4,544. AGEB urbanas: 14. Superficie urbana de esas AGEB: 11.6 km².
- Densidad: 1,506 hab/km² (lugar 74 de 76).
- Edad: 0-14 años 24.8 %; 15-24 17.1 %; 25-59 45.8 %; 60 o más 12.0 %.
- Escolaridad promedio de la población de 15 y más: 9.9 años (lugar 53 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 48.2 %; con internet: 43.5 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 71.5 %, medio 27.6 %, alto 0.9 %.
- Decil estimado típico (mediana ponderada por población): 4.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Bajo 0.9 %; Medio 74.9 %; Alto 24.2 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 1,220 (69.7 por cada 1 000 habitantes, lugar 23 de 76). Fuente: INEGI, DENUE (corte 05/2026; histórico 11/2020).
- Establecimientos en el DENUE 11/2020: 1,005. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 4,534.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 560 | 45.9 % |
| 81 Otros servicios excepto actividades gubernamentales | 159 | 13.0 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 125 | 10.2 % |
| 31 Industrias manufactureras | 100 | 8.2 % |
| 32 Industrias manufactureras | 68 | 5.6 % |
| 62 Servicios de salud y de asistencia social | 35 | 2.9 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 197 |
| 812110 | Salones y clínicas de belleza y peluquerías | 53 |
| 465311 | Comercio al por menor de artículos de papelería | 47 |
| 327420 | Fabricación de yeso y productos de yeso | 45 |
| 315229 | Confección en serie de otra ropa exterior de materiales textiles | 34 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 31 |
| 467115 | Comercio al por menor de artículos para la limpieza | 25 |
| 461130 | Comercio al por menor de frutas y verduras frescas | 24 |
| 465912 | Comercio al por menor de regalos | 24 |
| 467111 | Comercio al por menor en ferreterías y tlapalerías | 23 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 199 | 113.6 |
| barberia_estetica | 53 | 30.3 |
| papeleria | 47 | 26.8 |
| carniceria | 44 | 25.1 |
| fruteria | 24 | 13.7 |
| ferreteria | 23 | 13.1 |
| tienda_ropa | 21 | 12.0 |
| farmacia | 21 | 12.0 |
| taller_mecanico | 21 | 12.0 |
| tortilleria | 17 | 9.7 |
| taqueria | 17 | 9.7 |
| cafeteria | 17 | 9.7 |
| cafe_internet | 15 | 8.6 |
| bar | 13 | 7.4 |
| panaderia | 12 | 6.9 |
| heladeria | 11 | 6.3 |
| consultorio_dental | 11 | 6.3 |
| lavanderia | 10 | 5.7 |
| fonda | 10 | 5.7 |
| consultorio_medico | 6 | 3.4 |
| purificadora | 6 | 3.4 |
| gimnasio | 5 | 2.9 |
| tienda_celulares | 4 | 2.3 |
| tienda_mascotas | 4 | 2.3 |
| floreria | 4 | 2.3 |
| veterinaria | 3 | 1.7 |
| spa | 3 | 1.7 |
| pasteleria | 3 | 1.7 |
| zapateria | 3 | 1.7 |
| pizzeria | 2 | 1.1 |
| cerrajeria | 1 | 0.6 |
| sushi | 1 | 0.6 |
| laboratorio_clinico | 1 | 0.6 |
| escuela_idiomas | 0 | 0.0 |
| guarderia | 0 | 0.0 |
| libreria | 0 | 0.0 |
| comida_china | 0 | 0.0 |
| optica | 0 | 0.0 |
| coworking | 0 | 0.0 |
| renta_bicicletas | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| SANTO TOMAS APIPILHUASCO | 1 | 4,234 | 217 | bajo |
| CENTRO | 1 | 658 | 191 | medio |
| LA CONCEPCION | 1 | 2,809 | 180 | bajo |
| SAN PABLO JOLALPAN | 2 | 1,755 | 171 | bajo |
| SAN PABLO | 2 | 1,606 | 137 | bajo |
| EL CALVARIO | 1 | 2,198 | 129 | bajo |
| LA ASUNCION | 2 | 1,900 | 109 | medio |
| SAN VICENTE | 1 | 1,201 | 43 | medio |
| LA SANTISIMA | 2 | 781 | 34 | medio |
| EL PROGRESO | 1 | 368 | 5 | medio |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 24.8 millones de pesos por trimestre.
- Por hogar: 5,466 pesos por trimestre (lugar 47 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.

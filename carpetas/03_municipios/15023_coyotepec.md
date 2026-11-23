# Ficha de municipio: Coyotepec (Estado de México), clave 15023

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 37,442 habitantes (lugar 51 de 76 en la ZMVM). Fuente: INEGI, Censo de Poblacion y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 9,046. AGEB urbanas: 12. Superficie urbana de esas AGEB: 10.6 km².
- Densidad: 3,549 hab/km² (lugar 53 de 76).
- Edad: 0-14 años 26.5 %; 15-24 17.9 %; 25-59 46.1 %; 60 o más 9.5 %.
- Escolaridad promedio de la población de 15 y más: 9.6 años (lugar 58 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 37.9 %; con internet: 44.5 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 63.6 %, medio 36.4 %, alto 0.0 %.
- Decil estimado típico (mediana ponderada por población): 4.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Medio 93.0 %; Alto 7.0 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 2,447 (65.4 por cada 1 000 habitantes, lugar 27 de 76). Fuente: INEGI, DENUE (corte 05/2026; historico 11/2020).
- Establecimientos en el DENUE 11/2020: 1,752. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 7,768.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 1,310 | 53.5 % |
| 81 Otros servicios excepto actividades gubernamentales | 364 | 14.9 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 224 | 9.2 % |
| 31 Industrias manufactureras | 171 | 7.0 % |
| 62 Servicios de salud y de asistencia social | 73 | 3.0 % |
| 32 Industrias manufactureras | 53 | 2.2 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 387 |
| 812110 | Salones y clínicas de belleza y peluquerías | 122 |
| 465311 | Comercio al por menor de artículos de papelería | 107 |
| 311830 | Elaboración de tortillas de maíz y molienda de nixtamal | 95 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 73 |
| 467111 | Comercio al por menor en ferreterías y tlapalerías | 61 |
| 465912 | Comercio al por menor de regalos | 60 |
| 467115 | Comercio al por menor de artículos para la limpieza | 54 |
| 461160 | Comercio al por menor de dulces y materias primas para repostería | 52 |
| 722519 | Servicios de preparación de otros alimentos para consumo inmediato | 47 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 396 | 105.8 |
| barberia_estetica | 122 | 32.6 |
| papeleria | 107 | 28.6 |
| tortilleria | 95 | 25.4 |
| tienda_ropa | 73 | 19.5 |
| carniceria | 69 | 18.4 |
| fonda | 67 | 17.9 |
| ferreteria | 61 | 16.3 |
| taller_mecanico | 51 | 13.6 |
| farmacia | 43 | 11.5 |
| fruteria | 38 | 10.1 |
| cafeteria | 33 | 8.8 |
| taqueria | 27 | 7.2 |
| panaderia | 26 | 6.9 |
| tienda_celulares | 24 | 6.4 |
| consultorio_dental | 24 | 6.4 |
| purificadora | 22 | 5.9 |
| bar | 20 | 5.3 |
| cafe_internet | 19 | 5.1 |
| zapateria | 17 | 4.5 |
| floreria | 15 | 4.0 |
| gimnasio | 13 | 3.5 |
| heladeria | 9 | 2.4 |
| pasteleria | 9 | 2.4 |
| pizzeria | 8 | 2.1 |
| tienda_mascotas | 6 | 1.6 |
| consultorio_medico | 6 | 1.6 |
| optica | 6 | 1.6 |
| cerrajeria | 5 | 1.3 |
| laboratorio_clinico | 4 | 1.1 |
| veterinaria | 4 | 1.1 |
| lavanderia | 4 | 1.1 |
| spa | 1 | 0.3 |
| coworking | 0 | 0.0 |
| renta_bicicletas | 0 | 0.0 |
| sushi | 0 | 0.0 |
| comida_china | 0 | 0.0 |
| libreria | 0 | 0.0 |
| guarderia | 0 | 0.0 |
| escuela_idiomas | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| LA CABECERA | 1 | 5,054 | 755 | medio |
| SAN JUAN | 2 | 10,644 | 517 | medio |
| IXTAPALCALCO | 2 | 8,677 | 444 | bajo |
| SANTIAGO | 1 | 3,889 | 267 | bajo |
| CALTENCO | 2 | 3,544 | 183 | bajo |
| SAN FRANCISCO | 1 | 1,984 | 147 | bajo |
| PUEBLO NUEVO | 1 | 1,437 | 78 | bajo |
| MANANTIALES | 1 | 1,289 | 34 | bajo |
| QUERETARO | 1 | 924 | 20 | bajo |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 47.7 millones de pesos por trimestre.
- Por hogar: 5,275 pesos por trimestre (lugar 51 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.

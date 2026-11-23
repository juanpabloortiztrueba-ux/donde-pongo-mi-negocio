# Ficha de municipio: Hueypoxtla (Estado de México), clave 15036

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). No está en la delimitación 2020 (Metrópolis de México 2020). Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 39,769 habitantes (lugar 49 de 76 en la ZMVM). Fuente: INEGI, Censo de Poblacion y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 9,862. AGEB urbanas: 22. Superficie urbana de esas AGEB: 21.6 km².
- Densidad: 1,843 hab/km² (lugar 70 de 76).
- Edad: 0-14 años 26.8 %; 15-24 17.1 %; 25-59 45.8 %; 60 o más 10.1 %.
- Escolaridad promedio de la población de 15 y más: 8.6 años (lugar 76 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 36.5 %; con internet: 26.7 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 96.7 %, medio 3.3 %, alto 0.0 %.
- Decil estimado típico (mediana ponderada por población): 2.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Medio 15.8 %; Alto 82.4 %; Muy alto 1.8 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 3,000 (75.4 por cada 1 000 habitantes, lugar 16 de 76). Fuente: INEGI, DENUE (corte 05/2026; historico 11/2020).
- Establecimientos en el DENUE 11/2020: 2,038. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 9,840.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 1,550 | 51.7 % |
| 81 Otros servicios excepto actividades gubernamentales | 364 | 12.1 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 314 | 10.5 % |
| 31 Industrias manufactureras | 290 | 9.7 % |
| 62 Servicios de salud y de asistencia social | 94 | 3.1 % |
| 43 Comercio al por mayor | 75 | 2.5 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 417 |
| 812110 | Salones y clínicas de belleza y peluquerías | 136 |
| 465311 | Comercio al por menor de artículos de papelería | 127 |
| 311830 | Elaboración de tortillas de maíz y molienda de nixtamal | 123 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 105 |
| 461122 | Comercio al por menor de carne de aves | 86 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 77 |
| 461160 | Comercio al por menor de dulces y materias primas para repostería | 72 |
| 465912 | Comercio al por menor de regalos | 66 |
| 464111 | Farmacias sin minisúper | 63 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 422 | 106.1 |
| barberia_estetica | 136 | 34.2 |
| papeleria | 127 | 31.9 |
| tortilleria | 123 | 30.9 |
| carniceria | 119 | 29.9 |
| tienda_ropa | 105 | 26.4 |
| taller_mecanico | 68 | 17.1 |
| farmacia | 66 | 16.6 |
| ferreteria | 52 | 13.1 |
| fruteria | 46 | 11.6 |
| cafeteria | 44 | 11.1 |
| panaderia | 43 | 10.8 |
| fonda | 38 | 9.6 |
| taqueria | 37 | 9.3 |
| cafe_internet | 24 | 6.0 |
| floreria | 19 | 4.8 |
| purificadora | 19 | 4.8 |
| gimnasio | 16 | 4.0 |
| consultorio_medico | 15 | 3.8 |
| tienda_celulares | 15 | 3.8 |
| heladeria | 14 | 3.5 |
| consultorio_dental | 14 | 3.5 |
| pasteleria | 13 | 3.3 |
| bar | 13 | 3.3 |
| zapateria | 11 | 2.8 |
| laboratorio_clinico | 10 | 2.5 |
| pizzeria | 10 | 2.5 |
| tienda_mascotas | 8 | 2.0 |
| lavanderia | 7 | 1.8 |
| optica | 4 | 1.0 |
| spa | 4 | 1.0 |
| guarderia | 4 | 1.0 |
| veterinaria | 3 | 0.8 |
| cerrajeria | 1 | 0.3 |
| escuela_idiomas | 0 | 0.0 |
| comida_china | 0 | 0.0 |
| sushi | 0 | 0.0 |
| libreria | 0 | 0.0 |
| coworking | 0 | 0.0 |
| renta_bicicletas | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| SAN FRANCISCO ZACACALCO | 5 | 9,045 | 758 | bajo |
| SANTA MARIA AJOLOAPAN | 1 | 3,648 | 446 | bajo |
| SAN ANTONIO | 1 | 5,048 | 349 | bajo |
| EL CRUCERO | 1 | 4,097 | 254 | bajo |
| SAN JOSE | 1 | 4,760 | 218 | bajo |
| GUADALUPE NOPALA | 3 | 2,982 | 203 | bajo |
| CENTRO | 1 | 1,328 | 190 | medio |
| CAPULIN | 2 | 1,757 | 149 | bajo |
| JUAREZ | 1 | 2,292 | 148 | bajo |
| EMILIANO ZAPATA SAN JOSE BATHA | 2 | 2,604 | 136 | bajo |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 38.6 millones de pesos por trimestre.
- Por hogar: 3,918 pesos por trimestre (lugar 73 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.

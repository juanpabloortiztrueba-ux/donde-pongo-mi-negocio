# Ficha de municipio: Nextlalpan (Estado de México), clave 15059

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 50,918 habitantes (lugar 45 de 76 en la ZMVM). Fuente: INEGI, Censo de Población y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 14,251. AGEB urbanas: 23. Superficie urbana de esas AGEB: 11.9 km².
- Densidad: 4,261 hab/km² (lugar 45 de 76).
- Edad: 0-14 años 29.0 %; 15-24 16.1 %; 25-59 48.4 %; 60 o más 6.5 %.
- Escolaridad promedio de la población de 15 y más: 10.1 años (lugar 44 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 37.6 %; con internet: 47.8 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 91.8 %, medio 8.2 %, alto 0.0 %.
- Decil estimado típico (mediana ponderada por población): 4.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Muy bajo 7.9 %; Bajo 16.6 %; Medio 44.2 %; Alto 24.2 %; Muy alto 7.2 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 2,201 (43.2 por cada 1 000 habitantes, lugar 66 de 76). Fuente: INEGI, DENUE (corte 05/2026; histórico 11/2020).
- Establecimientos en el DENUE 11/2020: 1,343. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 7,702.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 1,251 | 56.8 % |
| 81 Otros servicios excepto actividades gubernamentales | 265 | 12.0 % |
| 31 Industrias manufactureras | 193 | 8.8 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 185 | 8.4 % |
| 61 Servicios educativos | 55 | 2.5 % |
| 33 Industrias manufactureras | 44 | 2.0 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 325 |
| 465311 | Comercio al por menor de artículos de papelería | 115 |
| 812110 | Salones y clínicas de belleza y peluquerías | 93 |
| 311830 | Elaboración de tortillas de maíz y molienda de nixtamal | 66 |
| 461122 | Comercio al por menor de carne de aves | 63 |
| 467115 | Comercio al por menor de artículos para la limpieza | 60 |
| 465912 | Comercio al por menor de regalos | 55 |
| 464111 | Farmacias sin minisúper | 55 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 55 |
| 467111 | Comercio al por menor en ferreterías y tlapalerías | 51 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 339 | 66.6 |
| papeleria | 115 | 22.6 |
| barberia_estetica | 93 | 18.3 |
| carniceria | 92 | 18.1 |
| tortilleria | 69 | 13.6 |
| farmacia | 57 | 11.2 |
| tienda_ropa | 55 | 10.8 |
| ferreteria | 51 | 10.0 |
| fruteria | 38 | 7.5 |
| purificadora | 37 | 7.3 |
| taller_mecanico | 31 | 6.1 |
| panaderia | 28 | 5.5 |
| taqueria | 27 | 5.3 |
| lavanderia | 24 | 4.7 |
| cafeteria | 23 | 4.5 |
| fonda | 23 | 4.5 |
| tienda_celulares | 22 | 4.3 |
| floreria | 16 | 3.1 |
| heladeria | 14 | 2.7 |
| cafe_internet | 14 | 2.7 |
| gimnasio | 13 | 2.6 |
| consultorio_dental | 12 | 2.4 |
| pizzeria | 9 | 1.8 |
| consultorio_medico | 7 | 1.4 |
| zapateria | 6 | 1.2 |
| tienda_mascotas | 6 | 1.2 |
| veterinaria | 5 | 1.0 |
| pasteleria | 5 | 1.0 |
| laboratorio_clinico | 3 | 0.6 |
| bar | 3 | 0.6 |
| optica | 2 | 0.4 |
| spa | 1 | 0.2 |
| cerrajeria | 1 | 0.2 |
| escuela_idiomas | 0 | 0.0 |
| comida_china | 0 | 0.0 |
| sushi | 0 | 0.0 |
| guarderia | 0 | 0.0 |
| coworking | 0 | 0.0 |
| libreria | 0 | 0.0 |
| renta_bicicletas | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| BARRIO CENTRAL | 3 | 5,867 | 596 | bajo |
| SAN FRANCISCO MOLONCO | 3 | 7,998 | 513 | bajo |
| SAN MIGUEL JALTOCAN | 2 | 4,098 | 221 | bajo |
| SANTA ANA NEXTLALPAN | 1 | 2,304 | 191 | bajo |
| HACIENDA TEQUIXQUIAPAN | 1 | 5,990 | 149 | bajo |
| PRADOS DE SAN FRANCISCO | 3 | 3,702 | 114 | bajo |
| HACIENDA COCOYOC | 1 | 5,734 | 103 | bajo |
| ATENANCO | 1 | 2,857 | 97 | bajo |
| HACIENDA LA CADENA | 1 | 2,333 | 50 | bajo |
| PASEOS DEL VALLE | 1 | 1,630 | 33 | bajo |

## Colonias de mayor y menor nivel socioeconómico estimado

Solo colonias con 3 000 habitantes o más en sus AGEB. «Decil esperado» es el promedio ponderado por población del decil estimado (1 = más bajo, 10 = más alto de la ZMVM). Es estimación.

Mayor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| HACIENDA COCOYOC | 5,734 | 4.3 |
| BARRIO CENTRAL | 5,867 | 4.2 |
| SAN FRANCISCO MOLONCO | 7,998 | 3.9 |
| SAN MIGUEL JALTOCAN | 4,098 | 3.5 |
| HACIENDA TEQUIXQUIAPAN | 5,990 | 3.3 |

Menor nivel estimado:

| Colonia | Habitantes | Decil esperado |
|---|---|---|
| PRADOS DE SAN FRANCISCO | 3,702 | 2.6 |
| HACIENDA TEQUIXQUIAPAN | 5,990 | 3.3 |
| SAN MIGUEL JALTOCAN | 4,098 | 3.5 |
| SAN FRANCISCO MOLONCO | 7,998 | 3.9 |
| BARRIO CENTRAL | 5,867 | 4.2 |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 72.5 millones de pesos por trimestre.
- Por hogar: 5,089 pesos por trimestre (lugar 55 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.

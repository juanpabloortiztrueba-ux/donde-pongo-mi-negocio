# Ficha de municipio: Cocotitlán (Estado de México), clave 15022

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 10,290 habitantes (lugar 67 de 76 en la ZMVM). Fuente: INEGI, Censo de Población y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 2,657. AGEB urbanas: 8. Superficie urbana de esas AGEB: 2.2 km².
- Densidad: 4,765 hab/km² (lugar 41 de 76).
- Edad: 0-14 años 23.2 %; 15-24 16.0 %; 25-59 47.0 %; 60 o más 13.0 %.
- Escolaridad promedio de la población de 15 y más: 10.7 años (lugar 25 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 37.6 %; con internet: 54.0 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 38.1 %, medio 61.9 %, alto 0.0 %.
- Decil estimado típico (mediana ponderada por población): 5.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Bajo 61.8 %; Medio 38.2 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 660 (64.1 por cada 1 000 habitantes, lugar 29 de 76). Fuente: INEGI, DENUE (corte 05/2026; histórico 11/2020).
- Establecimientos en el DENUE 11/2020: 549. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 2,205.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 390 | 59.1 % |
| 81 Otros servicios excepto actividades gubernamentales | 81 | 12.3 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 44 | 6.7 % |
| 31 Industrias manufactureras | 36 | 5.5 % |
| 62 Servicios de salud y de asistencia social | 23 | 3.5 % |
| 43 Comercio al por mayor | 22 | 3.3 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 120 |
| 465311 | Comercio al por menor de artículos de papelería | 30 |
| 812110 | Salones y clínicas de belleza y peluquerías | 30 |
| 311830 | Elaboración de tortillas de maíz y molienda de nixtamal | 22 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 21 |
| 461121 | Comercio al por menor de carnes rojas | 19 |
| 461122 | Comercio al por menor de carne de aves | 18 |
| 465912 | Comercio al por menor de regalos | 17 |
| 461160 | Comercio al por menor de dulces y materias primas para repostería | 16 |
| 467111 | Comercio al por menor en ferreterías y tlapalerías | 14 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 122 | 118.6 |
| carniceria | 37 | 36.0 |
| papeleria | 30 | 29.2 |
| barberia_estetica | 30 | 29.2 |
| tortilleria | 22 | 21.4 |
| tienda_ropa | 21 | 20.4 |
| farmacia | 15 | 14.6 |
| ferreteria | 14 | 13.6 |
| fruteria | 14 | 13.6 |
| cafe_internet | 7 | 6.8 |
| panaderia | 7 | 6.8 |
| heladeria | 7 | 6.8 |
| consultorio_dental | 7 | 6.8 |
| consultorio_medico | 6 | 5.8 |
| fonda | 6 | 5.8 |
| taqueria | 6 | 5.8 |
| tienda_celulares | 4 | 3.9 |
| bar | 4 | 3.9 |
| cafeteria | 4 | 3.9 |
| taller_mecanico | 4 | 3.9 |
| pizzeria | 3 | 2.9 |
| gimnasio | 3 | 2.9 |
| pasteleria | 3 | 2.9 |
| veterinaria | 2 | 1.9 |
| purificadora | 2 | 1.9 |
| floreria | 2 | 1.9 |
| laboratorio_clinico | 1 | 1.0 |
| lavanderia | 1 | 1.0 |
| guarderia | 1 | 1.0 |
| cerrajeria | 1 | 1.0 |
| optica | 1 | 1.0 |
| tienda_mascotas | 1 | 1.0 |
| spa | 0 | 0.0 |
| escuela_idiomas | 0 | 0.0 |
| zapateria | 0 | 0.0 |
| comida_china | 0 | 0.0 |
| sushi | 0 | 0.0 |
| coworking | 0 | 0.0 |
| renta_bicicletas | 0 | 0.0 |
| libreria | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| TECHICHILCO | 4 | 6,627 | 539 | medio |
| TLAPIPINCA | 2 | 3,631 | 116 | bajo |
| Cocotitlán | 2 | 32 | 0 | medio |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 16.1 millones de pesos por trimestre.
- Por hogar: 6,076 pesos por trimestre (lugar 34 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.

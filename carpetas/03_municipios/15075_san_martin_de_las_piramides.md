# Ficha de municipio: San Martín de las Pirámides (Estado de México), clave 15075

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 14,283 habitantes (lugar 66 de 76 en la ZMVM). Fuente: INEGI, Censo de Poblacion y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 3,865. AGEB urbanas: 6. Superficie urbana de esas AGEB: 3.5 km².
- Densidad: 4,125 hab/km² (lugar 47 de 76).
- Edad: 0-14 años 21.8 %; 15-24 17.3 %; 25-59 48.2 %; 60 o más 12.7 %.
- Escolaridad promedio de la población de 15 y más: 10.5 años (lugar 28 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 46.2 %; con internet: 53.0 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 31.4 %, medio 68.6 %, alto 0.0 %.
- Decil estimado típico (mediana ponderada por población): 5.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Bajo 38.0 %; Medio 62.0 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 1,563 (109.4 por cada 1 000 habitantes, lugar 5 de 76). Fuente: INEGI, DENUE (corte 05/2026; historico 11/2020).
- Establecimientos en el DENUE 11/2020: 1,201. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 5,780.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 647 | 41.4 % |
| 81 Otros servicios excepto actividades gubernamentales | 229 | 14.7 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 218 | 13.9 % |
| 32 Industrias manufactureras | 126 | 8.1 % |
| 31 Industrias manufactureras | 81 | 5.2 % |
| 62 Servicios de salud y de asistencia social | 61 | 3.9 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 143 |
| 327991 | Fabricación de productos a base de piedras de cantera | 67 |
| 812110 | Salones y clínicas de belleza y peluquerías | 65 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 46 |
| 465915 | Comercio al por menor en tiendas de artesanías | 37 |
| 465311 | Comercio al por menor de artículos de papelería | 34 |
| 465912 | Comercio al por menor de regalos | 33 |
| 722519 | Servicios de preparación de otros alimentos para consumo inmediato | 33 |
| 461130 | Comercio al por menor de frutas y verduras frescas | 32 |
| 722515 | Cafeterías, fuentes de sodas, neverías, refresquerías y similares | 30 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 149 | 104.3 |
| barberia_estetica | 65 | 45.5 |
| fonda | 61 | 42.7 |
| tienda_ropa | 46 | 32.2 |
| carniceria | 44 | 30.8 |
| papeleria | 34 | 23.8 |
| fruteria | 32 | 22.4 |
| cafeteria | 30 | 21.0 |
| taller_mecanico | 29 | 20.3 |
| tortilleria | 22 | 15.4 |
| farmacia | 21 | 14.7 |
| ferreteria | 18 | 12.6 |
| taqueria | 16 | 11.2 |
| panaderia | 15 | 10.5 |
| lavanderia | 13 | 9.1 |
| bar | 11 | 7.7 |
| heladeria | 10 | 7.0 |
| tienda_celulares | 10 | 7.0 |
| consultorio_dental | 10 | 7.0 |
| gimnasio | 9 | 6.3 |
| pizzeria | 9 | 6.3 |
| purificadora | 8 | 5.6 |
| cafe_internet | 8 | 5.6 |
| floreria | 8 | 5.6 |
| consultorio_medico | 7 | 4.9 |
| veterinaria | 7 | 4.9 |
| zapateria | 6 | 4.2 |
| pasteleria | 4 | 2.8 |
| guarderia | 4 | 2.8 |
| optica | 3 | 2.1 |
| laboratorio_clinico | 3 | 2.1 |
| tienda_mascotas | 3 | 2.1 |
| comida_china | 1 | 0.7 |
| spa | 1 | 0.7 |
| cerrajeria | 1 | 0.7 |
| sushi | 0 | 0.0 |
| escuela_idiomas | 0 | 0.0 |
| coworking | 0 | 0.0 |
| libreria | 0 | 0.0 |
| renta_bicicletas | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| SAN MARTIN DE LAS PIRAMIDES | 6 | 14,283 | 1,554 | medio |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 23.4 millones de pesos por trimestre.
- Por hogar: 6,044 pesos por trimestre (lugar 35 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.

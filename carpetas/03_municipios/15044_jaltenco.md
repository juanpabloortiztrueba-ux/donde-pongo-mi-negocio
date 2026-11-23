# Ficha de municipio: Jaltenco (Estado de México), clave 15044

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 28,217 habitantes (lugar 55 de 76 en la ZMVM). Fuente: INEGI, Censo de Poblacion y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 7,638. AGEB urbanas: 8. Superficie urbana de esas AGEB: 4.7 km².
- Densidad: 6,056 hab/km² (lugar 35 de 76).
- Edad: 0-14 años 23.5 %; 15-24 16.7 %; 25-59 46.6 %; 60 o más 13.2 %.
- Escolaridad promedio de la población de 15 y más: 10.2 años (lugar 35 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 36.5 %; con internet: 59.8 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 57.8 %, medio 42.2 %, alto 0.0 %.
- Decil estimado típico (mediana ponderada por población): 4.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Bajo 54.7 %; Medio 28.5 %; Alto 16.8 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 1,327 (47.0 por cada 1 000 habitantes, lugar 57 de 76). Fuente: INEGI, DENUE (corte 05/2026; historico 11/2020).
- Establecimientos en el DENUE 11/2020: 1,094. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 4,803.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 650 | 49.0 % |
| 81 Otros servicios excepto actividades gubernamentales | 191 | 14.4 % |
| 31 Industrias manufactureras | 157 | 11.8 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 128 | 9.6 % |
| 62 Servicios de salud y de asistencia social | 55 | 4.1 % |
| 61 Servicios educativos | 28 | 2.1 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 215 |
| 812110 | Salones y clínicas de belleza y peluquerías | 70 |
| 315229 | Confección en serie de otra ropa exterior de materiales textiles | 56 |
| 465311 | Comercio al por menor de artículos de papelería | 53 |
| 461122 | Comercio al por menor de carne de aves | 35 |
| 311830 | Elaboración de tortillas de maíz y molienda de nixtamal | 33 |
| 467115 | Comercio al por menor de artículos para la limpieza | 33 |
| 464111 | Farmacias sin minisúper | 31 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 30 |
| 461130 | Comercio al por menor de frutas y verduras frescas | 28 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 221 | 78.3 |
| barberia_estetica | 70 | 24.8 |
| papeleria | 53 | 18.8 |
| carniceria | 46 | 16.3 |
| tortilleria | 34 | 12.0 |
| farmacia | 33 | 11.7 |
| tienda_ropa | 30 | 10.6 |
| fruteria | 28 | 9.9 |
| fonda | 23 | 8.2 |
| cafeteria | 22 | 7.8 |
| taller_mecanico | 22 | 7.8 |
| taqueria | 21 | 7.4 |
| lavanderia | 21 | 7.4 |
| cafe_internet | 17 | 6.0 |
| consultorio_dental | 16 | 5.7 |
| ferreteria | 16 | 5.7 |
| panaderia | 16 | 5.7 |
| purificadora | 11 | 3.9 |
| tienda_celulares | 11 | 3.9 |
| heladeria | 10 | 3.5 |
| gimnasio | 7 | 2.5 |
| tienda_mascotas | 7 | 2.5 |
| consultorio_medico | 6 | 2.1 |
| pasteleria | 6 | 2.1 |
| pizzeria | 5 | 1.8 |
| floreria | 4 | 1.4 |
| veterinaria | 3 | 1.1 |
| optica | 2 | 0.7 |
| cerrajeria | 1 | 0.4 |
| bar | 1 | 0.4 |
| laboratorio_clinico | 1 | 0.4 |
| guarderia | 1 | 0.4 |
| spa | 0 | 0.0 |
| escuela_idiomas | 0 | 0.0 |
| libreria | 0 | 0.0 |
| renta_bicicletas | 0 | 0.0 |
| comida_china | 0 | 0.0 |
| sushi | 0 | 0.0 |
| coworking | 0 | 0.0 |
| zapateria | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| SAN ANDRES JALTENCO | 3 | 12,785 | 818 | bajo |
| NINGUNO | 2 | 7,011 | 218 | bajo |
| ALBORADA JALTENCO | 2 | 7,567 | 188 | medio |
| PROVIVIENDA | 1 | 854 | 103 | medio |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 44.9 millones de pesos por trimestre.
- Por hogar: 5,874 pesos por trimestre (lugar 41 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.

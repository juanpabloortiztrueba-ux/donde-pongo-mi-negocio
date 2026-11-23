# Ficha de municipio: Chiautla (Estado de México), clave 15028

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). Es municipio central de la zona metropolitana. Está en la delimitación 2020. Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 19,275 habitantes (lugar 60 de 76 en la ZMVM). Fuente: INEGI, Censo de Poblacion y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 5,057. AGEB urbanas: 10. Superficie urbana de esas AGEB: 8.6 km².
- Densidad: 2,242 hab/km² (lugar 63 de 76).
- Edad: 0-14 años 23.6 %; 15-24 17.4 %; 25-59 47.2 %; 60 o más 11.5 %.
- Escolaridad promedio de la población de 15 y más: 10.3 años (lugar 33 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 47.3 %; con internet: 47.9 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 43.9 %, medio 56.1 %, alto 0.0 %, sin estimación 0.0 %.
- Decil estimado típico (mediana ponderada por población): 6.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Bajo 16.5 %; Medio 62.0 %; Alto 21.6 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 1,464 (76.0 por cada 1 000 habitantes, lugar 15 de 76). Fuente: INEGI, DENUE (corte 05/2026; historico 11/2020).
- Establecimientos en el DENUE 11/2020: 1,149. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 5,840.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 647 | 44.2 % |
| 81 Otros servicios excepto actividades gubernamentales | 212 | 14.5 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 177 | 12.1 % |
| 31 Industrias manufactureras | 97 | 6.6 % |
| 32 Industrias manufactureras | 80 | 5.5 % |
| 62 Servicios de salud y de asistencia social | 61 | 4.2 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 169 |
| 812110 | Salones y clínicas de belleza y peluquerías | 76 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 49 |
| 465311 | Comercio al por menor de artículos de papelería | 47 |
| 327121 | Fabricación de ladrillos no refractarios | 35 |
| 464111 | Farmacias sin minisúper | 30 |
| 465912 | Comercio al por menor de regalos | 30 |
| 461122 | Comercio al por menor de carne de aves | 29 |
| 311830 | Elaboración de tortillas de maíz y molienda de nixtamal | 27 |
| 722514 | Restaurantes con servicio de preparación de tacos y tortas | 25 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 175 | 90.8 |
| barberia_estetica | 76 | 39.4 |
| carniceria | 50 | 25.9 |
| papeleria | 47 | 24.4 |
| farmacia | 32 | 16.6 |
| fonda | 27 | 14.0 |
| tortilleria | 27 | 14.0 |
| taqueria | 25 | 13.0 |
| ferreteria | 23 | 11.9 |
| taller_mecanico | 21 | 10.9 |
| cafeteria | 20 | 10.4 |
| lavanderia | 20 | 10.4 |
| panaderia | 19 | 9.9 |
| consultorio_dental | 18 | 9.3 |
| fruteria | 16 | 8.3 |
| cafe_internet | 15 | 7.8 |
| bar | 13 | 6.7 |
| purificadora | 13 | 6.7 |
| floreria | 12 | 6.2 |
| consultorio_medico | 11 | 5.7 |
| tienda_ropa | 11 | 5.7 |
| heladeria | 9 | 4.7 |
| pizzeria | 9 | 4.7 |
| tienda_celulares | 7 | 3.6 |
| tienda_mascotas | 7 | 3.6 |
| zapateria | 6 | 3.1 |
| gimnasio | 5 | 2.6 |
| laboratorio_clinico | 4 | 2.1 |
| cerrajeria | 4 | 2.1 |
| pasteleria | 4 | 2.1 |
| optica | 3 | 1.6 |
| spa | 2 | 1.0 |
| veterinaria | 1 | 0.5 |
| renta_bicicletas | 0 | 0.0 |
| libreria | 0 | 0.0 |
| guarderia | 0 | 0.0 |
| comida_china | 0 | 0.0 |
| sushi | 0 | 0.0 |
| coworking | 0 | 0.0 |
| escuela_idiomas | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| HUITZNAHUAC | 1 | 3,963 | 470 | medio |
| CHIAUTLA | 2 | 3,773 | 375 | medio |
| SANTIAGO CHIMALPA | 1 | 4,157 | 263 | bajo |
| OCOPULCO | 1 | 4,308 | 225 | bajo |
| NONOALCO | 1 | 1,906 | 64 | medio |
| AMAJAC | 2 | 765 | 55 | medio |
| SAN FRANCISCO | 1 | 399 | 8 | medio |
| Chiautla | 1 | 4 | 0 | NO ENCONTRADO |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 31.4 millones de pesos por trimestre.
- Por hogar: 6,203 pesos por trimestre (lugar 33 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.

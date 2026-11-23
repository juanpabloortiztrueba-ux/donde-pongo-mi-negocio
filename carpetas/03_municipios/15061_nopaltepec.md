# Ficha de municipio: Nopaltepec (Estado de México), clave 15061

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). No está en la delimitación 2020 (Metrópolis de México 2020). Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 8,699 habitantes (lugar 70 de 76 en la ZMVM). Fuente: INEGI, Censo de Poblacion y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 2,453. AGEB urbanas: 17. Superficie urbana de esas AGEB: 5.6 km².
- Densidad: 1,546 hab/km² (lugar 73 de 76).
- Edad: 0-14 años 25.9 %; 15-24 17.6 %; 25-59 43.6 %; 60 o más 12.2 %.
- Escolaridad promedio de la población de 15 y más: 9.1 años (lugar 72 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 48.8 %; con internet: 36.1 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 89.3 %, medio 10.3 %, alto 0.0 %, sin estimación 0.4 %.
- Decil estimado típico (mediana ponderada por población): 3.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Bajo 5.1 %; Medio 15.5 %; Alto 77.8 %; Muy alto 1.6 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 928 (106.7 por cada 1 000 habitantes, lugar 6 de 76). Fuente: INEGI, DENUE (corte 05/2026; historico 11/2020).
- Establecimientos en el DENUE 11/2020: 576. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 3,501.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 409 | 44.1 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 134 | 14.4 % |
| 81 Otros servicios excepto actividades gubernamentales | 105 | 11.3 % |
| 31 Industrias manufactureras | 86 | 9.3 % |
| 32 Industrias manufactureras | 49 | 5.3 % |
| 62 Servicios de salud y de asistencia social | 32 | 3.4 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 121 |
| 812110 | Salones y clínicas de belleza y peluquerías | 39 |
| 315229 | Confección en serie de otra ropa exterior de materiales textiles | 38 |
| 465311 | Comercio al por menor de artículos de papelería | 36 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 31 |
| 465912 | Comercio al por menor de regalos | 29 |
| 461160 | Comercio al por menor de dulces y materias primas para repostería | 21 |
| 722514 | Restaurantes con servicio de preparación de tacos y tortas | 20 |
| 326120 | Fabricación de tubería y conexiones, y tubos para embalaje | 20 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 19 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 121 | 139.1 |
| barberia_estetica | 39 | 44.8 |
| papeleria | 36 | 41.4 |
| carniceria | 24 | 27.6 |
| fonda | 23 | 26.4 |
| taqueria | 20 | 23.0 |
| tienda_ropa | 19 | 21.8 |
| ferreteria | 18 | 20.7 |
| tortilleria | 18 | 20.7 |
| fruteria | 17 | 19.5 |
| taller_mecanico | 16 | 18.4 |
| cafeteria | 15 | 17.2 |
| farmacia | 13 | 14.9 |
| panaderia | 13 | 14.9 |
| bar | 10 | 11.5 |
| consultorio_dental | 8 | 9.2 |
| consultorio_medico | 8 | 9.2 |
| zapateria | 8 | 9.2 |
| purificadora | 5 | 5.7 |
| heladeria | 5 | 5.7 |
| gimnasio | 4 | 4.6 |
| lavanderia | 4 | 4.6 |
| pasteleria | 4 | 4.6 |
| cafe_internet | 3 | 3.4 |
| laboratorio_clinico | 3 | 3.4 |
| floreria | 2 | 2.3 |
| veterinaria | 1 | 1.1 |
| pizzeria | 1 | 1.1 |
| optica | 1 | 1.1 |
| spa | 1 | 1.1 |
| escuela_idiomas | 1 | 1.1 |
| tienda_mascotas | 1 | 1.1 |
| cerrajeria | 1 | 1.1 |
| tienda_celulares | 1 | 1.1 |
| guarderia | 0 | 0.0 |
| comida_china | 0 | 0.0 |
| sushi | 0 | 0.0 |
| libreria | 0 | 0.0 |
| coworking | 0 | 0.0 |
| renta_bicicletas | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| NOPALTEPEC | 8 | 3,941 | 468 | bajo |
| SAN FELIPE TEOTITLAN | 6 | 4,587 | 456 | bajo |
| TLAXOXILCO | 1 | 139 | 4 | bajo |
| Nopaltepec | 1 | 0 | 0 | NO ENCONTRADO |
| San Felipe Teotitlán | 1 | 32 | 0 | bajo |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 11.1 millones de pesos por trimestre.
- Por hogar: 4,539 pesos por trimestre (lugar 67 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.

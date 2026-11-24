# Ficha de municipio: Ozumba (Estado de México), clave 15068

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). No está en la delimitación 2020 (Metrópolis de México 2020). Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 24,951 habitantes (lugar 58 de 76 en la ZMVM). Fuente: INEGI, Censo de Población y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 5,870. AGEB urbanas: 10. Superficie urbana de esas AGEB: 7.6 km².
- Densidad: 3,288 hab/km² (lugar 56 de 76).
- Edad: 0-14 años 26.0 %; 15-24 17.6 %; 25-59 45.0 %; 60 o más 11.4 %.
- Escolaridad promedio de la población de 15 y más: 10.0 años (lugar 49 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 34.4 %; con internet: 37.6 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 91.2 %, medio 8.8 %, alto 0.0 %.
- Decil estimado típico (mediana ponderada por población): 4.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Medio 8.8 %; Alto 91.2 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 2,064 (82.7 por cada 1 000 habitantes, lugar 13 de 76). Fuente: INEGI, DENUE (corte 05/2026; histórico 11/2020).
- Establecimientos en el DENUE 11/2020: 1,734. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 7,363.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 1,019 | 49.4 % |
| 81 Otros servicios excepto actividades gubernamentales | 329 | 15.9 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 224 | 10.9 % |
| 31 Industrias manufactureras | 114 | 5.5 % |
| 62 Servicios de salud y de asistencia social | 66 | 3.2 % |
| 43 Comercio al por mayor | 59 | 2.9 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 256 |
| 465311 | Comercio al por menor de artículos de papelería | 87 |
| 812110 | Salones y clínicas de belleza y peluquerías | 82 |
| 461130 | Comercio al por menor de frutas y verduras frescas | 73 |
| 461121 | Comercio al por menor de carnes rojas | 70 |
| 465912 | Comercio al por menor de regalos | 55 |
| 722514 | Restaurantes con servicio de preparación de tacos y tortas | 52 |
| 311830 | Elaboración de tortillas de maíz y molienda de nixtamal | 51 |
| 461122 | Comercio al por menor de carne de aves | 47 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 45 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 265 | 106.2 |
| carniceria | 117 | 46.9 |
| papeleria | 87 | 34.9 |
| barberia_estetica | 82 | 32.9 |
| fruteria | 73 | 29.3 |
| taqueria | 52 | 20.8 |
| tortilleria | 51 | 20.4 |
| farmacia | 47 | 18.8 |
| tienda_ropa | 37 | 14.8 |
| fonda | 36 | 14.4 |
| taller_mecanico | 35 | 14.0 |
| cafeteria | 34 | 13.6 |
| panaderia | 26 | 10.4 |
| consultorio_dental | 25 | 10.0 |
| ferreteria | 22 | 8.8 |
| consultorio_medico | 18 | 7.2 |
| tienda_celulares | 17 | 6.8 |
| zapateria | 16 | 6.4 |
| floreria | 16 | 6.4 |
| cafe_internet | 15 | 6.0 |
| bar | 12 | 4.8 |
| optica | 8 | 3.2 |
| veterinaria | 8 | 3.2 |
| pasteleria | 7 | 2.8 |
| purificadora | 7 | 2.8 |
| gimnasio | 7 | 2.8 |
| lavanderia | 7 | 2.8 |
| heladeria | 6 | 2.4 |
| tienda_mascotas | 6 | 2.4 |
| pizzeria | 6 | 2.4 |
| laboratorio_clinico | 4 | 1.6 |
| libreria | 2 | 0.8 |
| cerrajeria | 2 | 0.8 |
| spa | 1 | 0.4 |
| comida_china | 1 | 0.4 |
| sushi | 0 | 0.0 |
| coworking | 0 | 0.0 |
| escuela_idiomas | 0 | 0.0 |
| guarderia | 0 | 0.0 |
| renta_bicicletas | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| ALZATE | 2 | 4,896 | 841 | bajo |
| OZUMBA | 2 | 9,124 | 595 | bajo |
| SAN JUAN | 1 | 2,184 | 241 | medio |
| SAN MATEO TECALCO | 1 | 3,440 | 233 | bajo |
| SAN VICENTE CHIMALHUACAN | 2 | 2,931 | 76 | bajo |
| TEPETLIXPA | 1 | 1,568 | 60 | bajo |
| HUAMANTLA | 1 | 808 | 18 | bajo |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 29.4 millones de pesos por trimestre.
- Por hogar: 5,009 pesos por trimestre (lugar 58 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.

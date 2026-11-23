# Ficha de municipio: Ayapango (Estado de México), clave 15017

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). No está en la delimitación 2020 (Metrópolis de México 2020). Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 3,975 habitantes (lugar 75 de 76 en la ZMVM). Fuente: INEGI, Censo de Poblacion y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 1,057. AGEB urbanas: 8. Superficie urbana de esas AGEB: 1.7 km².
- Densidad: 2,326 hab/km² (lugar 62 de 76).
- Edad: 0-14 años 26.0 %; 15-24 16.5 %; 25-59 45.9 %; 60 o más 10.5 %.
- Escolaridad promedio de la población de 15 y más: 10.0 años (lugar 48 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 39.5 %; con internet: 40.6 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 81.7 %, medio 18.3 %, alto 0.0 %.
- Decil estimado típico (mediana ponderada por población): 3.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Medio 95.9 %; Alto 1.7 %; Muy alto 2.5 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 286 (71.9 por cada 1 000 habitantes, lugar 22 de 76). Fuente: INEGI, DENUE (corte 05/2026; historico 11/2020).
- Establecimientos en el DENUE 11/2020: 197. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 1,162.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 141 | 49.3 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 42 | 14.7 % |
| 81 Otros servicios excepto actividades gubernamentales | 30 | 10.5 % |
| 31 Industrias manufactureras | 14 | 4.9 % |
| 61 Servicios educativos | 10 | 3.5 % |
| 62 Servicios de salud y de asistencia social | 10 | 3.5 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 45 |
| 465311 | Comercio al por menor de artículos de papelería | 13 |
| 722515 | Cafeterías, fuentes de sodas, neverías, refresquerías y similares | 12 |
| 461122 | Comercio al por menor de carne de aves | 10 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 9 |
| 813210 | Asociaciones y organizaciones religiosas | 7 |
| 461150 | Comercio al por menor de leche, otros productos lácteos y embutidos | 7 |
| 467111 | Comercio al por menor en ferreterías y tlapalerías | 7 |
| 722514 | Restaurantes con servicio de preparación de tacos y tortas | 7 |
| 811111 | Reparación mecánica en general de automóviles y camiones | 6 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 45 | 113.2 |
| carniceria | 14 | 35.2 |
| papeleria | 13 | 32.7 |
| cafeteria | 12 | 30.2 |
| ferreteria | 7 | 17.6 |
| taqueria | 7 | 17.6 |
| taller_mecanico | 7 | 17.6 |
| fonda | 6 | 15.1 |
| farmacia | 6 | 15.1 |
| tortilleria | 5 | 12.6 |
| fruteria | 5 | 12.6 |
| barberia_estetica | 4 | 10.1 |
| tienda_ropa | 3 | 7.5 |
| tienda_mascotas | 2 | 5.0 |
| panaderia | 2 | 5.0 |
| purificadora | 2 | 5.0 |
| cafe_internet | 2 | 5.0 |
| consultorio_medico | 2 | 5.0 |
| heladeria | 2 | 5.0 |
| consultorio_dental | 2 | 5.0 |
| veterinaria | 2 | 5.0 |
| pasteleria | 1 | 2.5 |
| bar | 1 | 2.5 |
| lavanderia | 1 | 2.5 |
| pizzeria | 1 | 2.5 |
| optica | 1 | 2.5 |
| libreria | 1 | 2.5 |
| tienda_celulares | 1 | 2.5 |
| guarderia | 0 | 0.0 |
| escuela_idiomas | 0 | 0.0 |
| spa | 0 | 0.0 |
| floreria | 0 | 0.0 |
| renta_bicicletas | 0 | 0.0 |
| cerrajeria | 0 | 0.0 |
| comida_china | 0 | 0.0 |
| sushi | 0 | 0.0 |
| zapateria | 0 | 0.0 |
| coworking | 0 | 0.0 |
| gimnasio | 0 | 0.0 |
| laboratorio_clinico | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| LA SOLEDAD | 2 | 1,956 | 130 | bajo |
| AYAPANGO | 3 | 736 | 107 | medio |
| LA CAPILLA | 1 | 1,190 | 47 | bajo |
| Ayapango de Gabriel Ramos M. | 2 | 93 | 0 | bajo |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 5.2 millones de pesos por trimestre.
- Por hogar: 4,932 pesos por trimestre (lugar 60 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.

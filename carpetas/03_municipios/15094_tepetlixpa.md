# Ficha de municipio: Tepetlixpa (Estado de México), clave 15094

Zona Metropolitana del Valle de México (76 municipios, delimitación 2015 de SEDATU-CONAPO-INEGI). No está en la delimitación 2020 (Metrópolis de México 2020). Cifras generadas con código el 2026-11-23 desde `data/processed/agebs_features.parquet` y el DENUE; cubren solo AGEB urbanas.

## Población y hogares

- Población en AGEB urbanas: 17,258 habitantes (lugar 63 de 76 en la ZMVM). Fuente: INEGI, Censo de Poblacion y Vivienda 2020 (resultados por AGEB urbana).
- Hogares: 4,336. AGEB urbanas: 8. Superficie urbana de esas AGEB: 8.2 km².
- Densidad: 2,104 hab/km² (lugar 67 de 76).
- Edad: 0-14 años 25.6 %; 15-24 16.7 %; 25-59 46.2 %; 60 o más 11.5 %.
- Escolaridad promedio de la población de 15 y más: 9.4 años (lugar 65 de 76); promedio de las AGEB ponderado por población.
- Viviendas con automóvil: 32.0 %; con internet: 32.4 % (ponderado por viviendas habitadas).
- Población en AGEB a 1 km o menos de una estación de transporte masivo (Metro, Metrobús, Tren Ligero, Cablebús, Tren Suburbano, Mexibús y Mexicable; estos dos últimos salen de OpenStreetMap): 0.0 %.

## Nivel socioeconómico estimado

Estimación propia (no dato del INEGI): modelo de ingreso entrenado en la ENIGH 2024 y aplicado a las variables del Censo por AGEB. Bajo = deciles 1 a 4, medio = 5 a 8, alto = 9 y 10 de la ZMVM. Detalle en `01_metodologia/nse_estimado.md`.

- Población por NSE estimado: bajo 100.0 %, medio 0.0 %, alto 0.0 %.
- Decil estimado típico (mediana ponderada por población): 2.
- Grado de marginación urbana (CONAPO 2020), % de la población con índice: Medio 8.0 %; Alto 92.0 %. Fuente: CONAPO, IMU 2020. Ojo: «Muy bajo» es la menor marginación.

## Actividad económica (DENUE)

- Establecimientos en el DENUE 05/2026: 1,087 (63.0 por cada 1 000 habitantes, lugar 31 de 76). Fuente: INEGI, DENUE (corte 05/2026; historico 11/2020).
- Establecimientos en el DENUE 11/2020: 962. Cuidado: la diferencia entre cortes no son aperturas netas; hay cargas masivas de los Censos Económicos y rotación de identificadores.
- Personal ocupado estimado en AGEB (punto medio de estratos; subestima grandes empleadores): 4,192.

### Sectores con más establecimientos

| Sector SCIAN | Establecimientos | % del municipio |
|---|---|---|
| 46 Comercio al por menor | 530 | 48.8 % |
| 72 Servicios de alojamiento temporal y de preparación de alimentos y bebidas | 156 | 14.4 % |
| 81 Otros servicios excepto actividades gubernamentales | 150 | 13.8 % |
| 31 Industrias manufactureras | 53 | 4.9 % |
| 62 Servicios de salud y de asistencia social | 38 | 3.5 % |
| 43 Comercio al por mayor | 35 | 3.2 % |

### Giros dominantes (clases SCIAN con más establecimientos)

| Clase SCIAN | Actividad | Establecimientos |
|---|---|---|
| 461110 | Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas | 182 |
| 812110 | Salones y clínicas de belleza y peluquerías | 50 |
| 465311 | Comercio al por menor de artículos de papelería | 38 |
| 465912 | Comercio al por menor de regalos | 29 |
| 722513 | Restaurantes con servicio de preparación de antojitos | 28 |
| 461122 | Comercio al por menor de carne de aves | 28 |
| 722515 | Cafeterías, fuentes de sodas, neverías, refresquerías y similares | 27 |
| 722514 | Restaurantes con servicio de preparación de tacos y tortas | 26 |
| 311830 | Elaboración de tortillas de maíz y molienda de nixtamal | 25 |
| 463211 | Comercio al por menor de ropa, excepto de bebé y lencería | 23 |

## Negocios de giros del catálogo en este municipio

Cuenta del DENUE 05/2026 según la definición de cada giro en `config/giros.yaml` (clases SCIAN y, donde la clase se comparte, filtro por nombre). La tercera columna es la tasa por cada 10 000 habitantes.

| Giro | Establecimientos | Por 10 000 hab. |
|---|---|---|
| abarrotes | 187 | 108.4 |
| barberia_estetica | 50 | 29.0 |
| carniceria | 48 | 27.8 |
| fonda | 40 | 23.2 |
| papeleria | 38 | 22.0 |
| cafeteria | 27 | 15.6 |
| taller_mecanico | 26 | 15.1 |
| taqueria | 26 | 15.1 |
| tortilleria | 25 | 14.5 |
| tienda_ropa | 23 | 13.3 |
| fruteria | 21 | 12.2 |
| farmacia | 21 | 12.2 |
| ferreteria | 13 | 7.5 |
| panaderia | 10 | 5.8 |
| floreria | 9 | 5.2 |
| cafe_internet | 9 | 5.2 |
| consultorio_dental | 9 | 5.2 |
| pizzeria | 8 | 4.6 |
| bar | 7 | 4.1 |
| consultorio_medico | 7 | 4.1 |
| purificadora | 7 | 4.1 |
| tienda_celulares | 7 | 4.1 |
| laboratorio_clinico | 5 | 2.9 |
| tienda_mascotas | 5 | 2.9 |
| pasteleria | 4 | 2.3 |
| lavanderia | 4 | 2.3 |
| veterinaria | 4 | 2.3 |
| heladeria | 3 | 1.7 |
| zapateria | 3 | 1.7 |
| gimnasio | 2 | 1.2 |
| cerrajeria | 1 | 0.6 |
| libreria | 0 | 0.0 |
| spa | 0 | 0.0 |
| comida_china | 0 | 0.0 |
| sushi | 0 | 0.0 |
| escuela_idiomas | 0 | 0.0 |
| coworking | 0 | 0.0 |
| renta_bicicletas | 0 | 0.0 |
| optica | 0 | 0.0 |
| guarderia | 0 | 0.0 |

## Colonias con más negocios

Colonia = el asentamiento más frecuente del DENUE dentro de cada AGEB (`nom_colonia`); varias AGEB pueden compartir colonia. Negocios = establecimientos del DENUE 05/2026 dentro de las AGEB de esa colonia. El NSE es estimado.

| Colonia | AGEB | Habitantes | Negocios | NSE estimado |
|---|---|---|---|---|
| TEPETLIXPA | 4 | 14,845 | 949 | bajo |
| NEPANTLA DE SOR JUANA INES DE LA CRUZ | 2 | 2,266 | 138 | bajo |
| Nepantla de Sor Juana Inés de la Cruz | 1 | 48 | 0 | bajo |
| Tepetlixpa | 1 | 99 | 0 | bajo |

## Gasto potencial en comida fuera del hogar

Estimación: hogares × gasto trimestral promedio del hogar por decil (ENIGH 2024, ámbito ZMVM, pesos de 2024), ponderado por la probabilidad de decil de cada AGEB. Rubro «alimentos y bebidas consumidos fuera del hogar». Sirve para comparar zonas, no es una proyección de ventas.

- Gasto potencial total: 17.5 millones de pesos por trimestre.
- Por hogar: 4,041 pesos por trimestre (lugar 71 de 76).

## Fuentes de esta ficha
Censo 2020 (INEGI), DENUE 05/2026 y 11/2020 (INEGI), ENIGH 2024 (INEGI), IMU 2020 (CONAPO), Marco Geoestadístico 2020 (INEGI). Detalle y ligas en `01_metodologia/`. Generada el 2026-11-23 por `scripts/04a_carpetas.py`.

# Censo de Población y Vivienda 2020 (INEGI)

## Qué es y qué se usó
El Censo de Población y Vivienda 2020 es el conteo de todas las personas y viviendas del país que hace el INEGI cada diez años. El levantamiento en campo fue del 2 al 27 de marzo de 2020. Este proyecto usa el archivo de resultados por AGEB y manzana urbana de tres entidades: Ciudad de México (09), Hidalgo (13, solo Tizayuca) y Estado de México (15).
Fuente: INEGI, https://www.inegi.org.mx/programas/ccpv/2020/ . Archivos `ageb_mza_urbana_<entidad>_cpv2020_csv.zip`, descargados el 2026-11-23 (ver `data/FUENTES.md`).

## Qué es una AGEB
Una AGEB (Área Geoestadística Básica) urbana es un conjunto de manzanas delimitadas por calles, avenidas u otros rasgos fáciles de identificar, de uso principalmente habitacional, industrial, comercial o de servicios, dentro de localidades urbanas (de 2 500 habitantes o más, o cabeceras municipales). Es la unidad de análisis del proyecto: **no es lo mismo que una colonia**. Una colonia puede tener varias AGEB y una AGEB puede cortar dos colonias. Por eso el nombre de colonia que se muestra es el asentamiento más frecuente en el DENUE dentro de la AGEB.
Fuente: Marco Geoestadístico, https://www.inegi.org.mx/temas/mg/ .

## Qué trae el proyecto de cada AGEB
Población total y por edad (0-14, 15-24, 25-59 y 60 o más años), hogares, viviendas particulares habitadas, promedio de ocupantes por vivienda, escolaridad promedio (grado promedio de escolaridad de la población de 15 años y más), porcentaje de viviendas con automóvil, internet, computadora y celular, población económicamente activa y población ocupada.
- El Censo no publica por AGEB los grupos 15-29 ni 30-59; se armaron los grupos exactos que sí se pueden formar (15-24 y 25-59), restando de la población de 15 a 64 años.
- Los porcentajes de equipamiento se calculan sobre las viviendas particulares habitadas con características captadas.

## Cobertura
5 875 AGEB urbanas en los 76 municipios de la ZMVM, con 21 110 690 habitantes. En la Ciudad de México la suma por alcaldía coincide con la cifra oficial. En el Estado de México queda por debajo de la población municipal porque el proyecto solo cubre AGEB urbanas y no la población rural.
43 AGEB urbanas del Censo (157 641 habitantes, 0.75 %) no tienen polígono en la capa de AGEB urbana y quedaron fuera.

## Límites que hay que decir al usar estos datos
- Los datos son de marzo de 2020, antes de los cambios de la pandemia y con seis años de antigüedad a 2026. El proyecto no usa ningún levantamiento posterior por AGEB.
- Los valores protegidos por confidencialidad estadística (`*` y `N/D` en el archivo del INEGI) se dejan vacíos; no se inventan.
- **El Censo no trae ingreso.** El nivel socioeconómico por AGEB es una estimación propia (ver `nse_estimado.md`), no un dato del INEGI.

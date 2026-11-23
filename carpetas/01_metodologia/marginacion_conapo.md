# Índice de marginación urbana 2020 (CONAPO)

## Qué es
El Consejo Nacional de Población (CONAPO) publica el índice de marginación urbana por AGEB con base en el Censo 2020. Fuente: https://www.gob.mx/conapo/documentos/indices-de-marginacion-2020-284372 (archivo `IMU_2020.zip`, descargado el 2026-11-23 desde conapo.segob.gob.mx; publicado el 2021-09-24).

## Qué columnas trae el proyecto
- `im_2020`: el índice. **En este índice un valor ALTO significa MENOS marginación** (grado «Muy bajo» ronda 123.7 a 128; «Muy alto» ronda 93 a 115).
- `gm_2020`: grado de marginación (Muy bajo, Bajo, Medio, Alto, Muy alto).
- `imn_2020`: índice normalizado de 0 a 1.

## Cobertura y uso
168 AGEB de la ZMVM no tienen índice (CONAPO no las calcula; mediana de 19 habitantes; la mayor es población colectiva en Gustavo A. Madero). El índice sirve para contrastar el nivel socioeconómico estimado por el proyecto: la correlación de Spearman entre ambos es 0.88.

## Delimitación de la zona metropolitana
Los 76 municipios de la ZMVM vienen de la delimitación 2015 de zonas metropolitanas (SEDATU, CONAPO e INEGI): 16 alcaldías de la CDMX, 59 municipios del Estado de México y Tizayuca (Hidalgo). La edición 2020 («Metrópolis de México 2020», https://www.gob.mx/cms/uploads/sedatu/MM2020_06022024.pdf) trae 63 municipios; 14 de los 76 solo están en la edición 2015 y 1 (Atotonilco de Tula) solo en la 2020. La columna `en_delim_2020` de `zmvm_municipios.csv` lo marca.

# DENUE: Directorio Estadístico Nacional de Unidades Económicas (INEGI)

## Qué es y qué se usó
El DENUE es el directorio del INEGI con los establecimientos del país: nombre, actividad económica (clave SCIAN), tamaño por estrato de personal ocupado y ubicación con coordenadas. Se usa la descarga masiva por entidad (CDMX, Hidalgo y Estado de México) con dos cortes:
- **Corte actual: mayo de 2026** (archivo modificado el 2026-05-20): 1 081 737 establecimientos en los 76 municipios de la ZMVM.
- **Corte histórico: noviembre de 2020**, el más cercano al Censo 2020 en la sección de descargas históricas: 996 622 establecimientos.
Fuente: INEGI, https://www.inegi.org.mx/app/descarga/?ti=6 (pestaña DENUE) y https://www.inegi.org.mx/app/mapa/denue/ . Descargado el 2026-11-23; sha256 en `data/FUENTES.md`.
Comprobación: los conteos de la descarga masiva en CDMX por clase SCIAN coinciden con los de la API del DENUE (461110: 38 996; 311520: 1 090; 461170: 1 872).

## SCIAN
El DENUE clasifica cada establecimiento por su actividad principal con el Sistema de Clasificación Industrial de América del Norte (SCIAN, https://www.inegi.org.mx/app/scian/). Una clave de 6 dígitos es una clase; 2 dígitos es un sector (por ejemplo 46 = comercio al por menor, 72 = alojamiento y alimentos, 62 = salud).
- El DENUE actual dice usar SCIAN 2018, pero sus claves corresponden al catálogo SCIAN 2023 (el 100 % está en ese catálogo). El corte de 2020 usa SCIAN 2013 con algunas claves de 2018. El proyecto traduce el corte histórico al catálogo vigente con un puente empírico (columna `codigo_act_actual`).
- El DENUE clasifica por **actividad, no por producto**: una pastelería y una panadería caen en la misma clase (311812), y una pizzería, un sushi y un restaurante comparten clases. Para separar giros se filtra por el nombre del negocio (ver `06_giros/`).

## Tamaño
`per_ocu` es el estrato de personal ocupado (0 a 5, 6 a 10, 11 a 30, ..., 251 y más). El 96 % de los establecimientos de la ZMVM son de 0 a 5 personas. Para estimar empleo se usa el punto medio del estrato, y el estrato «251 y más» cuenta como 251, así que se subestima a los grandes empleadores. El 3.7 % son establecimientos semifijos (puestos).

## Límites que hay que decir al usar estos datos
- **«Apareció en el DENUE» no es lo mismo que «abrió».** Entre los dos cortes hay 651 710 identificadores en ambos, 344 912 solo en 2020 y 430 027 solo en 2026. Parte de lo nuevo es cobertura de los Censos Económicos (cargas masivas) y parte de lo que desaparece son cierres o identificadores reasignados.
- `fecha_alta` del corte actual tiene cargas masivas (2019 y 2024) y por eso no sirve para contar aperturas.
- El directorio solo distingue establecimientos fijos y semifijos; el comercio ambulante sin lugar fijo no se identifica. Los negocios informales sin registro no aparecen.
- Una competencia cercana en el DENUE no dice qué tan buena es: no hay ventas ni calidad.

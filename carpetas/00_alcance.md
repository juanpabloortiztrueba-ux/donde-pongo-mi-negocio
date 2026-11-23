# Alcance del modelo: qué cubre y qué no

## Qué cubre
El modelo responde **dónde conviene poner un negocio dentro de la Zona Metropolitana del Valle de México (ZMVM)**: las 16 alcaldías de la Ciudad de México, 59 municipios del Estado de México y Tizayuca (Hidalgo), 76 en total, según la delimitación 2015 de SEDATU, CONAPO e INEGI. La unidad de análisis es la AGEB urbana (5 875 en total) y se reporta con el nombre de colonia más frecuente del DENUE. La lista de municipios está en `03_municipios/00_resumen_zmvm.md`.
Los 40 giros que entiende están en `06_giros/`.

## Qué no cubre (responder «fuera de alcance» o «NO ENCONTRADO»)
- **Cualquier ciudad fuera de la ZMVM**: Monterrey, Guadalajara, Puebla, Toluca, Querétaro, Cuernavaca, Pachuca, etc. No hay datos de esas ciudades en el proyecto. No se debe contestar con colonias de la ZMVM como si fueran de otra ciudad.
- **Municipios del Estado de México y de Hidalgo que no están entre los 76**.
- **Zonas rurales**: solo hay AGEB urbanas; 43 AGEB urbanas del Censo (0.75 % de la población) quedaron sin polígono.
- **Rentas, precios de locales, flujo peatonal por calle, seguridad, permisos y ventas reales**: no hay datos de eso en el proyecto.
- **Giros que no están en el catálogo**: se puede aproximar con el giro más parecido, y hay que decirlo.

## Qué fuentes usa
Censo 2020 (INEGI), DENUE 2020 y 2026 (INEGI), ENIGH 2024 (INEGI), índice de marginación urbana 2020 (CONAPO), series de Banxico e INEGI para el contexto macro, y datos abiertos de transporte de la CDMX (y OpenStreetMap para Mexibús y Mexicable). Detalle en `01_metodologia/`.

## Regla de honestidad
Toda cifra tiene fuente. Lo que no está en los datos se dice «NO ENCONTRADO»; no se inventan colonias, cifras ni referencias.

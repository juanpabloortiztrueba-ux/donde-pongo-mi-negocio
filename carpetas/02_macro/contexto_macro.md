# Contexto macroeconómico de México

Generado por `scripts/04a_carpetas.py` desde `data/processed/macro.json` (última lectura de las series: 2026-11-23). Cada cifra trae fecha, número de serie y fuente. Las lecturas en «Qué significa» son interpretación del proyecto, no dato oficial.

## Precios y tasas

- **Inflación general anual (INPC)**: 3.75 % variacion anual (dato de 2026-10, serie 910406). Fuente: INEGI, Banco de Indicadores API (BIE, id 910406); https://www.inegi.org.mx/app/indicadores/. Consultado el 2026-11-23. Índice base 2018 = 147.026.
- **Tasa objetivo de Banxico**: 6.25 % anual (dato de 2026-11-23, serie SF61745). Fuente: Banco de Mexico, SIE API (serie SF61745); https://www.banxico.org.mx/SieInternet/. Consultado el 2026-11-23.
- **TIIE a 28 días**: 6.515 % anual (dato de 2026-11-23, serie SF43783). Fuente: Banco de Mexico, SIE API (serie SF43783); https://www.banxico.org.mx/SieInternet/. Consultado el 2026-11-23.
- Tasa real aproximada (tasa objetivo menos inflación anual de 2026-10): 2.50 puntos porcentuales. Cálculo del proyecto.

## Inflación de alimentos

**NO ENCONTRADO**: El subindice de INPC 'Alimentos, bebidas y tabaco' (por objeto del gasto) no se encontro en la API de indicadores del INEGI ni en el SIE de Banxico. Ver evidencia y proxies.

Aproximaciones oficiales que sí existen (son proxies, no la inflación de alimentos):

- **Agropecuarios (proxy)**: 2.99 % variacion anual (dato de 2026-10, serie 910411). Fuente: INEGI, Banco de Indicadores API (BIE, id 910411); https://www.inegi.org.mx/app/indicadores/. Consultado el 2026-11-23.
- **Mercancías (proxy)**: 3.25 % variacion anual (dato de 2026-10, serie 910408). Fuente: INEGI, Banco de Indicadores API (BIE, id 910408); https://www.inegi.org.mx/app/indicadores/. Consultado el 2026-11-23.

## Tipo de cambio, remesas y consumo

- **Tipo de cambio FIX**: 19.02 MXN por USD (dato de 2026-11-20, serie SF43718). Fuente: Banco de Mexico, SIE API (serie SF43718); https://www.banxico.org.mx/SieInternet/. Consultado el 2026-11-23.
- **Remesas familiares (mensual)**: 5,362 millones de USD (mensual) (dato de 2026-09-01, serie SE27803). Fuente: Banco de Mexico, SIE API (serie SE27803); https://www.banxico.org.mx/SieInternet/. Consultado el 2026-11-23. Variación anual: 1.55 %. Acumulado de 12 meses: 63,452 millones de USD.
- **Confianza del consumidor**: 45.19 puntos (indice) (dato de 2026-10, serie 454168). Fuente: INEGI, Banco de Indicadores API (BIE, id 454168); https://www.inegi.org.mx/app/indicadores/. Consultado el 2026-11-23. Serie 454168 del BIE tal cual; no se verifico si es desestacionalizada.
- **Consumo privado (IMCP, variación anual)**: 1.343 % variacion anual (cifras originales) (dato de 2026-08, serie 740946). Fuente: INEGI, Banco de Indicadores API (BIE, id 740946); https://www.inegi.org.mx/app/indicadores/. Consultado el 2026-11-23. Índice de volumen base 2018 = 115.83. variacion anual recalculada desde el indice 740933: 1.34%; ids confirmados contra el boletin IMCP de INEGI (imcpmi2026_08.pdf)

## Qué significa para quien abre un negocio
Interpretación del proyecto, a partir de las cifras anteriores:

- Con tasa objetivo de 6.25 % e inflación de 3.75 %, el crédito sigue caro en términos reales (2.5 puntos): financiar la apertura con deuda pesa más que con ahorro propio.
- Con inflación de 3.75 %, los costos de insumos y rentas suben a ese ritmo en promedio; el ticket tiene que ajustarse en lo mismo para mantener el margen.
- El consumo privado crece 1.34 % anual (2026-08) y la confianza del consumidor está en 45.2 puntos (2026-10): la demanda crece poco.
- Las remesas son un dato nacional; este proyecto no las tiene desagregadas por municipio ni por colonia (NO ENCONTRADO).

## Límites
Son cifras nacionales. No se encontró en esta fuente un indicador macro específico de la ZMVM; el nivel de ingreso local viene de la ENIGH y está en `01_metodologia/`.

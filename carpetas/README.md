# Carpetas de información del modelo

Estas carpetas son la base de conocimiento que consulta el modelo (RAG: se busca por significado en estos textos y la respuesta se escribe con lo que se encuentra). Todo es Markdown. Lo que dice una carpeta viene de una fuente citada en el mismo archivo; lo que no se encontró se marca «NO ENCONTRADO».

| Carpeta | Qué contiene | Cómo se hizo |
|---|---|---|
| `00_alcance.md` | Qué cubre el modelo (la ZMVM, 76 municipios, 40 giros) y qué no (otras ciudades, rentas, flujo peatonal) | Escrito a mano |
| `01_metodologia/` | Cómo se construyeron los datos: Censo 2020, DENUE, ENIGH 2024, marginación de CONAPO y la estimación del nivel socioeconómico | Escrito a mano, resumido de la documentación oficial, con liga. `enigh_zmvm_deciles.md` sale de código |
| `02_macro/` | Contexto macroeconómico (inflación, tasa de Banxico, tipo de cambio, remesas, confianza del consumidor, consumo privado) | Generado desde `data/processed/macro.json` |
| `03_municipios/` | Una ficha por cada uno de los 76 municipios y alcaldías de la Zona Metropolitana del Valle de México, más un resumen comparativo | Generado desde `data/processed/agebs_features.parquet` y el DENUE |
| `04_teoria_localizacion/` | Marco teórico de localización de negocios (Reilly, Huff, Hotelling, Christaller, aglomeración, entrada de empresas) y referencias verificadas | Escrito a mano; cada referencia se verificó (DOI en Crossref u OpenAlex, libros en Open Library) |
| `05_modelo/` | Qué hace el modelo de aperturas, cómo se valida y qué no puede decir | Generado por `scripts/04a_carpetas.py` leyendo `reports/validacion.md` |
| `06_giros/` | Catálogo de giros: códigos SCIAN, radio, cliente objetivo y gasto de referencia | Generado desde `config/giros.yaml` |

## Cómo regenerar

```
uv run python scripts/04a_carpetas.py      # regenera lo generado (municipios, macro, giros, modelo)
uv run python scripts/04_indexar.py        # lo anterior más los embeddings en data/index/chunks.parquet
```

Los textos escritos a mano no los toca ningún script.

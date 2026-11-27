# rag_local.R: RAG local en R con Ollama, adaptado de la guía del profesor.
# Se corre desde la raíz del repo: Rscript rag_r/rag_local.R (antes, Rscript rag_r/00_corpus.R)
# Requisitos: Ollama abierto, embeddinggemma y qwen3:1.7b descargados, install.packages("httr2")

dir.create("rag_r/salidas", showWarnings = FALSE)
sink("rag_r/salidas/salida_completa.txt", split = TRUE)   # guarda todo lo que imprime la corrida

# 1. Conexión y corpus
base <- "http://127.0.0.1:11434"
modelo_chat <- "qwen3:1.7b"
modelo_embedding <- "embeddinggemma"
ollama <- function(ruta, datos = NULL) {
  req <- httr2::request(paste0(base, ruta))
  req <- httr2::req_timeout(req, 180)
  if (!is.null(datos)) req <- httr2::req_body_json(req, datos)
  httr2::resp_body_json(httr2::req_perform(req), simplifyVector = TRUE)
}
print(ollama("/api/version"))
corpus <- read.csv("rag_r/corpus.csv", fileEncoding = "UTF-8")
stopifnot(nrow(corpus) > 0, !anyDuplicated(corpus$id))

# 2. Embeddings y recuperación
# Los textos se mandan por lotes de 32 para no saturar a Ollama.
embeddings <- function(textos) {
  lotes <- split(seq_along(textos), ceiling(seq_along(textos) / 32))
  salida <- lapply(lotes, function(i) {
    as.matrix(ollama("/api/embed", list(model = modelo_embedding, input = as.list(textos[i])))$embeddings)
  })
  do.call(rbind, salida)
}
# El índice se guarda en rag_r/indice.rds; se reconstruye si cambia el corpus o el modelo.
archivo_indice <- "rag_r/indice.rds"
guardado <- if (file.exists(archivo_indice)) readRDS(archivo_indice) else NULL
if (!is.null(guardado) && identical(guardado$modelo, modelo_embedding) &&
    identical(guardado$id, corpus$id) && identical(guardado$texto, corpus$texto)) {
  indice <- guardado$indice
  cat("Índice cargado de", archivo_indice, "\n")
} else {
  indice <- embeddings(corpus$texto)
  saveRDS(list(modelo = modelo_embedding, id = corpus$id, texto = corpus$texto, indice = indice), archivo_indice)
  cat("Índice reconstruido y guardado en", archivo_indice, "\n")
}
cat("Índice:", nrow(indice), "fragmentos x", ncol(indice), "dimensiones\n")
recuperar <- function(pregunta, k = 3L) {
  consulta <- as.numeric(embeddings(pregunta)[1, ])
  producto <- drop(indice %*% consulta)
  normas <- sqrt(rowSums(indice^2)) * sqrt(sum(consulta^2))
  similitud <- producto / normas
  filas <- head(order(similitud, decreasing = TRUE), k)
  resultado <- corpus[filas, , drop = FALSE]
  resultado$similitud <- similitud[filas]
  resultado
}

# 3. Respuesta y pruebas
# El razonamiento de qwen3 llega en message$thinking, no en content (ver rag_r/README.md).
responder <- function(pregunta, fragmentos) {
  pasajes <- sprintf("[%s] %s\n%s", fragmentos$id, fragmentos$fuente, fragmentos$texto)
  contexto <- if (length(pasajes)) paste(pasajes, collapse = "\n\n") else "(Sin fragmentos)"
  respuesta <- ollama("/api/chat", list(
    model = modelo_chat, stream = FALSE, options = list(temperature = 0),
    messages = list(
      list(role = "system", content = "Usa solo los fragmentos. Cita los IDs entre corchetes. Si falta evidencia, responde: No hay evidencia suficiente en los fragmentos."),
      list(role = "user", content = paste("Fragmentos", contexto, "Pregunta", pregunta, sep = "\n"))
    )
  ))
  respuesta$message$content
}
preguntas <- read.csv("rag_r/preguntas.csv", fileEncoding = "UTF-8")
stopifnot(nrow(preguntas) == 8L, !anyDuplicated(preguntas$id))
tabla_recuperados <- list()
tabla_respuestas <- list()
for (i in seq_len(nrow(preguntas))) {
  consulta <- preguntas$pregunta[i]
  fragmentos <- recuperar(consulta)
  respuesta <- responder(consulta, fragmentos)
  cat("\nPregunta:", consulta, "\n")
  print(fragmentos[, c("id", "fuente", "similitud")])
  cat(sprintf("\n[%s]\n%s\n", fragmentos$id, fragmentos$texto), sep = "")
  cat("Respuesta:", respuesta, "\n")
  tabla_recuperados[[i]] <- data.frame(
    id_pregunta = preguntas$id[i], pregunta = consulta, lugar = 1:nrow(fragmentos),
    id = fragmentos$id, fuente = fragmentos$fuente, similitud = fragmentos$similitud)
  tabla_respuestas[[i]] <- data.frame(
    id_pregunta = preguntas$id[i], pregunta = consulta,
    ids_recuperados = paste(fragmentos$id, collapse = " "), respuesta = respuesta)
}
recuperados <- do.call(rbind, tabla_recuperados)
respuestas <- do.call(rbind, tabla_respuestas)
write.csv(recuperados, "rag_r/salidas/recuperados.csv", row.names = FALSE, fileEncoding = "UTF-8")
write.csv(respuestas, "rag_r/salidas/respuestas.csv", row.names = FALSE, fileEncoding = "UTF-8")

# Prueba controlada. La fuente se selecciona del corpus completo.
pregunta <- "¿Cuál es el gasto potencial total en comida fuera del hogar de Coyoacán por trimestre?"
id_evidencia <- "D11-F10"
dato_clave <- "2,120.2"
evidencia <- corpus[corpus$id == id_evidencia, , drop = FALSE]
stopifnot(nrow(evidencia) == 1L, grepl(dato_clave, evidencia$texto, fixed = TRUE))
distractores <- recuperar(pregunta, nrow(corpus))
# Ningún distractor puede traer el dato.
distractores <- distractores[distractores$id != id_evidencia & !grepl(dato_clave, distractores$texto, fixed = TRUE), names(corpus)]
distractores <- head(distractores, 2)
con_evidencia <- responder(pregunta, rbind(evidencia, distractores))
sin_evidencia <- responder(pregunta, distractores)
cat("Con evidencia\n", con_evidencia, "\n")
cat("Sin evidencia\n", sin_evidencia, "\n")
prueba <- c(
  paste("Pregunta:", pregunta),
  paste("ID de la evidencia:", id_evidencia),
  paste("Dato clave:", dato_clave),
  paste("IDs de los distractores:", paste(distractores$id, collapse = " ")),
  "", "Texto de los distractores", paste0("[", distractores$id, "] ", distractores$texto),
  "", "Con evidencia", con_evidencia,
  paste("Menciona el dato clave:", ifelse(grepl(dato_clave, con_evidencia, fixed = TRUE), "sí", "no")),
  "", "Sin evidencia", sin_evidencia,
  paste("Menciona el dato clave:", ifelse(grepl(dato_clave, sin_evidencia, fixed = TRUE), "sí", "no")))
writeLines(prueba, "rag_r/salidas/prueba_controlada.txt", useBytes = TRUE)

# 4. Tabla de evaluación
# Columnas automáticas + columnas de lectura humana (rag_r/lectura_evaluacion.csv).
sino <- function(x) ifelse(x, "sí", "no")
citados <- regmatches(respuestas$respuesta, gregexpr("D[0-9]+-F[0-9]+", respuestas$respuesta))
tabla <- data.frame(
  id_pregunta = respuestas$id_pregunta,
  pregunta = respuestas$pregunta,
  tipo = preguntas$tipo,
  ids_recuperados = respuestas$ids_recuperados,
  similitud_maxima = round(tapply(recuperados$similitud, recuperados$id_pregunta, max)[respuestas$id_pregunta], 4),
  cita_id = sino(grepl("\\[[^]]*D[0-9]+-F[0-9]+[^]]*\\]", respuestas$respuesta)),
  ids_citados = vapply(citados, function(x) paste(unique(x), collapse = " "), character(1)),
  cita_ids_no_recuperados = sino(vapply(seq_along(citados), function(j) any(!citados[[j]] %in% strsplit(respuestas$ids_recuperados[j], " ")[[1]]), logical(1))),
  dice_no_hay_evidencia = sino(grepl("No hay evidencia suficiente en los fragmentos", respuestas$respuesta, fixed = TRUE)),
  stringsAsFactors = FALSE)
rownames(tabla) <- NULL
lectura <- read.csv("rag_r/lectura_evaluacion.csv", fileEncoding = "UTF-8", colClasses = "character")
tabla <- cbind(tabla, lectura[match(tabla$id_pregunta, lectura$id_pregunta), -1])
write.csv(tabla, "rag_r/salidas/tabla_evaluacion.csv", row.names = FALSE, fileEncoding = "UTF-8")
cat("\nTabla de evaluación\n")
print(tabla[, c("id_pregunta", "tipo", "similitud_maxima", "cita_id", "dice_no_hay_evidencia")])
sink()

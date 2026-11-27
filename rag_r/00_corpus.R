# 00_corpus.R: arma rag_r/corpus.csv a partir de carpetas/*.md
# Se corre desde la raíz del repo: Rscript rag_r/00_corpus.R
# Solo R base. Cada fragmento = una sección (##) o parte de ella, de 40 a 200 palabras.

# 1. Parámetros
carpeta <- "carpetas"
salida <- "rag_r/corpus.csv"
min_palabras <- 40
max_palabras <- 200

palabras <- function(x) length(strsplit(trimws(x), "[[:space:]]+")[[1]])

# 2. Archivos (todos los .md menos el README de carpetas)
archivos <- sort(list.files(carpeta, pattern = "\\.md$", recursive = TRUE), method = "radix")
archivos <- archivos[archivos != "README.md"]
stopifnot(length(archivos) > 0)

# 3. Un archivo -> bloques (párrafos o tablas) con su encabezado ## y ###
leer_bloques <- function(ruta) {
  lineas <- readLines(file.path(carpeta, ruta), encoding = "UTF-8", warn = FALSE)
  titulo <- sub("^# ", "", lineas[grep("^# ", lineas)[1]])
  h2 <- "Introducción"
  h3 <- ""
  bloques <- list()
  actual <- character(0)
  guardar <- function() {
    if (length(actual) > 0) {
      bloques[[length(bloques) + 1]] <<- list(h2 = h2, h3 = h3, lineas = actual)
      actual <<- character(0)
    }
  }
  for (l in lineas) {
    if (grepl("^# ", l)) {
      next
    } else if (grepl("^## ", l)) {
      guardar(); h2 <- sub("^## ", "", l); h3 <- ""
    } else if (grepl("^### ", l)) {
      guardar(); h3 <- sub("^### ", "", l)
    } else if (grepl("^[[:space:]]*$", l)) {
      guardar()
    } else {
      actual <- c(actual, l)
    }
  }
  guardar()
  list(titulo = titulo, bloques = bloques)
}

# 4. Un bloque muy largo se parte por renglones (en las tablas se repite el encabezado)
partir_bloque <- function(lineas) {
  if (palabras(paste(lineas, collapse = " ")) <= max_palabras) return(list(lineas))
  es_tabla <- grepl("^\\|", lineas[1]) && length(lineas) > 2
  cabecera <- if (es_tabla) lineas[1:2] else character(0)
  cuerpo <- if (es_tabla) lineas[-(1:2)] else lineas
  partes <- list()
  parte <- character(0)
  for (l in cuerpo) {
    prueba <- c(cabecera, parte, l)
    if (length(parte) > 0 && palabras(paste(prueba, collapse = " ")) > max_palabras) {
      partes[[length(partes) + 1]] <- c(cabecera, parte)
      parte <- character(0)
    }
    parte <- c(parte, l)
  }
  partes[[length(partes) + 1]] <- c(cabecera, parte)
  partes
}

# 5. Bloques -> fragmentos (se juntan los bloques de la misma sección hasta max_palabras;
#    si se pegan dos secciones, la fuente las nombra a las dos)
armar_fragmentos <- function(doc) {
  frags <- list()
  for (b in doc$bloques) {
    for (p in partir_bloque(b$lineas)) {
      txt <- paste(p, collapse = "\n")
      n <- length(frags)
      if (n > 0 && frags[[n]]$h2 == b$h2 && frags[[n]]$h3 == b$h3 &&
          palabras(frags[[n]]$texto) + palabras(txt) <= max_palabras) {
        frags[[n]]$texto <- paste(frags[[n]]$texto, txt, sep = "\n\n")
      } else {
        etiqueta <- if (nzchar(b$h3)) paste(b$h2, b$h3, sep = " › ") else b$h2
        frags[[n + 1]] <- list(h2 = b$h2, h3 = b$h3, etiquetas = etiqueta, texto = txt)
      }
    }
  }
  # los fragmentos cortos se pegan al anterior o al siguiente, sin pasar de max_palabras
  i <- 1
  while (i <= length(frags)) {
    pegado <- FALSE
    if (length(frags) > 1 && palabras(frags[[i]]$texto) < min_palabras) {
      for (j in c(i - 1, i + 1)) {
        if (!pegado && j >= 1 && j <= length(frags) &&
            palabras(frags[[j]]$texto) + palabras(frags[[i]]$texto) <= max_palabras) {
          a <- min(i, j); b <- max(i, j)
          frags[[a]]$texto <- paste(frags[[a]]$texto, frags[[b]]$texto, sep = "\n\n")
          frags[[a]]$etiquetas <- unique(c(frags[[a]]$etiquetas, frags[[b]]$etiquetas))
          frags[[b]] <- NULL
          pegado <- TRUE
        }
      }
    }
    if (!pegado) i <- i + 1
  }
  frags
}

# 6. Recorre los archivos y arma la tabla
filas <- list()
for (d in seq_along(archivos)) {
  doc <- leer_bloques(archivos[d])
  frags <- armar_fragmentos(doc)
  for (f in seq_along(frags)) {
    fr <- frags[[f]]
    seccion <- paste(fr$etiquetas, collapse = " + ")
    filas[[length(filas) + 1]] <- data.frame(
      id = sprintf("D%02d-F%02d", d, f),
      fuente = paste0("carpetas/", archivos[d], " › ", seccion),
      # el texto lleva el título del documento y la sección para que se entienda solo
      texto = paste0(doc$titulo, " › ", seccion, "\n", fr$texto),
      stringsAsFactors = FALSE
    )
  }
}
corpus <- do.call(rbind, filas)
stopifnot(nrow(corpus) > 0, !anyDuplicated(corpus$id))

# 7. Guarda en UTF-8 y resume
write.csv(corpus, salida, row.names = FALSE, fileEncoding = "UTF-8")
n_pal <- vapply(corpus$texto, palabras, numeric(1))
cat("Archivos:", length(archivos), "\n")
cat("Fragmentos:", nrow(corpus), "\n")
cat("Palabras por fragmento (mínimo, mediana, máximo):", min(n_pal), median(n_pal), max(n_pal), "\n")
cat("Guardado en", salida, "\n")

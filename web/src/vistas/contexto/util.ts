// Utilidades de las vistas del grupo «contexto»: tipos de la API (app/api/contexto.py), fechas y bytes en es-MX.

export interface Indicador {
  valor?: number; unidad?: string; fecha?: string; id_serie?: string; titulo_serie?: string; descripcion_serie?: string; fuente?: string; consultado?: string
  variacion_anual_pct?: number; acumulado_12_meses_millones_usd?: number; estado?: string; detalle?: string
  proxies?: Record<string, Indicador>
}
export interface SerieMacro {
  clave: string; nombre: string; unidad: string; agregacion: string; tono: 'naranja' | 'azul' | 'gris' | 'verde'; tema: string
  id_serie: string; fuente: string; periodicidad: string; ultimo: { fecha: string; valor: number | null }; desde: string; n_datos: number
  puntos: [string, number][]
}
export interface MacroResp { indicadores: Record<string, Indicador>; series: SerieMacro[]; meta: { generado?: string }; aviso: string | null; fuente: string }

export interface Termino { clave: string; nombre: string; descripcion: string; peso: number; peso_norm: number }
export interface GiroAuc {
  giro: string; nombre: string; tasa_base: number | null; agebs_con_apertura: number; poco_dato: boolean
  auc_modelo: number | null; auc_densidad: number | null; auc_competencia: number | null; auc_comp_ageb: number | null; auc_actividad: number | null; auc_score: number | null
}
export interface Cifra { etiqueta: string; valor: number | null; formato: 'n' | 'pct' | 'auc' }
export interface Limite { clave: string; titulo: string; texto: string; fuente: string; cifras: Cifra[] }
export interface PreguntaProfe { pregunta: string; respuesta: string; fuente: string }
export interface FilaEval { id: number; pregunta: string; latencia_s: number | null; pasa: boolean; tipo: string | null; modo: string | null }
export interface ModeloResp {
  score: { version: string | null; origen: string; terminos: Termino[]; suma_pesos: number; sin_redondear: Record<string, number> | null; por_pliegue: Record<string, number>[] | null; objetivos: string[] | null; fecha: string | null; origen_pesos: string | null }
  modelo: { nombre: string; sklearn: string; id: string; fecha: string; n_variables: number; n_giros: number; iteraciones: number; filas_entrenamiento: number; cortes: { features: string; etiqueta: string }; segundos: number }
  validacion: { auc_global: number | null; ap_global: number | null; tasa_base: number | null; pliegues: { pliegue: number; auc: number; n_test: number; municipios: number }[]; metodo: string; fuente: string }
  sobrevivencia: { auc_oof: number | null; ap_oof: number | null; tasa_sobrevive: number | null; n: number | null }
  giros: GiroAuc[]
  lineas_base: { giros: number; modelo_promedio: number | null; supera: Record<string, number>; promedio: Record<string, number | null> }
  importancia: { variable: string; nombre: string; importancia: number | null; sd: number | null }[]
  evaluacion: { fecha: string; modelo: string; preguntas: number; pasan: number; aprobado: boolean; trampa_pasa: boolean; latencia_mediana_s: number; latencia_p90_s: number; latencia_max_s: number; mediana_bajo_objetivo: boolean; criterios: { latencia_max_s: number; mediana_objetivo_s: number }; filas: FilaEval[]; fuente: string } | Record<string, never>
  validacion_score: { version: string; filas: { objetivo: string; etiqueta: string; metrica: string; vigente: number | null; vigente_oos?: number | null; anterior: number | null; mejor_base: number | null; mejor_base_nombre: string | null; modelo_dedicado: number | null }[]; fuente: string } | Record<string, never>
  limites: Limite[]
  preguntas: PreguntaProfe[]
  fuentes: { giros: string; importancia: string }
}
export interface EjemploScore {
  giro: string; nombre_giro: string; posicion: number; cvegeo: string; colonia: string; municipio: string; score: number; suma_terminos: number
  terminos: { clave: string; nombre: string; peso: number; peso_norm: number; percentil: number; aporte: number; acumulado: number }[]
  sin_demanda_enigh: boolean; score_version: string; fuente: string
}

export interface FilaFuente { archivo: string; url: string; descarga: string; corte: string; tamano: string; bytes: number | null; sha256: string; nota: string }
export interface FuentesResp {
  secciones: { titulo: string; texto: string[]; filas: FilaFuente[] }[]; n_fuentes: number; cortes: Record<string, string | null>
  procesados: { archivo: string; bytes: number }[]; bytes_procesados: number
  reconstruir: { comando: string; pasos: { objetivo: string; descripcion: string }[]; setup: { objetivo: string; descripcion: string } | null }; fuente: string
}
export interface NodoCarpeta { nombre: string; ruta: string; tipo: 'carpeta' | 'archivo'; hijos?: NodoCarpeta[]; archivos?: number; trozos: number; titulo?: string; bytes?: number; descripcion?: string }
export interface CarpetasResp { nodos: NodoCarpeta[]; archivos: number; trozos: number; indice: { modelo_embeddings?: string; dim?: number; creado?: string; max_chars?: number }; fuente: string }
export interface DocResp { ruta: string; titulo: string; markdown: string; bytes: number; trozos: number; fuente: string }
export interface BusquedaResp { q: string; modo: 'vectorial' | 'lexico' | null; k: number; aviso: string | null; resultados: { archivo: string; seccion: string; texto: string; score: number | null; municipio: string }[]; fuente: string }
export interface DescargasResp { descargas: { archivo: string; descripcion: string; ruta: string; origen: string; disponible: boolean }[] }

const MESES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']
/** «2026-11-23» → «23 nov 2026»; «2026-10» → «oct 2026». */
export function fecha(s: string | null | undefined): string {
  if (!s) return 'NO ENCONTRADO'
  const m = /^(\d{4})-(\d{2})(?:-(\d{2}))?/.exec(s)
  if (!m) return s
  const mes = MESES[Number(m[2]) - 1] ?? m[2]
  return m[3] ? `${Number(m[3])} ${mes} ${m[1]}` : `${mes} ${m[1]}`
}
/** Bytes legibles en unidades decimales (como Finder y las páginas de descarga): 11,434,836 → «11.4 MB». */
export function fmtBytes(n: number | null | undefined): string {
  if (n == null || !Number.isFinite(n)) return 'NO ENCONTRADO'
  const u = ['B', 'kB', 'MB', 'GB']
  let i = 0, v = n
  while (v >= 1000 && i < u.length - 1) { v /= 1000; i++ }
  return `${new Intl.NumberFormat('es-MX', { maximumFractionDigits: i ? 1 : 0, minimumFractionDigits: i ? 1 : 0 }).format(v)} ${u[i]}`
}

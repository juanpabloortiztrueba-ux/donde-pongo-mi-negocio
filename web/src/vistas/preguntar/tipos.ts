// Tipos de la API de preguntar (app/api/preguntar.py). Solo describen lo que regresa el servidor.

export interface ZonaTop {
  colonia: string; municipio: string; ageb: string; score: number | null; rank_zmvm?: number
  prob_apertura_pct: number | string | null; prob_sigue_abierto_pct?: number | string | null
  gasto_potencial_trim_mxn: number | string | null; competidores_ponderados: number | string | null
  captura_huff_pct: number | string | null; complementarios_ponderados?: number | string | null
  nse_estimado: string | null; decil_estimado: number | string | null; ingreso_trim_mediano_estimado_mxn: number | string | null
  edad_clave_etiqueta: string; edad_clave_pct: number | string | null; edad_clave_pct_zmvm: number | string | null
  poblacion_ageb_2020: number | string | null; radio_m: number; resumen_texto: string
  dist_a_colonia_km?: number; en_colonia_consultada?: boolean
}

export interface SugerenciaGiro {
  giro: string; nombre: string | null; viabilidad_pct: number; prob_apertura_pct: number; prob_sigue_abierto_pct: number
  score_relativo_medio_top10: number | null; ticket_promedio_mxn: number | null
}

/** Qué clase de pregunta fuera de tema detectó el backend: un saludo, una pregunta por el nombre del agente o algo ajeno al negocio. */
export type TipoFueraDeTema = 'saludo' | 'nombre' | 'ajeno'

export interface DatosPregunta {
  /** Si el backend lo marca aquí también, vale igual que en el resultado del trabajo. */
  fuera_de_tema?: boolean
  giro: { clave: string; nombre: string } | null
  zonas: ZonaTop[]
  fuentes: string[]
  corte_denue: string | null
  perfil?: {
    coincidencia: string | null; ticket_promedio_mxn: number | null; ticket_fuente: string | null; radio_influencia_m: number | null
    nse_objetivo: Record<string, number> | null; cliente_objetivo_edades: Record<string, number> | null; demanda_base: string | null
    notas: string | null; aviso_rubro?: string | null
  }
  perfil_no_encontrado?: { motivo: string; propuestas_scian: { scian: string; titulo: string; establecimientos_zmvm_2026: number }[] }
  filtros?: Record<string, string | number> | null
  agebs_evaluadas?: number
  metodo?: string; como_leer_score?: string
  edad_clave?: { grupo: string; etiqueta: string; pct_zmvm: number | null } | null
  aviso_prob_baja?: string | null; aviso_colonia?: string | null; avisos?: string[]
  mapa?: { valores: Record<string, number>; municipio: string | null } | null
  fuera_de_alcance?: { fuera_de_zmvm: boolean; motivo: string; sugerencias: string[] }
  sugerencias?: SugerenciaGiro[]; sugerencias_como_leer?: string; sugerencias_filtros?: Record<string, string> | null
  macro?: { linea: string; fuentes: string[] }
  municipio?: { nombre: string; ficha: string[]; fuentes: string[] }
}

export interface Herramienta { nombre: string; args: Record<string, unknown>; resultado: unknown }

export type EstadoPregunta = 'en_cola' | 'pensando' | 'listo' | 'error' | 'cancelada'
export interface VistaTrabajo {
  id: string; estado: EstadoPregunta; posicion_en_cola: number; segundos: number; pregunta: string
  respuesta: string | null; latencia_s: number | null; modo: 'llm' | 'rapido' | 'plantilla' | null; modelo: string | null
  aviso: string | null; error: string | null; herramientas: Herramienta[]; fuentes?: string[]
  /** true si la pregunta no es de negocios (saludo, nombre del agente, tema ajeno): solo hay texto, sin zonas ni mapa. false o ausente en las normales. */
  fuera_de_tema?: boolean; tipo_fuera_de_tema?: TipoFueraDeTema | null
  detalle: { rondas?: number; herencia?: Record<string, string> | null; cortada?: boolean; metricas?: Record<string, number> } | null
}
export interface RespuestaCrear extends VistaTrabajo { datos: DatosPregunta; segundos_consulta: number; ollama: boolean }

/** Una vuelta del hilo: lo que se guarda en sessionStorage (sin el mapa ni los resultados de las herramientas, que son pesados). */
export interface Turno {
  k: string
  pregunta: string
  rapido: boolean
  /** hora local en que se envió */
  creada: number
  /** consultando: el POST sigue en vuelo; si no, estado del trabajo en el servidor */
  fase: 'consultando' | EstadoPregunta | 'falla'
  id?: string
  datos?: DatosPregunta
  respuesta?: string | null
  modo?: VistaTrabajo['modo']
  modelo?: string | null
  latencia_s?: number | null
  aviso?: string | null
  error?: string | null
  fuentes?: string[]
  posicion?: number
  segundos?: number
  /** momento (Date.now()) en que llegó `segundos`, para seguir contando entre sondeos */
  t_seg?: number
  herramientas?: Herramienta[]
  fuera_de_tema?: boolean
  tipo_fuera_de_tema?: TipoFueraDeTema | null
}

/** Una respuesta fuera de tema muestra solo el texto: sin tarjetas, sin «Top 5», sin mapa ni resaltado. Lo dice el backend (`fuera_de_tema`)
 *  o lo delata una lista de zonas vacía junto a un giro que sí se entendió (no es un fuera de alcance, un giro desconocido ni una sugerencia de giros). */
export function esFueraDeTema(t: Pick<Turno, 'fuera_de_tema' | 'datos'>): boolean {
  if (t.fuera_de_tema === true || t.datos?.fuera_de_tema === true) return true
  const d = t.datos
  return !!d && d.zonas.length === 0 && !d.giro && !d.fuera_de_alcance && !d.perfil_no_encontrado && !d.sugerencias?.length && !d.macro && !d.municipio && !d.perfil
}

// ---- Ficha
export interface Comp { pct: number | null; pct_zmvm: number | null }
export interface FichaZona {
  encontrado: boolean; ageb: string; colonia: string | null; municipio: string; cvegeo_mun: string
  tipo_asentamiento: string | null; cp: string | null; colonia_fuente?: string | null; lat: number; lon: number
  poblacion: { habitantes: number | null; hogares: number | null; viviendas: number | null; ocupantes_por_vivienda: number | null; densidad_hab_km2: number | null; area_km2: number | null; fuente: string }
  edades: { grupos: { grupo: string; etiqueta: string; personas: number | null; pct: number | null; pct_zmvm: number | null }[]; fuente: string }
  vivienda: { bienes: { clave: string; etiqueta: string; pct: number | null; pct_zmvm: number | null }[]; fuente: string }
  escolaridad: { anios: number | null; anios_zmvm: number | null; fuente: string }
  marginacion: { grado: string | null; indice: number | null; indice_normalizado: number | null; grados_zmvm: { grado: string; agebs: number }[]; n_agebs: number; sin_grado: number; fuente: string }
  ingreso: { decil: number | null; nse: string | null; ingreso_trim_mediano: number | null; prob_deciles_pct: (number | null)[]; prob_deciles_zmvm_pct: (number | null)[]; prob_nse_pct: Record<string, number | null>; fuente: string }
  empleo: {
    sectores: { clave: string; nombre: string; n_500m: number | null; n_1km: number | null }[]
    negocios_500m: number | null; negocios_1km: number | null; empleos_500m: number | null; empleos_1km: number | null
    negocios_en_ageb: number | null; empleos_en_ageb: number | null; escuelas_1km: number | null; hospitales_1km: number | null; plazas_1km: number | null; fuente: string
  }
  transporte: { estacion: string | null; sistema: string | null; distancia_m: number | null; metro: string | null; distancia_metro_m: number | null; afluencia_metro_anual: number | null; estaciones_1km: number | null; fuente: string }
  fuentes: string[]
  giro?: {
    clave: string; nombre: string | null; score: number | null; rank_zmvm: number; de_agebs: number; percentil: number | null; en_top_5: boolean
    prob_apertura_pct: number | string | null; prob_sigue_abierto_pct: number | string | null; aperturas_esperadas_en_radio: number | string | null
    gasto_potencial_trim_mxn: number | string | null; competidores_ponderados: number | string | null; captura_huff_pct: number | string | null
    complementarios_ponderados: number | string | null; residentes_objetivo_en_radio: number | string | null; empleos_en_radio: number | string | null
    demanda_de_personas: string; negocios_corredor_comercial_en_radio: number | string | null
    edad_clave_etiqueta: string; edad_clave_pct: number | string | null; edad_clave_pct_zmvm: number | string | null; radio_m: number; resumen_texto: string; fuente: string
  }
  giro_no_encontrado?: string
  vecinas?: { valores: Record<string, number>; dominio: [number, number]; etiqueta: string; radio_km: number; fuente: string } | null
}

export interface ResultadoBusqueda {
  colonia: string; municipio: string; cvegeo_mun: string; n_agebs: number; habitantes: number | null
  agebs: { cvegeo: string; habitantes: number | null }[]
}
export interface RespuestaBusqueda { q: string; resultados: ResultadoBusqueda[]; sugerencias: string[]; fuente: string; motivo: string | null }

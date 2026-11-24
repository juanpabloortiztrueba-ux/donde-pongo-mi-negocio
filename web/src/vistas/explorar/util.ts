import { fmtCompacto, fmtNum, fmtPct, fmtPesos } from '../../comun'

// Tipos de las respuestas de app/api/explorar.py y utilidades comunes de Explorar y Comparar.

export interface VarMeta {
  clave: string; etiqueta: string; unidad: string; grupo: string; formato: 'num' | 'pct' | 'pesos' | 'compacto' | 'decil' | 'ordinal'
  descripcion: string; decimales: number; fuente: string; agregacion: string; agregacion_texto: string
  etiquetas_ordinal?: Record<string, string>
}
export interface FilaMunicipio { cvegeo_mun: string; municipio: string; n_agebs: number; n_con_dato: number; poblacion: number; valor: number | null; mediana: number | null }
export interface Extremo { cvegeo: string; colonia: string | null; municipio: string; valor: number | null }
export interface CajaHist { x0: number; x1: number; n: number; etiqueta?: string }
export interface MapaResp {
  variable: VarMeta; municipio: string | null; valores: Record<string, number>; dominio: [number, number]
  cuantiles: { p: number; valor: number | null }[]
  resumen: { n_agebs: number; n_con_dato: number; poblacion: number; valor: number | null; mediana: number | null; minimo: Extremo; maximo: Extremo; ambito: string }
  municipios: FilaMunicipio[]
  histograma: { cajas: CajaHist[]; dominio: [number, number]; valores_en_extremos: number; n: number }
  fuente: string
}
export interface ZonaTop {
  posicion: number; ageb: string; colonia: string | null; municipio: string; score: number; prob_apertura_pct: number | null
  prob_sigue_abierto_pct: number | string | null; competidores_ponderados: number | null; nse_estimado: string | null; residentes_objetivo_en_radio: number | null
}
export interface GiroComparado {
  clave: string; nombre: string; negocios_denue: number; negocios_denue_hist: number; aperturas: number | null; agebs_con_apertura: number | null
  auc: number | null; tasa_base_pct: number | null; prob_apertura_media_pct: number | null; prob_sigue_abierto_media_pct: number | null; viabilidad_media_pct: number | null
  mejor_municipio: { cvegeo_mun: string; municipio: string; score_medio: number; prob_apertura_media_pct: number; n_agebs: number; criterio: string } | null
  ticket_promedio_mxn: number | null; radio_influencia_m: number | null; top: ZonaTop[]; avisos: Record<string, string>
}
export interface CompararResp { giros: GiroComparado[]; notas: Record<string, string>; fuentes: Record<string, string> }
export interface ScoresResp { giro: string; nombre: string; n: number; scores: Record<string, number>; como_leer: string; fuente: string }
export interface DenueResp { giro: string; total: number; mostrados: number; muestreado: boolean; puntos: [number, number, string][]; fuente: string }
export interface Estacion { sistema: string; linea: string | null; estacion: string; lat: number; lon: number; afluencia_anual: number | null; anio_afluencia: number | null; estado: string }
export interface SugerirFila {
  giro: string; nombre: string; viabilidad_pct: number; prob_apertura_pct: number; prob_sigue_abierto_pct: number; score_relativo_medio_top10: number
  ticket_promedio_mxn: number | null; aviso?: string
}
export interface SugerirResp {
  encontrado: boolean; giros?: SugerirFila[]; como_leer?: string; metodo?: string; motivo?: string; filtros?: Record<string, string | number> | null; fuentes?: string[]
}

/** Cómo se escribe un valor de la variable: por AGEB o ya agregado (un municipio o la ZMVM). */
export function formatoDe(m: VarMeta, agregado = false): (v: number) => string {
  switch (m.formato) {
    case 'pct': return (v) => fmtPct(v, 1)
    case 'pesos': return (v) => fmtPesos(v)
    case 'compacto': return (v) => fmtCompacto(v)
    case 'decil': return (v) => fmtNum(v, agregado ? 1 : 0)
    case 'ordinal': return (v) => {
      if (agregado) return fmtNum(v, 1)
      const n = Math.min(5, Math.max(1, Math.round(v)))
      return `${m.etiquetas_ordinal?.[String(n)] ?? n} (${n})`
    }
    default: return (v) => fmtNum(v, m.decimales)
  }
}

/** Descarga un CSV (UTF-8 con BOM para que Excel respete los acentos). Los números van crudos, sin separador de miles. */
export function descargarCsv(nombre: string, filas: (string | number | null | undefined)[][]) {
  const esc = (x: string | number | null | undefined) => (x == null ? '' : typeof x === 'number' ? String(x) : /[",\n\r]/.test(x) ? `"${x.replace(/"/g, '""')}"` : x)
  const blob = new Blob(['﻿' + filas.map((r) => r.map(esc).join(',')).join('\r\n')], { type: 'text/csv;charset=utf-8' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob); a.download = nombre
  document.body.appendChild(a); a.click(); a.remove()
  setTimeout(() => URL.revokeObjectURL(a.href), 1000)
}

export const TONOS_GIRO = ['naranja', 'azul', 'verde', 'gris'] as const

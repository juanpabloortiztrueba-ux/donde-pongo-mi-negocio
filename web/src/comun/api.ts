import { useCallback, useEffect, useRef, useState } from 'react'

// Cliente de la API (/api/*) con tipos. En dev vite reenvía /api al backend; en producción lo sirve app/servidor.py.
export class ErrorApi extends Error {
  constructor(public estado: number, mensaje: string) { super(mensaje); this.name = 'ErrorApi' }
}

/** true si el error es de un pedido cancelado con AbortController (no se muestra al usuario). */
export const esCancelado = (e: unknown) => (e as { name?: string })?.name === 'AbortError'

async function pedir<T>(ruta: string, init?: RequestInit): Promise<T> {
  let r: Response
  try { r = await fetch(ruta, init) } catch (e) {
    if ((e as { name?: string })?.name === 'AbortError') throw e // cancelado a propósito: quien llama lo ignora (`esCancelado`)
    throw new ErrorApi(0, 'No pude hablar con el servidor. ¿Sigue abierto el tablero?')
  }
  if (!r.ok) {
    let detalle = ''
    try { const j = await r.json(); detalle = j.error ?? j.detail ?? '' } catch { /* sin cuerpo */ }
    throw new ErrorApi(r.status, detalle ? String(detalle) : `El servidor respondió ${r.status}.`)
  }
  return (await r.json()) as T
}
/** `init` admite `{ signal }` de un AbortController: cancela el pedido al salir de la vista o al reenviar (el agente tarda ~2 min). */
export const apiGet = <T,>(ruta: string, init?: RequestInit) => pedir<T>(ruta, init)
export const apiPost = <T,>(ruta: string, cuerpo: unknown, init?: RequestInit) =>
  pedir<T>(ruta, { ...init, method: 'POST', headers: { 'Content-Type': 'application/json', ...(init?.headers as Record<string, string> | undefined) }, body: JSON.stringify(cuerpo) })

// Hook GET con caché en memoria (misma ruta = misma respuesta, sin repetir el pedido). ruta=null no pide nada.
const cache = new Map<string, Promise<unknown>>()
export function useApi<T>(ruta: string | null, opciones: { cache?: boolean } = {}) {
  const usarCache = opciones.cache ?? true
  const [est, setEst] = useState<{ datos: T | null; error: ErrorApi | null; cargando: boolean }>({ datos: null, error: null, cargando: !!ruta })
  const vivo = useRef(true)
  const [n, setN] = useState(0)
  useEffect(() => { vivo.current = true; return () => { vivo.current = false } }, [])
  useEffect(() => {
    if (!ruta) { setEst({ datos: null, error: null, cargando: false }); return }
    let activo = true
    setEst((e) => ({ ...e, cargando: true, error: null }))
    let p = usarCache ? (cache.get(ruta) as Promise<T> | undefined) : undefined
    if (!p) { p = apiGet<T>(ruta); if (usarCache) { cache.set(ruta, p); p.catch(() => cache.delete(ruta)) } }
    p.then((d) => activo && setEst({ datos: d, error: null, cargando: false }))
      .catch((e) => activo && setEst({ datos: null, error: e instanceof ErrorApi ? e : new ErrorApi(0, String(e)), cargando: false }))
    return () => { activo = false }
  }, [ruta, n, usarCache])
  const recargar = useCallback(() => { if (ruta) cache.delete(ruta); setN((x) => x + 1) }, [ruta])
  return { ...est, recargar }
}

// ---------------------------------------------------------------- tipos de la API Base
export interface EstadoOllama { prendido: boolean; modelos: string[]; cargados: string[]; faltan: string[] }
export interface Estado {
  ollama: EstadoOllama
  internet: boolean
  cortes: { denue_actual: string | null; denue_hist: string | null; censo: string; enigh: string; conapo: string; macro_consultado: string | null; modelo: string | null }
  kpis: {
    agebs: number | null; municipios: number | null; negocios_denue: number | null; negocios_denue_hist: number | null
    giros: number | null; auc_global: number | null
    evaluacion: { pasan: number | null; total: number | null; aprobado: boolean | null; trampa_pasa: boolean | null; fecha: string | null; latencia_mediana_s: number | null }
  }
  fuentes: Record<string, string>
}
export interface Giro { clave: string; nombre: string; nombres: string[]; ticket_promedio_mxn: number | null; radio_influencia_m: number | null; rubro_enigh: string | null; demanda_base: string }
export interface Municipio { cvegeo_mun: string; nombre: string; cve_ent: string; entidad: string }
export interface GeoFeature { type: 'Feature'; properties: Record<string, string | number | null>; geometry: { type: string; coordinates: unknown } }
export interface GeoColeccion { type: 'FeatureCollection'; features: GeoFeature[] }
export interface DemoInicio {
  giro: string; pregunta: string; metodo: string | null; fuentes: string[]
  zonas: { colonia: string; municipio: string; ageb: string; score: number; prob_apertura_pct: number; lat: number; lon: number }[]
  /** una fila por AGEB: [lon, lat, score 0-100, cvegeo] */
  puntos: [number, number, number, string][]
}

export const useEstadoApi = () => useApi<Estado>('/api/estado', { cache: false })
export const useGiros = () => useApi<{ giros: Giro[]; fuente: string }>('/api/giros')
export const useMunicipios = () => useApi<{ municipios: Municipio[]; fuente: string }>('/api/municipios')

let geoAgebs: Promise<GeoColeccion> | null = null
let geoMuns: Promise<GeoColeccion> | null = null
/** GeoJSON de AGEB (propiedades: cvegeo, colonia, municipio). Se baja una vez por sesión. */
export const cargarGeoAgebs = () => (geoAgebs ??= apiGet<GeoColeccion>('/api/geo/agebs').catch((e) => { geoAgebs = null; throw e }))
export const cargarGeoMunicipios = () => (geoMuns ??= apiGet<GeoColeccion>('/api/geo/municipios').catch((e) => { geoMuns = null; throw e }))

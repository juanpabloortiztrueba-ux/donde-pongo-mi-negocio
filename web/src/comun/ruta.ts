import { useEffect, useState } from 'react'

// Ruteo por hash, sin dependencias: #/inicio · #/preguntar · #/explorar · #/zona/<cvegeo>?giro= · #/comparar · #/macro · #/modelo · #/datos
export type VistaId = 'inicio' | 'preguntar' | 'explorar' | 'zona' | 'comparar' | 'macro' | 'modelo' | 'datos' | 'ejemplo-mapa'

export interface Ruta {
  vista: VistaId
  /** segmento después de la vista: el cvegeo en #/zona/<cvegeo> */
  param?: string
  /** lo que va después de ?, ya decodificado: {giro: 'heladeria'} */
  query: Record<string, string>
}
/** Props que recibe cada vista (default export de web/src/vistas/<grupo>/<Vista>.tsx). */
export interface VistaProps { ruta: Ruta }

export const SECCIONES: { titulo: string | null; vistas: { id: VistaId; titulo: string }[] }[] = [
  { titulo: null, vistas: [{ id: 'inicio', titulo: 'Inicio' }] },
  { titulo: null, vistas: [{ id: 'preguntar', titulo: 'Preguntar' }] },
  { titulo: 'Explorar', vistas: [{ id: 'explorar', titulo: 'Explorar la ZMVM' }, { id: 'zona', titulo: 'Ficha de zona' }, { id: 'comparar', titulo: 'Comparar giros' }] },
  { titulo: 'Contexto', vistas: [{ id: 'macro', titulo: 'Macro' }, { id: 'modelo', titulo: 'El modelo' }, { id: 'datos', titulo: 'Datos y carpetas' }] },
]
export const TITULOS = Object.fromEntries(SECCIONES.flatMap((s) => s.vistas).map((v) => [v.id, v.titulo])) as Record<string, string>
const VALIDAS = new Set<string>([...Object.keys(TITULOS), 'ejemplo-mapa'])

export function parseRuta(hash: string): Ruta {
  const limpio = hash.replace(/^#\/?/, '')
  const [camino, qs = ''] = limpio.split('?')
  const [v, ...resto] = camino.split('/').filter(Boolean)
  const query: Record<string, string> = {}
  new URLSearchParams(qs).forEach((val, k) => { query[k] = val })
  const vista = (VALIDAS.has(v ?? '') ? v : 'inicio') as VistaId
  return { vista, param: resto[0] ? decodeURIComponent(resto[0]) : undefined, query }
}

/** href de una ruta: href('zona', '0900200010010', {giro: 'heladeria'}) → «#/zona/0900200010010?giro=heladeria». */
export function href(vista: VistaId, param?: string, query?: Record<string, string | null | undefined>): string {
  const q = new URLSearchParams()
  Object.entries(query ?? {}).forEach(([k, v]) => { if (v != null && v !== '') q.set(k, v) })
  const s = q.toString()
  return `#/${vista}${param ? '/' + encodeURIComponent(param) : ''}${s ? '?' + s : ''}`
}
/** Navega (cambia el hash). */
export function ir(vista: VistaId, param?: string, query?: Record<string, string | null | undefined>) { window.location.hash = href(vista, param, query) }
/** Cambia solo el query de la ruta actual sin apilar historial (p. ej. al elegir un giro en un filtro). */
export function fijarQuery(cambios: Record<string, string | null | undefined>) {
  const r = parseRuta(window.location.hash)
  const q = { ...r.query, ...cambios }
  window.history.replaceState(null, '', href(r.vista, r.param, q))
  window.dispatchEvent(new HashChangeEvent('hashchange'))
}

export function useRuta(): Ruta {
  const [h, setH] = useState(window.location.hash)
  useEffect(() => {
    const f = () => setH(window.location.hash)
    window.addEventListener('hashchange', f)
    return () => window.removeEventListener('hashchange', f)
  }, [])
  return parseRuta(h)
}

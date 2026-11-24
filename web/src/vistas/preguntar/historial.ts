import type { Turno } from './tipos'

// El historial vive en el navegador (sessionStorage): se pierde al cerrar la pestaña. Todo con try/catch: en modo privado o con el
// almacenamiento lleno, el tablero sigue funcionando sin guardar.
const LLAVE = 'dpmn-preguntar-hilo-v1'
const MAX = 8

export function leerHilo(): Turno[] {
  try {
    const crudo = sessionStorage.getItem(LLAVE)
    if (!crudo) return []
    const v = JSON.parse(crudo)
    return Array.isArray(v) ? (v as Turno[]).filter((t) => t && typeof t.pregunta === 'string' && typeof t.k === 'string') : []
  } catch { return [] }
}

/** Guarda lo ligero: sin el mapa (120 KB por turno) ni los resultados de las herramientas; se vuelven a pedir al servidor. */
export function guardarHilo(turnos: Turno[]) {
  try {
    const ligero = turnos.slice(-MAX).map(({ herramientas: _h, datos, ...t }) => ({ ...t, datos: datos ? { ...datos, mapa: undefined } : undefined }))
    sessionStorage.setItem(LLAVE, JSON.stringify(ligero))
  } catch { /* sin almacenamiento */ }
}

export function borrarHilo() {
  try { sessionStorage.removeItem(LLAVE) } catch { /* sin almacenamiento */ }
}

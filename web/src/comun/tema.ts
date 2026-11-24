import { useSyncExternalStore } from 'react'

// Tema claro/oscuro: sigue al sistema y el botón lo fija. Se guarda en localStorage solo como comodidad.
export type Tema = 'light' | 'dark'
type Pref = 'sistema' | Tema
const LLAVE = 'tablero-tema'
const oyentes = new Set<() => void>()
const mq = typeof window !== 'undefined' ? window.matchMedia('(prefers-color-scheme: dark)') : null

function leer(): Pref {
  try { const v = localStorage.getItem(LLAVE); if (v === 'light' || v === 'dark') return v } catch { /* sin storage */ }
  return 'sistema'
}
let pref: Pref = leer()
const resuelto = (): Tema => (pref === 'sistema' ? (mq?.matches ? 'dark' : 'light') : pref)
let actual: Tema = resuelto()

function aplicar() {
  const t = resuelto()
  document.documentElement.dataset.tema = t
  if (t !== actual) { actual = t; oyentes.forEach((f) => f()) }
}
aplicar()
mq?.addEventListener('change', aplicar)

/** Tema efectivo ('light' | 'dark') y el botón que lo alterna. Úsalo para el `theme` de una escena Stage y para el Mapa. */
export function useTema() {
  const tema = useSyncExternalStore((f) => { oyentes.add(f); return () => oyentes.delete(f) }, () => actual)
  return {
    tema,
    alternar() {
      pref = tema === 'dark' ? 'light' : 'dark'
      try { localStorage.setItem(LLAVE, pref) } catch { /* sin storage */ }
      aplicar()
    },
  }
}

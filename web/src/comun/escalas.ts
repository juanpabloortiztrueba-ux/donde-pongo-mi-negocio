import type { Tema } from './tema'

// Escalas de color legibles en claro y en oscuro.
//  · secuencial: un solo tono (naranja del tablero), de claro a oscuro en el tema claro y de apagado a brillante en el oscuro,
//    así «más» siempre se ve más fuerte sobre el fondo.
//  · categórica: 8 tonos en orden fijo (paleta validada de la skill dataviz); nunca se reciclan: del 9.º en adelante usa «Otros».
const SEC_CLARO = ['#fdf0e4', '#fbd3b2', '#f8ab73', '#ef7a38', '#d4561a', '#a63e0f', '#6f2808']
const SEC_OSCURO = ['#26201c', '#4b2f1f', '#7d4424', '#b45a28', '#e8743a', '#fb9a64', '#ffd0ad']
export const SEC_VACIO = { light: '#ececee', dark: '#232328' }

const CAT_CLARO = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#008300', '#6250d6', '#e34948']
const CAT_OSCURO = ['#3987e5', '#d95926', '#199e70', '#c98500', '#d55181', '#0ca30c', '#9085e9', '#e66767']
export const CAT_OTROS = { light: '#9a9aa3', dark: '#6c6c76' }

const hex = (h: string) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16))
const aHex = (c: number[]) => '#' + c.map((x) => Math.round(x).toString(16).padStart(2, '0')).join('')

/** Rampa secuencial: t en [0,1] → color hex. */
export function secuencial(t: number, tema: Tema): string {
  const r = tema === 'dark' ? SEC_OSCURO : SEC_CLARO
  const x = Math.min(1, Math.max(0, t)) * (r.length - 1)
  const i = Math.min(r.length - 2, Math.floor(x))
  const a = hex(r[i]), b = hex(r[i + 1]), k = x - i
  return aHex(a.map((v, j) => v + (b[j] - v) * k))
}
/** Color de una categoría por su posición (0 = la primera, orden fijo). Más allá de 8 → gris «Otros». */
export function categorica(i: number, tema: Tema): string {
  const r = tema === 'dark' ? CAT_OSCURO : CAT_CLARO
  return i >= 0 && i < r.length ? r[i] : CAT_OTROS[tema]
}
/** CSS linear-gradient de la rampa, para la leyenda. */
export function gradienteSecuencial(tema: Tema): string {
  return `linear-gradient(90deg, ${Array.from({ length: 8 }, (_, i) => secuencial(i / 7, tema)).join(', ')})`
}
/** Color de un valor dentro de un dominio [min, max]. */
export function colorDeValor(v: number | null | undefined, dominio: [number, number], tema: Tema): string {
  if (v == null || !Number.isFinite(v)) return SEC_VACIO[tema === 'dark' ? 'dark' : 'light']
  return secuencial((v - dominio[0]) / (dominio[1] - dominio[0] || 1), tema)
}

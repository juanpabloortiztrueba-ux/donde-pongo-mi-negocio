import type { ReactNode } from 'react'
import { Badge } from '../kit'

/** Píldora (Badge de stageshow). tono: naranja = clave, azul = comparación, verde = ok, amarillo = destacado, gris = neutro. */
export function Pill({ tono = 'gris', children }: { tono?: 'naranja' | 'azul' | 'verde' | 'amarillo' | 'gris' | 'rojo'; children: ReactNode }) {
  const t = { naranja: 'accent', azul: 'accent', verde: 'success', amarillo: 'warning', gris: 'neutral', rojo: 'danger' }[tono] as 'accent' | 'success' | 'warning' | 'neutral' | 'danger'
  return <span className={`c-pill c-pill--${tono}`}><Badge tone={t}>{children}</Badge></span>
}

/** Encabezado de vista: píldora de sección + título-afirmación (<em> pinta en naranja las palabras clave) + descripción corta. */
export function Cabecera({ seccion, sub, titulo, children }: { seccion: string; sub?: string; titulo: ReactNode; children?: ReactNode }) {
  return (
    <header className="mc-cab">
      <div className="kicker"><span>{seccion}</span>{sub && <em>· {sub}</em>}</div>
      <h1 className="titulo">{titulo}</h1>
      {children && <p className="lede">{children}</p>}
    </header>
  )
}

import type { ReactNode } from 'react'

/** Pie con la fuente de una cifra o gráfica: <Fuente>Censo 2020 INEGI</Fuente> → «Fuente: Censo 2020 INEGI». Toda cifra lleva el suyo. */
export function Fuente({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <p className={`c-fuente ${className}`}><b>Fuente:</b> {children}</p>
}

import { Fragment, useEffect, useRef, useState, type ReactNode } from 'react'
import { Count } from '../../kit'

/** Control segmentado plano (botones con una línea fina bajo la opción activa). Accesible por teclado. */
export function Opciones<T extends string>({ valor, opciones, onCambio, etiqueta }: { valor: T; opciones: { id: T; texto: string }[]; onCambio: (v: T) => void; etiqueta: string }) {
  return (
    <div className="ctx-ops" role="tablist" aria-label={etiqueta}>
      {opciones.map((o) => (
        <button key={o.id} role="tab" aria-selected={o.id === valor} data-on={o.id === valor} className="ctx-ops__b" onClick={() => onCambio(o.id)}>{o.texto}</button>
      ))}
    </div>
  )
}

/** Texto con `código`, **negritas** y *cursivas* sencillas (lo que traen los reportes en Markdown). */
export function Inline({ t, abrir }: { t: string; abrir?: (href: string) => boolean }): ReactNode {
  const partes: ReactNode[] = []
  const re = /(`[^`]+`)|(\*\*[^*]+\*\*)|(\[[^\]]+\]\([^)\s]+\))|(\*[^*\s][^*]*\*)|(https?:\/\/[^\s)<>]+)/g
  let i = 0, m: RegExpExecArray | null, k = 0
  while ((m = re.exec(t))) {
    if (m.index > i) partes.push(t.slice(i, m.index))
    const s = m[0]
    if (m[1]) partes.push(<code key={k++}>{s.slice(1, -1)}</code>)
    else if (m[2]) partes.push(<strong key={k++}><Inline t={s.slice(2, -2)} abrir={abrir} /></strong>)
    else if (m[3]) {
      const mm = /^\[([^\]]+)\]\(([^)\s]+)\)$/.exec(s)!
      const h = mm[2]
      if (/^https?:/.test(h)) partes.push(<a key={k++} href={h} target="_blank" rel="noreferrer">{mm[1]}</a>)
      else partes.push(<a key={k++} href={'#'} onClick={(e) => { e.preventDefault(); abrir?.(h) }}>{mm[1]}</a>)
    }
    else if (m[4]) partes.push(<em key={k++}>{s.slice(1, -1)}</em>)
    else partes.push(<a key={k++} href={s} target="_blank" rel="noreferrer">{s}</a>)
    i = m.index + s.length
  }
  if (i < t.length) partes.push(t.slice(i))
  return <Fragment>{partes}</Fragment>
}

/** Sección de una vista: kicker en mayúsculas pequeñas, afirmación opcional y contenido. */
export function Seccion({ id, kicker, titulo, children }: { id?: string; kicker: string; titulo?: ReactNode; children: ReactNode }) {
  return (
    <section className="ctx-sec" id={id} aria-label={kicker}>
      <h2 className="seccion-t">{kicker}</h2>
      {titulo && <h3 className="ctx-sec__t">{titulo}</h3>}
      {children}
    </section>
  )
}

/** true cuando el elemento entra en pantalla (una sola vez): hace que las cifras rueden cuando se ven, no al cargar la página. */
export function useVisible<T extends HTMLElement>(): [React.RefObject<T | null>, boolean] {
  const ref = useRef<T>(null)
  const [v, setV] = useState(false)
  useEffect(() => {
    const el = ref.current
    if (!el || v) return
    if (typeof IntersectionObserver === 'undefined') { setV(true); return }
    const io = new IntersectionObserver((es) => { if (es.some((e) => e.isIntersecting)) { setV(true); io.disconnect() } }, { threshold: 0.2 })
    io.observe(el)
    return () => io.disconnect()
  }, [v])
  return [ref, v]
}

/** Cifra con etiqueta que rueda desde 0 al entrar en pantalla (Count de stageshow). valor=null → NO ENCONTRADO. */
export function CifraRueda({ valor, formato, etiqueta, retraso = 0 }: { valor: number | null | undefined; formato: (n: number) => string; etiqueta: string; retraso?: number }) {
  const [ref, visible] = useVisible<HTMLDivElement>()
  const [v, setV] = useState(0)
  useEffect(() => {
    if (!visible || valor == null) return
    const t = setTimeout(() => setV(valor), 100 + retraso)
    return () => clearTimeout(t)
  }, [visible, valor, retraso])
  return (
    <div ref={ref} className="ctx-cifra">
      <div className="ctx-cifra__v">{valor == null ? <span className="ctx-cifra__nd">NO ENCONTRADO</span> : <Count value={v} format={formato} duration={900} stagger={45} />}</div>
      <div className="ctx-cifra__e">{etiqueta}</div>
    </div>
  )
}

import type { ReactNode } from 'react'

// Markdown mínimo para la respuesta del agente: títulos, párrafos, listas, citas, **negritas**, _cursivas_ y `código`.
// Sin dependencias (el tablero va empaquetado y sin internet). No interpreta HTML: todo lo que no reconoce sale como texto.

const INLINE = /(\*\*[^*]+\*\*|`[^`]+`|\*[^*\s][^*]*\*|\b_[^_\s][^_]*_\b)/g

export function enLinea(texto: string): ReactNode[] {
  const out: ReactNode[] = []
  let i = 0, k = 0
  for (const m of texto.matchAll(INLINE)) {
    const idx = m.index ?? 0
    if (idx > i) out.push(texto.slice(i, idx))
    const t = m[0]
    if (t.startsWith('**')) out.push(<strong key={k++}>{enLinea(t.slice(2, -2))}</strong>)
    else if (t.startsWith('`')) out.push(<code key={k++}>{t.slice(1, -1)}</code>)
    else out.push(<em key={k++}>{enLinea(t.slice(1, -1))}</em>)
    i = idx + t.length
  }
  if (i < texto.length) out.push(texto.slice(i))
  return out
}

type Bloque =
  | { t: 'p'; lineas: string[] }
  | { t: 'h'; n: number; texto: string }
  | { t: 'ul'; items: string[] }
  | { t: 'ol'; items: string[] }
  | { t: 'q'; lineas: string[] }

export function bloques(md: string): Bloque[] {
  const out: Bloque[] = []
  const lineas = md.replace(/\r/g, '').split('\n')
  let p: string[] = []
  const cierra = () => { if (p.length) { out.push({ t: 'p', lineas: p }); p = [] } }
  for (const ln of lineas) {
    const l = ln.trimEnd()
    let m: RegExpMatchArray | null
    if (!l.trim()) { cierra(); continue }
    if ((m = l.match(/^(#{1,4})\s+(.*)$/))) { cierra(); out.push({ t: 'h', n: m[1].length, texto: m[2] }); continue }
    if ((m = l.match(/^>\s?(.*)$/))) {
      cierra()
      const ult = out[out.length - 1]
      if (ult?.t === 'q') ult.lineas.push(m[1]); else out.push({ t: 'q', lineas: [m[1]] })
      continue
    }
    if ((m = l.match(/^\s*(\d+)[.)]\s+(.*)$/))) {
      cierra()
      const ult = out[out.length - 1]
      if (ult?.t === 'ol') ult.items.push(m[2]); else out.push({ t: 'ol', items: [m[2]] })
      continue
    }
    if ((m = l.match(/^\s*[-*•]\s+(.*)$/))) {
      cierra()
      const ult = out[out.length - 1]
      if (ult?.t === 'ul') ult.items.push(m[1]); else out.push({ t: 'ul', items: [m[1]] })
      continue
    }
    p.push(l)
  }
  cierra()
  return out
}

/** Quita el párrafo «**Fuentes:** …» del final (la vista lo muestra aparte, como lista). */
export function sinFuentes(md: string): string {
  return md.replace(/\n+[*#_ ]*Fuentes?[*#_ ]*:?[\s\S]*$/i, '').trimEnd()
}

export function Markdown({ texto }: { texto: string }) {
  return (
    <div className="pre-md">
      {bloques(texto).map((b, i) => {
        if (b.t === 'h') return <p key={i} className="pre-md__h">{enLinea(b.texto)}</p>
        if (b.t === 'ul') return <ul key={i}>{b.items.map((x, j) => <li key={j}>{enLinea(x)}</li>)}</ul>
        if (b.t === 'ol') return <ol key={i}>{b.items.map((x, j) => <li key={j}>{enLinea(x)}</li>)}</ol>
        if (b.t === 'q') return <blockquote key={i}>{b.lineas.map((x, j) => <p key={j}>{enLinea(x)}</p>)}</blockquote>
        return <p key={i}>{b.lineas.map((x, j) => <span key={j}>{j > 0 && <br />}{enLinea(x)}</span>)}</p>
      })}
    </div>
  )
}

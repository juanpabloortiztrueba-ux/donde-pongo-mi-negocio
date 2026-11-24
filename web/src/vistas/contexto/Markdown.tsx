import { Fragment, useMemo, type ReactNode } from 'react'
import { Inline } from './ui'

// Visor de Markdown sin dependencias (los documentos de carpetas/ son Markdown plano): títulos, párrafos, listas, tablas,
// citas, bloques de código y líneas. Todo se pinta con elementos de React (nada de HTML crudo).

type Bloque =
  | { t: 'h'; n: number; x: string }
  | { t: 'p'; x: string }
  | { t: 'cod'; x: string }
  | { t: 'cita'; x: string }
  | { t: 'hr' }
  | { t: 'lista'; items: { nivel: number; orden: boolean; x: string }[] }
  | { t: 'tabla'; cab: string[]; filas: string[][] }

const celdas = (ln: string) => ln.trim().replace(/^\|/, '').replace(/\|$/, '').split(/(?<!\\)\|/).map((c) => c.trim().replace(/\\\|/g, '|'))

export function parsear(md: string): Bloque[] {
  const L = md.replace(/\r/g, '').split('\n')
  const out: Bloque[] = []
  let i = 0
  while (i < L.length) {
    const ln = L[i]
    if (!ln.trim()) { i++; continue }
    if (/^```/.test(ln.trim())) {
      const c: string[] = []
      i++
      while (i < L.length && !/^```/.test(L[i].trim())) c.push(L[i++])
      i++
      out.push({ t: 'cod', x: c.join('\n') })
      continue
    }
    const h = /^(#{1,6})\s+(.*?)\s*#*\s*$/.exec(ln)
    if (h) { out.push({ t: 'h', n: h[1].length, x: h[2] }); i++; continue }
    if (/^\s*([-*_])(\s*\1){2,}\s*$/.test(ln)) { out.push({ t: 'hr' }); i++; continue }
    if (/^\s*\|/.test(ln) && i + 1 < L.length && /^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$/.test(L[i + 1])) {
      const cab = celdas(ln)
      i += 2
      const filas: string[][] = []
      while (i < L.length && /^\s*\|/.test(L[i])) filas.push(celdas(L[i++]))
      out.push({ t: 'tabla', cab, filas })
      continue
    }
    if (/^\s*>/.test(ln)) {
      const c: string[] = []
      while (i < L.length && /^\s*>/.test(L[i])) c.push(L[i++].replace(/^\s*>\s?/, ''))
      out.push({ t: 'cita', x: c.join(' ') })
      continue
    }
    if (/^\s*([-*+]|\d+\.)\s+/.test(ln)) {
      const items: { nivel: number; orden: boolean; x: string }[] = []
      while (i < L.length) {
        const m = /^(\s*)([-*+]|\d+\.)\s+(.*)$/.exec(L[i])
        if (m) { items.push({ nivel: Math.min(3, Math.floor(m[1].replace(/\t/g, '  ').length / 2)), orden: /\d/.test(m[2]), x: m[3] }); i++ }
        else if (items.length && L[i].trim() && /^\s{2,}\S/.test(L[i])) { items[items.length - 1].x += ' ' + L[i].trim(); i++ }
        else break
      }
      out.push({ t: 'lista', items })
      continue
    }
    const p: string[] = [ln.trim()]
    i++
    while (i < L.length && L[i].trim() && !/^(#{1,6}\s|```|\s*>|\s*([-*+]|\d+\.)\s+|\s*\|)/.test(L[i])) p.push(L[i++].trim())
    out.push({ t: 'p', x: p.join(' ') })
  }
  return out
}

/** Resuelve un enlace relativo («../01_metodologia/denue.md#x») respecto de la carpeta del documento abierto. */
export function resolverRuta(actual: string, href: string): string | null {
  const limpio = href.split('#')[0]
  if (!limpio || /^[a-z]+:/i.test(limpio)) return null
  const partes = actual.split('/').slice(0, -1)
  for (const s of limpio.split('/')) {
    if (s === '..') partes.pop()
    else if (s && s !== '.') partes.push(s)
  }
  return partes.join('/')
}

export function Markdown({ md, ruta, abrir }: { md: string; ruta: string; abrir: (ruta: string) => void }) {
  const bloques = useMemo(() => parsear(md), [md])
  const enlace = (h: string) => { const r = resolverRuta(ruta, h); if (r) abrir(r); return !!r }
  const en = (x: string): ReactNode => <Inline t={x} abrir={enlace} />
  return (
    <div className="ctx-md">
      {bloques.map((b, k): ReactNode => {
        switch (b.t) {
          case 'h': { const H = (`h${Math.min(6, b.n + 1)}`) as 'h2'; return <H key={k} data-n={b.n}>{en(b.x)}</H> }
          case 'p': return <p key={k}>{en(b.x)}</p>
          case 'cod': return <pre key={k}><code>{b.x}</code></pre>
          case 'cita': return <blockquote key={k}>{en(b.x)}</blockquote>
          case 'hr': return <hr key={k} />
          case 'tabla': return (
            <div className="ctx-md__tabla" key={k}>
              <table><thead><tr>{b.cab.map((c, j) => <th key={j}>{en(c)}</th>)}</tr></thead>
                <tbody>{b.filas.map((f, r) => <tr key={r}>{b.cab.map((_, j) => <td key={j}>{en(f[j] ?? '')}</td>)}</tr>)}</tbody></table>
            </div>
          )
          case 'lista': {
            const Lista = b.items[0]?.orden ? 'ol' : 'ul'
            return <Lista key={k} className="ctx-md__lista">{b.items.map((it, j) => <li key={j} style={{ marginLeft: it.nivel * 18 }}>{en(it.x)}</li>)}</Lista>
          }
          default: return <Fragment key={k} />
        }
      })}
    </div>
  )
}

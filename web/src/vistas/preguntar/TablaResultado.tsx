import { useState, type ReactNode } from 'react'
import { ChevronRight } from 'lucide-react'
import { Collapse } from '../../kit'
import { fmtNum } from '../../comun'
import type { Herramienta } from './tipos'

// «¿Cómo llegó a esto?»: cada herramienta que usó el agente, con sus argumentos y su resultado en tabla.

const NOMBRES: Record<string, string> = {
  perfil_giro: 'Perfil del giro', recomendar_zonas: 'Recomendar zonas', ficha_zona: 'Ficha de zona', buscar_carpetas: 'Buscar en las carpetas',
  contexto_macro: 'Contexto macro', sugerir_giros: 'Sugerir giros', ficha_municipio: 'Ficha del municipio',
}

const esObjeto = (v: unknown): v is Record<string, unknown> => !!v && typeof v === 'object' && !Array.isArray(v)

function valor(v: unknown): ReactNode {
  if (v == null) return <span className="pre-tab__nulo">—</span>
  if (typeof v === 'number') return Number.isInteger(v) ? fmtNum(v) : fmtNum(v, Math.abs(v) < 10 ? 2 : 1)
  if (typeof v === 'boolean') return v ? 'sí' : 'no'
  if (typeof v === 'string') return v
  return JSON.stringify(v)
}

function Tabla({ datos, nivel = 0 }: { datos: Record<string, unknown>; nivel?: number }) {
  const filas = Object.entries(datos)
  return (
    <table className="pre-tab" data-nivel={nivel}>
      <tbody>
        {filas.map(([k, v]) => (
          <tr key={k}>
            <th scope="row">{k.replace(/_/g, ' ')}</th>
            <td>{Celda(v, nivel)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

function Celda(v: unknown, nivel: number): ReactNode {
  if (Array.isArray(v)) {
    if (!v.length) return <span className="pre-tab__nulo">(vacío)</span>
    if (v.every((x) => esObjeto(x)) && nivel < 2) {
      const cols = [...new Set(v.flatMap((x) => Object.keys(x as object)))].filter((c) => v.every((x) => { const y = (x as Record<string, unknown>)[c]; return y == null || typeof y !== 'object' })).slice(0, 8)
      if (cols.length) {
        return (
          <div className="pre-tab__scroll">
            <table className="pre-tab pre-tab--lista">
              <thead><tr>{cols.map((c) => <th key={c} scope="col">{c.replace(/_/g, ' ')}</th>)}</tr></thead>
              <tbody>{v.slice(0, 12).map((x, i) => <tr key={i}>{cols.map((c) => <td key={c}>{valor((x as Record<string, unknown>)[c])}</td>)}</tr>)}</tbody>
            </table>
          </div>
        )
      }
    }
    if (v.every((x) => x == null || typeof x !== 'object')) return <ul className="pre-tab__lista">{v.map((x, i) => <li key={i}>{valor(x)}</li>)}</ul>
    return <span className="pre-tab__json">{JSON.stringify(v).slice(0, 400)}</span>
  }
  if (esObjeto(v)) return nivel < 2 ? <Tabla datos={v} nivel={nivel + 1} /> : <span className="pre-tab__json">{JSON.stringify(v).slice(0, 400)}</span>
  return valor(v)
}

function argsTexto(args: Record<string, unknown>): string {
  const e = Object.entries(args ?? {}).filter(([, v]) => v != null && v !== '')
  return e.length ? e.map(([k, v]) => `${k}=${typeof v === 'string' ? `«${v}»` : JSON.stringify(v)}`).join(', ') : 'sin argumentos'
}

function Una({ h, i }: { h: Herramienta; i: number }) {
  const [abierta, setAbierta] = useState(false)
  const r = h.resultado
  return (
    <li className="pre-herr">
      <button className="pre-herr__cab" onClick={() => setAbierta((a) => !a)} aria-expanded={abierta}>
        <ChevronRight size={16} className="pre-herr__flecha" data-abierta={abierta} />
        <span className="pre-herr__n">{i + 1}</span>
        <span className="pre-herr__nombre"><b>{NOMBRES[h.nombre] ?? h.nombre}</b><code>{h.nombre}({argsTexto(h.args)})</code></span>
      </button>
      <Collapse open={abierta}>
        <div className="pre-herr__cuerpo">
          {esObjeto(r) ? <Tabla datos={r} /> : <p className="chico">{valor(r)}</p>}
        </div>
      </Collapse>
    </li>
  )
}

export function Herramientas({ lista }: { lista: Herramienta[] }) {
  if (!lista.length) return <p className="chico">Esta pregunta no llamó herramientas.</p>
  return <ol className="pre-herrs">{lista.map((h, i) => <Una key={i} h={h} i={i} />)}</ol>
}

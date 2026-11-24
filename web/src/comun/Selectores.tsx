import { useMemo } from 'react'
import { useGiros, useMunicipios } from './api'

// Selectores compartidos (<select> nativo, en modo plano: borde fino, fondo transparente). Leen el catálogo de la API.

/** Selector de giro (los 40 de config/giros.yaml). `valor` es la clave («heladeria»); `onCambio` recibe la clave o null si eliges «Todos». */
export function SelectorGiro({ valor, onCambio, etiqueta = 'Giro', vacio, className = '' }: {
  valor: string | null; onCambio: (clave: string | null) => void; etiqueta?: string; vacio?: string; className?: string
}) {
  const { datos } = useGiros()
  return (
    <label className={`c-campo ${className}`}>
      <span className="c-campo__t">{etiqueta}</span>
      <select className="c-select" value={valor ?? ''} onChange={(e) => onCambio(e.target.value || null)} disabled={!datos}>
        {vacio !== undefined && <option value="">{vacio}</option>}
        {!datos && <option value="">Cargando…</option>}
        {datos?.giros.map((g) => <option key={g.clave} value={g.clave}>{g.nombre}</option>)}
      </select>
    </label>
  )
}

/** Selector de municipio (los 76 de la ZMVM, agrupados por entidad). `valor` es el cvegeo_mun de 5 dígitos; «Toda la ZMVM» = null. */
export function SelectorMunicipio({ valor, onCambio, etiqueta = 'Municipio', vacio = 'Toda la ZMVM', className = '' }: {
  valor: string | null; onCambio: (cvegeo_mun: string | null) => void; etiqueta?: string; vacio?: string | false; className?: string
}) {
  const { datos } = useMunicipios()
  const grupos = useMemo(() => {
    const por = new Map<string, { cvegeo_mun: string; nombre: string }[]>()
    for (const m of datos?.municipios ?? []) { if (!por.has(m.entidad)) por.set(m.entidad, []); por.get(m.entidad)!.push(m) }
    return [...por.entries()]
  }, [datos])
  return (
    <label className={`c-campo ${className}`}>
      <span className="c-campo__t">{etiqueta}</span>
      <select className="c-select" value={valor ?? ''} onChange={(e) => onCambio(e.target.value || null)} disabled={!datos}>
        {vacio !== false && <option value="">{vacio}</option>}
        {!datos && <option value="">Cargando…</option>}
        {grupos.map(([entidad, ms]) => (
          <optgroup key={entidad} label={entidad}>{ms.map((m) => <option key={m.cvegeo_mun} value={m.cvegeo_mun}>{m.nombre}</option>)}</optgroup>
        ))}
      </select>
    </label>
  )
}

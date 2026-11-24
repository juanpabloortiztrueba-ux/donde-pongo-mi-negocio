import { useMemo, useState } from 'react'
import { useApi, useGiros, type DemoInicio } from './api'
import { Cabecera } from './ss'
import { Mapa } from './Mapa'
import { Fuente } from './Fuente'
import { Cargando } from './Cargando'
import { ErrorApi } from './ErrorApi'
import { GraficaBarras, GraficaLineas } from './Grafica'
import { SelectorMunicipio } from './Selectores'
import { fmtNum, fmtPesos, titulo } from './formato'
import type { VistaProps } from './ruta'

/** #/ejemplo-mapa — la ruta de prueba de los componentes Mapa, SelectorMunicipio y Gráfica* con datos reales (score de heladería). No sale en el menú. */
export default function EjemploMapa(_: VistaProps) {
  const { datos, error, cargando, recargar } = useApi<DemoInicio>('/api/inicio/demo')
  const { datos: giros } = useGiros()
  const [municipio, setMunicipio] = useState<string | null>(null)
  const [elegida, setElegida] = useState<string | null>(null)
  const valores = useMemo(() => Object.fromEntries((datos?.puntos ?? []).map((p) => [p[3], p[2]])), [datos])
  const nombreGiro = giros?.giros.find((g) => g.clave === datos?.giro)?.nombre ?? datos?.giro ?? ''
  // histograma del score: cuántas AGEB caen en cada intervalo de 10 puntos
  const histograma = useMemo(() => {
    const c = Array.from({ length: 10 }, () => 0)
    for (const p of datos?.puntos ?? []) c[Math.min(9, Math.floor(p[2] / 10))]++
    return c.map((n, i) => ({ x: i * 10 + 5, y: n }))
  }, [datos])
  const tickets = useMemo(() => (giros?.giros ?? []).filter((g) => g.ticket_promedio_mxn != null).sort((a, b) => b.ticket_promedio_mxn! - a.ticket_promedio_mxn!).slice(0, 8)
    .map((g) => ({ etiqueta: g.nombre, valor: g.ticket_promedio_mxn! })), [giros])
  return (
    <div className="mc-cuerpo">
      <Cabecera seccion="Componentes" sub="Mapa y gráficas" titulo={<>El mapa del <em>score</em> por AGEB</>}>Ejemplo de los componentes de web/src/comun: Mapa (color por valor, hover, clic, números en el top 5, filtro por municipio) y las gráficas con ejes.</Cabecera>
      <div style={{ margin: '22px 0 12px', display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'center' }}>
        <SelectorMunicipio valor={municipio} onCambio={setMunicipio} />
        {elegida && <span className="chico">AGEB elegida: {elegida}</span>}
      </div>
      <ErrorApi error={error} reintentar={recargar} />
      {cargando ? <Cargando forma="mapa" alto={560} /> : datos && (
        <>
          <Mapa valores={valores} etiqueta={`Score de ${nombreGiro.toLowerCase()} (0–100)`} formatoValor={fmtNum} resaltar={datos.zonas.map((z) => z.ageb)}
            municipio={municipio} onClic={(cv) => setElegida(cv)} seleccion={elegida} />
          <Fuente>modelo propio (score por giro, DENUE, Censo 2020 INEGI). Top 5: {datos.zonas.map((z) => titulo(z.colonia)).join(', ')}.</Fuente>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 40, marginTop: 40 }}>
            <GraficaLineas titulo={`AGEB por intervalo de score de ${nombreGiro.toLowerCase()}`} series={[{ nombre: 'AGEB', puntos: histograma, tono: 'naranja' }]}
              etiquetaX="Score (0–100)" etiquetaY="AGEB" formatoY={(v) => fmtNum(v)} formatoX={(x) => `${Number(x) - 5}–${Number(x) + 5}`} fuente="modelo propio (score de heladería por AGEB); Censo 2020 INEGI, DENUE." />
            <GraficaBarras titulo="Ticket promedio de los 8 giros más caros" filas={tickets} formato={(v) => fmtPesos(v)} fuente="config/giros.yaml (supuestos del proyecto)." />
          </div>
        </>
      )}
    </div>
  )
}

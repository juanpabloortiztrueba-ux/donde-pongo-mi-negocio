import { Cargando, Cabecera, ErrorApi, fmtNum, fmtPct, Fuente, href, Kpi, useApi, useEstado, type DemoInicio, type VistaProps, type VistaId } from '../../comun'
import { ArrowUpRight } from 'lucide-react'
import { Escena } from './Escena'
import './inicio.css'

const TARJETAS: { id: VistaId; t: string; d: string }[] = [
  { id: 'preguntar', t: 'Preguntar', d: 'Escribe tu negocio y el agente local responde con colonias, cifras y fuentes.' },
  { id: 'explorar', t: 'Explorar la ZMVM', d: 'El mapa del score por AGEB, con filtros por giro, municipio y nivel socioeconómico.' },
  { id: 'zona', t: 'Ficha de zona', d: 'Todo lo que sabe el modelo de una colonia: gente, gasto, competencia y riesgos.' },
  { id: 'comparar', t: 'Comparar giros', d: 'Qué giros le quedan mejor a una zona, con probabilidades absolutas.' },
  { id: 'macro', t: 'Macro', d: 'Tasas, inflación, tipo de cambio y consumo: el entorno donde abre tu negocio.' },
  { id: 'modelo', t: 'El modelo', d: 'Cómo se arma el score, cómo se validó y dónde falla.' },
  { id: 'datos', t: 'Datos y carpetas', d: 'De dónde sale cada dato y los documentos que lee el agente.' },
]

export default function Inicio(_: VistaProps) {
  const { estado, error } = useEstado()
  const demo = useApi<DemoInicio>('/api/inicio/demo')
  const k = estado?.kpis
  const c = estado?.cortes
  const ev = k?.evaluacion
  return (
    <div className="mc-cuerpo ini">
      <Cabecera seccion="Inicio" sub="Herramientas Computacionales · UP" titulo={<>Dile qué negocio quieres abrir y te decimos <em>en qué colonias</em></>}>
        Un modelo local, sin mandar tus preguntas a ninguna nube, que ordena las colonias de la Zona Metropolitana del Valle de México para cada giro.
      </Cabecera>

      <section className="ini-escena-caja" aria-label="Demostración">
        {demo.error ? <ErrorApi error={demo.error} reintentar={demo.recargar} titulo="No pude armar la demostración" />
          : demo.datos ? <Escena datos={demo.datos} /> : <Cargando forma="mapa" alto={420} />}
        <Fuente>modelo propio (score de heladería, top 5 de recomendar_zonas); Censo 2020 INEGI, DENUE corte {c?.denue_actual ?? '…'}, ENIGH {c?.enigh ?? '…'}.</Fuente>
      </section>

      <section className="ini-pasos" aria-label="Cómo funciona">
        <div><span className="ini-pasos__n">1</span><h2>Describes tu negocio</h2><p>Escribes «una heladería» o «algo barato para zona de nivel bajo». El agente local entiende el giro y la zona.</p></div>
        <div><span className="ini-pasos__n">2</span><h2>El modelo puntúa cada colonia</h2><p>Cada una de las {k?.agebs != null ? fmtNum(k.agebs) : '…'} AGEB recibe un score de 0 a 100 para ese giro: aperturas esperadas, demanda, flujo y competencia.</p></div>
        <div><span className="ini-pasos__n">3</span><h2>Ves el porqué, con fuente</h2><p>El top 5 trae sus cifras del Censo, el DENUE y la ENIGH. Lo que no está en los datos se dice «NO ENCONTRADO».</p></div>
      </section>

      <section aria-label="Lo que hay adentro">
        <h2 className="seccion-t">Lo que hay adentro</h2>
        {error && !estado ? <ErrorApi error={error} titulo="No pude leer el estado del tablero" /> : (
          <div className="ini-kpis">
            <Kpi valor={k?.agebs} etiqueta="AGEB urbanas puntuadas" fuente="Censo 2020 INEGI" />
            <Kpi valor={k?.municipios} etiqueta="municipios y alcaldías" fuente="SEDATU-CONAPO-INEGI, ZM 2015" retraso={80} />
            <Kpi valor={k?.negocios_denue} etiqueta="negocios en el DENUE" fuente={`DENUE corte ${c?.denue_actual ?? '—'}`} retraso={160} tono="accent" />
            <Kpi valor={k?.giros} etiqueta="giros modelados" fuente="config/giros.yaml (supuestos del proyecto)" retraso={240} />
            <Kpi valor={k?.auc_medio_giro} formato={(n) => fmtNum(n, 3)} etiqueta={`AUC medio dentro de cada giro${k?.auc_medio_giro_n != null ? ` (${fmtNum(k.auc_medio_giro_n)} giros)` : ''}`} fuente="modelo propio (models/metricas_giro.csv), validación por municipio" retraso={320} />
            <Kpi valor={ev?.pasan} formato={(n) => `${fmtNum(n)}/${fmtNum(ev?.total)}`} etiqueta="preguntas que pasa la evaluación" fuente={`modelo propio, evaluación del ${ev?.fecha?.slice(0, 10) ?? '—'}`} retraso={400} />
          </div>
        )}
        {k?.auc_medio_giro != null && (
          <p className="chico ini-nota">
            El AUC mide qué tan bien el modelo de aperturas pone por encima una zona donde sí abrió un negocio del giro frente a una donde no ({fmtPct(k.auc_medio_giro, 1, true)} de probabilidad de ordenar bien un par, en promedio por giro), siempre en municipios que no vio al entrenar.
            {k.auc_global != null && <> El AUC global, {fmtNum(k.auc_global, 3)}, es más alto porque mezcla giros y parte se explica por cuántos negocios de cada giro hay; por eso la cifra de arriba es la que importa.</>}{' '}
            <a href={href('modelo')}>El score que ordena las colonias no es este modelo</a>: el modelo es solo uno de sus términos, junto con demanda, población, flujo y complementarios.
          </p>
        )}
      </section>

      <section aria-label="Vistas del tablero">
        <h2 className="seccion-t">A dónde ir</h2>
        <div className="ini-tarjetas">
          {TARJETAS.map((t) => (
            <a key={t.id} className="ini-tarjeta" href={href(t.id)}>
              <span className="ini-tarjeta__t">{t.t}<ArrowUpRight size={18} /></span>
              <span className="ini-tarjeta__d">{t.d}</span>
            </a>
          ))}
        </div>
      </section>

      <section className="ini-red" aria-label="Usarlo desde otra computadora">
        <h2 className="seccion-t">Usarlo desde otra computadora</h2>
        <div className="ini-red__opciones">
          <div><h3>En la misma red Wi-Fi</h3><p>Arranca con <code>--red</code> y abre en la otra computadora la dirección que imprime la terminal. Cualquiera en esa red puede abrirlo.</p><code className="ini-cmd">uv run python -m app.servidor --red</code></div>
          <div><h3>Clonando el repositorio</h3><p>Solo necesita <b>uv</b>. Doble clic en <code>iniciar.command</code> (Mac) o <code>iniciar.bat</code> (Windows). Ollama es opcional: sin él, todo funciona menos el chat.</p></div>
          <div><h3>Por internet</h3><p>Se puede con un túnel (Cloudflare Tunnel o similar), pero no viene configurado: habría que montarlo aparte.</p></div>
        </div>
      </section>
    </div>
  )
}

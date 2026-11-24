import { useMemo, useState } from 'react'
import { Cabecera, Cargando, ErrorApi, fmtNum, fmtPct, Fuente, GraficaBarras, Kpi, Pill, SelectorGiro, useApi, type VistaProps } from '../../comun'
import { EscenaScore } from './EscenaScore'
import { PuntosAuc, BASES, type Base } from './PuntosAuc'
import { CifraRueda, Inline, Opciones, Seccion } from './ui'
import type { Cifra, EjemploScore, ModeloResp } from './util'
import './contexto.css'

// Vista «El modelo»: cómo se calcula el score (pesos leídos en vivo de app/motor.py), validación espacial, AUC por giro contra líneas base,
// importancia de variables, evaluación del agente, límites honestos y preguntas que puede hacer el profe. Todo sale de /api/modelo.

const ND = 'NO ENCONTRADO'
const NOMBRE_BASE: Record<string, string> = { captura_huff: 'captura Huff', actividad: 'actividad', comp_ageb: 'competencia en la AGEB', comp_huff: 'competencia Huff', densidad: 'densidad' }
const formatoCifra = (c: Cifra) => (n: number) => (c.formato === 'pct' ? fmtPct(n, 1, true) : c.formato === 'auc' ? fmtNum(n, 3) : fmtNum(n, 0))
const ir = (id: string) => document.getElementById(id)?.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' })

const SECCIONES = [
  { id: 'm-score', t: 'Cómo se arma el score' }, { id: 'm-validacion', t: 'Validación' }, { id: 'm-giros', t: 'AUC por giro' },
  { id: 'm-variables', t: 'Variables' }, { id: 'm-agente', t: 'Agente' }, { id: 'm-limites', t: 'Límites' }, { id: 'm-profe', t: 'Preguntas del profe' },
]

function Ejemplo() {
  const [giro, setGiro] = useState<string | null>('heladeria')
  const { datos, error, recargar } = useApi<EjemploScore>(giro ? `/api/modelo/ejemplo?giro=${encodeURIComponent(giro)}&posicion=1` : null)
  return (
    <div className="ctx-ejemplo">
      <div className="ctx-ejemplo__sel">
        <SelectorGiro valor={giro} onCambio={(g) => g && setGiro(g)} etiqueta="Giro del ejemplo" />
        <span className="chico">Se arma la AGEB que queda primera en ese giro.</span>
      </div>
      {error ? <ErrorApi error={error} reintentar={recargar} titulo="No pude armar el ejemplo" />
        : datos ? <EscenaScore key={datos.giro} e={datos} /> : <Cargando forma="mapa" alto={480} />}
      {datos && <Fuente>{datos.fuente}. Cada aporte es peso × percentil × 100; los cinco suman el score ({fmtNum(datos.score, 1)}).{datos.sin_demanda_enigh ? ' Este giro no tiene rubro de gasto ENIGH: el peso del gasto pasa a la población objetivo.' : ''}</Fuente>}
    </div>
  )
}

export default function Modelo(_: VistaProps) {
  const { datos: d, error, cargando, recargar } = useApi<ModeloResp>('/api/modelo')
  const [base, setBase] = useState<Base>('comp_ageb')
  const [activo, setActivo] = useState<string | null>(null)
  const [abierta, setAbierta] = useState<number | null>(0)

  const ev = d?.evaluacion && 'filas' in d.evaluacion ? d.evaluacion : null
  const vs = d?.validacion_score && 'filas' in d.validacion_score ? d.validacion_score : null
  const infoBase = BASES.find((b) => b.id === base)!
  const giro = d?.giros.find((g) => g.giro === activo) ?? null
  const lb = d?.lineas_base
  const sinDato = d?.giros.filter((g) => g.poco_dato) ?? []
  const pliegues = useMemo(() => (d?.validacion.pliegues ?? []).map((p) => ({ etiqueta: `Pliegue ${p.pliegue + 1} · ${fmtNum(p.municipios)} municipios`, valor: p.auc, tono: 'azul' as const })), [d])
  const rangoPesos = (k: string) => {
    const xs = (d?.score.por_pliegue ?? []).map((p) => p[k]).filter((v) => v != null)
    return xs.length ? `${fmtNum(Math.min(...xs), 2)} a ${fmtNum(Math.max(...xs), 2)}` : ND
  }
  const aucPliegues = (d?.validacion.pliegues ?? []).map((p) => p.auc)

  if (error && !d) return <div className="mc-cuerpo"><Cabecera seccion="El modelo" titulo={<>El modelo</>} /><ErrorApi error={error} reintentar={recargar} titulo="No pude leer los resultados del modelo" /></div>

  return (
    <div className="mc-cuerpo ctx">
      <Cabecera seccion="El modelo" sub="Cómo se calcula y qué tanto creerle" titulo={<>Cómo se calcula el score y <em>dónde falla</em></>}>
        Cinco términos con pesos que aprendió el propio modelo, validados dejando municipios enteros fuera, y los límites dichos de frente.
      </Cabecera>

      {cargando && !d ? <Cargando forma="kpis" filas={4} /> : d && (
        <div className="ctx-kpis ctx-kpis--4">
          <Kpi valor={d.validacion.auc_global} formato={(n) => fmtNum(n, 3)} etiqueta="AUC global del modelo de aperturas" tono="accent" fuente="modelo propio, validación por municipio (DENUE 11/2020 y 05/2026)" />
          <Kpi valor={lb?.supera.densidad} formato={(n) => `${fmtNum(n)} de ${fmtNum(lb?.giros)}`} etiqueta="giros donde el modelo le gana a la densidad" retraso={80} fuente="modelo propio, models/metricas_giro.csv" />
          <Kpi valor={d.modelo.n_variables} etiqueta="variables por AGEB y giro" retraso={160} fuente={`modelo propio (${d.modelo.nombre})`} />
          <Kpi valor={ev?.pasan} formato={(n) => `${fmtNum(n)}/${fmtNum(ev?.preguntas)}`} etiqueta="preguntas que pasa el agente" retraso={240} fuente={`modelo propio, evaluación del ${ev?.fecha?.slice(0, 10) ?? ND}`} />
        </div>
      )}
      <nav className="ctx-indice" aria-label="Secciones de la vista">
        {SECCIONES.map((s) => <button key={s.id} className="ctx-indice__b" onClick={() => ir(s.id)}>{s.t}</button>)}
      </nav>

      <Seccion id="m-score" kicker="Cómo se arma el score" titulo={<>El score suma <em>cinco percentiles</em> con pesos aprendidos</>}>
        <p className="ctx-par">Cada AGEB recibe, para cada giro, el percentil (0 a 1) que ocupa entre las 5,875 de la ZMVM en cinco términos. El score es la suma de esos percentiles por su peso, escalada de 0 a 100:{' '}
          {d ? <code className="ctx-formula">score = 100 × ({d.score.terminos.map((t) => `${fmtNum(t.peso_norm, 2)}·${t.clave}`).join(' + ')})</code> : null}</p>
        <Ejemplo />
        {d && (
          <div className="ctx-pesos">
            <div className="ctx-tabla ctx-tabla--pesos" role="table" aria-label="Pesos del score">
              <div className="ctx-tabla__cab" role="row"><span>Término</span><span>Peso vigente</span><span>Sin redondear</span><span>Entre pliegues</span><span>Qué mide</span></div>
              {d.score.terminos.map((t) => (
                <div className="ctx-tabla__fila" role="row" key={t.clave}>
                  <span data-et="Término"><b>{t.nombre}</b></span>
                  <span data-et="Peso vigente" className="ctx-num">{fmtNum(t.peso_norm, 2)}</span>
                  <span data-et="Sin redondear" className="ctx-num">{d.score.sin_redondear ? fmtNum(d.score.sin_redondear[t.clave], 3) : ND}</span>
                  <span data-et="Entre pliegues" className="ctx-num">{rangoPesos(t.clave)}</span>
                  <span data-et="Qué mide" className="ctx-chico">{t.descripcion}</span>
                </div>
              ))}
            </div>
            <p className="ctx-par ctx-par--chico">Los pesos no los puso el autor: los aprendió <code>scripts/03b_validar_score.py</code> contra {(d.score.objetivos ?? []).map((o) => o.replace(/_/g, ' ')).join(', ')}, en pliegues por municipio, y quedaron en <code>models/pesos_score.json</code>.
              Se leen de <code>{d.score.origen}</code>; la versión del score es <Pill tono="gris">{d.score.version ?? ND}</Pill>. Si cambian, esta tabla cambia sola.</p>
            <Fuente>modelo propio (models/pesos_score.json y app/motor.py); validación con DENUE 11/2020 y 05/2026, Censo 2020 INEGI, ENIGH 2024.</Fuente>
          </div>
        )}
      </Seccion>

      <Seccion id="m-validacion" kicker="Validación espacial" titulo={<>Se probó en municipios <em>que el modelo no vio</em></>}>
        {d ? (
          <div className="ctx-val">
            <div className="ctx-val__txt">
              <CifraRueda valor={d.validacion.auc_global} formato={(n) => fmtNum(n, 3)} etiqueta="AUC global fuera de pliegue" />
              <p className="ctx-par">{d.validacion.metodo}. El AUC dice con qué probabilidad el modelo pone por encima a una zona donde sí apareció un negocio del giro frente a una donde no; 0.5 es el azar.
                Va de {fmtNum(Math.min(...aucPliegues), 3)} a {fmtNum(Math.max(...aucPliegues), 3)} entre pliegues: es estable.</p>
              <p className="ctx-par ctx-par--chico">El AUC global mezcla giros (parte se explica por cuántos negocios de cada giro hay); por eso importa más el AUC dentro de cada giro, abajo. Precisión promedio: {fmtNum(d.validacion.ap_global, 3)}; tasa base: {fmtPct(d.validacion.tasa_base, 1, true)} de los pares AGEB-giro tuvo una apertura.</p>
            </div>
            <div className="ctx-val__graf">
              <GraficaBarras titulo="AUC por pliegue (el eje va de 0 a 1)" fuente={d.validacion.fuente} dominio={[0, 1]} formato={(v) => fmtNum(v, 3)}
                filas={[...pliegues, { etiqueta: 'Global, fuera de pliegue', valor: d.validacion.auc_global ?? 0, tono: 'naranja' as const }]} />
            </div>
          </div>
        ) : <Cargando forma="mapa" alto={260} />}
      </Seccion>

      <Seccion id="m-giros" kicker="AUC por giro" titulo={<>Le gana a las <em>líneas base</em>, pero el score combinado no es el modelo</>}>
        {d && lb ? (
          <>
            <div className="ctx-giros__cab">
              <Opciones<Base> etiqueta="Línea base que se compara" valor={base} opciones={BASES.map((b) => ({ id: b.id, texto: b.texto }))} onCambio={setBase} />
              <div className="ctx-giros__lect" aria-live="polite">
                {giro ? (
                  <p><b>{giro.nombre}</b>: modelo <N>{fmtNum(giro.auc_modelo, 3)}</N> · densidad {fmtNum(giro.auc_densidad, 3)} · competencia Huff {fmtNum(giro.auc_competencia, 3)} · competencia en la AGEB {fmtNum(giro.auc_comp_ageb, 3)} · actividad {fmtNum(giro.auc_actividad, 3)} · score {fmtNum(giro.auc_score, 3)} <span className="chico">({fmtNum(giro.agebs_con_apertura)} AGEB con apertura)</span></p>
                ) : (
                  <p><b>Promedio de {fmtNum(lb.giros)} giros</b>: modelo <N>{fmtNum(lb.modelo_promedio, 3)}</N> · {infoBase.texto} <N>{fmtNum(lb.promedio[base === 'competencia' ? 'competencia' : base], 3)}</N>. El modelo le gana en <N>{fmtNum(lb.supera[base === 'competencia' ? 'competencia' : base])}</N> de {fmtNum(lb.giros)} giros. <span className="chico">Toca o pasa el cursor por un giro para ver todos sus AUC.</span></p>
                )}
              </div>
            </div>
            <div className="ctx-giros__leyenda"><span><i className="ctx-pt-m" /> Modelo de aperturas</span><span><i className="ctx-pt-b" /> {infoBase.texto}: {infoBase.largo}</span></div>
            <PuntosAuc giros={d.giros} base={base} activo={activo} onActivo={setActivo} />
            <Fuente>{d.fuentes.giros}. Solo giros con al menos 30 AGEB con apertura.</Fuente>
            <p className="ctx-par ctx-par--chico">El score combinado (la opción de hasta la derecha) queda debajo del modelo a propósito: castiga la competencia, y las aperturas crudas se aglomeran donde ya hay competidores. Por eso se validó también contra crecimiento neto y sobrevivencia (tabla siguiente).
              {sinDato.length > 0 && <> No entran {sinDato.map((g) => `${g.nombre.toLowerCase()} (${fmtNum(g.agebs_con_apertura)} AGEB con apertura, AUC ${fmtNum(g.auc_modelo, 3)})`).join(' y ')}: con tan pocas aperturas el AUC no es confiable.</>}</p>
          </>
        ) : <Cargando forma="mapa" alto={520} />}
        {vs && (
          <div className="ctx-vs">
            <h4 className="ctx-vs__t">El score contra lo que sí importa al decidir</h4>
            <div className="ctx-tabla ctx-tabla--vs" role="table" aria-label="Validación del score">
              <div className="ctx-tabla__cab" role="row"><span>Objetivo</span><span>Score vigente</span><span>Score anterior</span><span>Mejor línea base</span><span>Lectura</span></div>
              {vs.filas.map((f) => {
                const supera = f.vigente != null && f.mejor_base != null && f.vigente > f.mejor_base
                return (
                  <div className="ctx-tabla__fila" role="row" key={f.objetivo}>
                    <span data-et="Objetivo"><b>{f.etiqueta}</b><small>{f.metrica}</small></span>
                    <span data-et="Score vigente" className="ctx-num"><b>{fmtNum(f.vigente, 3)}</b><small>dentro de muestra{f.vigente_oos != null ? <> · {fmtNum(f.vigente_oos, 3)} fuera de muestra</> : null}</small></span>
                    <span data-et="Score anterior" className="ctx-num">{fmtNum(f.anterior, 3)}</span>
                    <span data-et="Mejor línea base" className="ctx-num">{fmtNum(f.mejor_base, 3)}<small>{f.mejor_base_nombre ? NOMBRE_BASE[f.mejor_base_nombre] ?? f.mejor_base_nombre : ''}</small></span>
                    <span data-et="Lectura"><Pill tono={supera ? 'verde' : 'amarillo'}>{supera ? 'supera a la línea base' : 'no supera a la línea base'}</Pill></span>
                  </div>
                )
              })}
            </div>
            <p className="ctx-par ctx-par--chico">«Dentro de muestra» usa pesos ya vistos con todos los municipios y es la cifra que se compara con las líneas base; «fuera de muestra» ajusta los pesos en 4 de 5 pliegues de municipios y los prueba en el que no vio; es la cifra principal.</p>
            <p className="ctx-par ctx-par--chico"><b>Salvedad:</b> la ventaja del score vigente en crecimiento neto viene sobre todo de la carga de los Censos Económicos 2024, que infla los «nuevos» del DENUE. En los objetivos que no dependen de esa carga (sobrevivencia y altas fuera de la carga censal) el score vigente empata o pierde contra el anterior. Se conserva por decisión de diseño, no como una victoria demostrada; el detalle está en <code>reports/validacion_score.md</code>.</p>
            <Fuente>{vs.fuente}.</Fuente>
          </div>
        )}
      </Seccion>

      <Seccion id="m-variables" kicker="Importancia de variables" titulo={<>Lo que más pesa: <em>{d?.importancia[0]?.nombre.toLowerCase() ?? '…'}</em> y los competidores que ya hay</>}>
        {d ? (
          <>
            <p className="ctx-par">Importancia por permutación: cuánto cae la precisión del modelo cuando se baraja una variable en un pliegue de municipios que no vio. Las 20 que más pesan, de {fmtNum(d.modelo.n_variables)}.</p>
            <GraficaBarras fuente={d.fuentes.importancia} formato={(v) => fmtNum(v, 3)} filas={d.importancia.map((i) => ({ etiqueta: i.nombre, valor: i.importancia ?? 0, tono: 'naranja' as const }))} />
            <p className="ctx-par ctx-par--chico">Que pese tanto la competencia ya instalada en la AGEB es la aglomeración: donde ya hay negocios del giro es donde más aparecen, en parte porque cierra uno y abre otro en el mismo local.</p>
          </>
        ) : <Cargando forma="lista" filas={6} />}
      </Seccion>

      <Seccion id="m-agente" kicker="Evaluación del agente" titulo={<>20 preguntas, una trampa y <em>cuánto tarda</em> cada respuesta</>}>
        {ev ? (
          <>
            <div className="ctx-kpis ctx-kpis--4">
              <Kpi valor={ev.pasan} formato={(n) => `${fmtNum(n)}/${fmtNum(ev.preguntas)}`} etiqueta="preguntas aprobadas" tono="accent" fuente="modelo propio, eval/evaluar.py" />
              <Kpi valor={ev.latencia_mediana_s} formato={(n) => `${fmtNum(n, 1)} s`} etiqueta="latencia mediana" retraso={80} fuente={`modelo propio, ${ev.modelo}`} />
              <Kpi valor={ev.latencia_p90_s} formato={(n) => `${fmtNum(n, 1)} s`} etiqueta="latencia del percentil 90" retraso={160} fuente="modelo propio, reports/evaluacion.json" />
              <Kpi valor={ev.latencia_max_s} formato={(n) => `${fmtNum(n, 1)} s`} etiqueta="la más lenta" retraso={240} fuente="modelo propio, reports/evaluacion.json" />
            </div>
            <p className="ctx-par">La pregunta trampa (una ciudad fuera de la ZMVM) {ev.trampa_pasa ? 'pasa: el agente dice que está fuera de alcance y no inventa colonias' : 'no pasa'}. Cada respuesta se califica con checks automáticos: que cada colonia exista, que las cifras coincidan con lo que regresaron las herramientas, que cite fuentes y que no pase de {fmtNum(ev.criterios.latencia_max_s)} s.
              {ev.mediana_bajo_objetivo === false && <> La mediana no cumple el objetivo de {fmtNum(ev.criterios.mediana_objetivo_s)} s: el modelo de lenguaje corre local en una Mac de 16 GB.</>}</p>
            <GraficaBarras titulo="Latencia por pregunta" fuente={ev.fuente} dominio={[0, ev.criterios.latencia_max_s]} formato={(v) => `${fmtNum(v, 1)} s`} formatoEje={(v) => `${fmtNum(v, 0)} s`}
              referencia={{ valor: ev.criterios.latencia_max_s, etiqueta: `límite de ${fmtNum(ev.criterios.latencia_max_s)} s` }}
              filas={ev.filas.map((f) => ({ etiqueta: `${f.id}. ${f.pregunta.length > 46 ? f.pregunta.slice(0, 45) + '…' : f.pregunta}`, valor: f.latencia_s ?? 0, tono: f.pasa ? ('naranja' as const) : ('gris' as const) }))} />
          </>
        ) : <Cargando forma="lista" filas={5} />}
      </Seccion>

      <Seccion id="m-limites" kicker="Límites honestos" titulo={<>Lo que el modelo <em>no puede decir</em></>}>
        <div className="ctx-limites">
          {(d?.limites ?? []).map((l, i) => (
            <article key={l.clave} className="ctx-limite">
              <h4>{l.titulo}</h4>
              <p><Inline t={l.texto} /></p>
              {l.cifras.length > 0 && <div className="ctx-limite__cifras">{l.cifras.map((c, j) => <CifraRueda key={j} valor={c.valor} formato={formatoCifra(c)} etiqueta={c.etiqueta} retraso={i * 40 + j * 80} />)}</div>}
              <p className="ctx-fuente-chica">Fuente: {l.fuente}.</p>
            </article>
          ))}
        </div>
        {!d && <Cargando forma="texto" filas={6} />}
      </Seccion>

      <Seccion id="m-profe" kicker="Preguntas que puede hacer el profe" titulo={<>Respuestas cortas, <em>con su fuente</em></>}>
        <div className="ctx-qa">
          {(d?.preguntas ?? []).map((q, i) => (
            <div key={q.pregunta} className="ctx-qa__item" data-abierta={abierta === i || undefined}>
              <button className="ctx-qa__p" aria-expanded={abierta === i} onClick={() => setAbierta(abierta === i ? null : i)}>
                <span>{q.pregunta}</span><span className="ctx-qa__mas" aria-hidden />
              </button>
              <div className="ctx-qa__cuerpo"><div><p><Inline t={q.respuesta} /></p><p className="ctx-fuente-chica">Fuente: {q.fuente}.</p></div></div>
            </div>
          ))}
        </div>
        {!d && <Cargando forma="texto" filas={5} />}
      </Seccion>
    </div>
  )
}
const N = ({ children }: { children: React.ReactNode }) => <strong className="ctx-n">{children}</strong>

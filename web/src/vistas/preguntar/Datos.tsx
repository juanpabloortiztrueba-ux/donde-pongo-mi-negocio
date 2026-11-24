import { useMemo, useState } from 'react'
import { ArrowUpRight, Info } from 'lucide-react'
import { Collapse } from '../../kit'
import { fmtNum, fmtPct, fmtPesos, GraficaBarras, href, ir, Fuente, Mapa, Pill, titulo } from '../../comun'
import { Cifra, num } from './Cifra'
import { Dato } from './Dato'
import type { DatosPregunta, ZonaTop } from './tipos'

// Lo que se pinta en cuanto las herramientas responden (~3 s), antes de que el LLM termine: mapa con el score del giro, las 5 zonas
// con sus cifras y los avisos de las herramientas. Todo viene de /api/preguntas (nada escrito a mano).

const pesosCompacto = (n: number) => fmtPesos(n, 0, true)

function Aviso({ tono, etiqueta, texto }: { tono: 'amarillo' | 'rojo' | 'azul'; etiqueta: string; texto: string }) {
  return (
    <div className="pre-aviso" data-tono={tono} role="note">
      <Pill tono={tono}>{etiqueta}</Pill>
      <p>{texto}</p>
    </div>
  )
}

function Tarjeta({ z, i, giro, corte }: { z: ZonaTop; i: number; giro: string; corte: string }) {
  const r = i * 90
  const enColonia = z.dist_a_colonia_km != null ? (z.en_colonia_consultada ? 'Dentro de la colonia pedida' : `A ${fmtNum(z.dist_a_colonia_km, 1)} km de la colonia pedida`) : null
  return (
    <li className="pre-zona">
      <a href={href('zona', z.ageb, { giro })} aria-label={`Abrir la ficha de ${titulo(z.colonia)}`}>
        <div className="pre-zona__cab">
          <span className="pre-zona__n">{i + 1}</span>
          <div className="pre-zona__t">
            <b>{titulo(z.colonia)}</b>
            <small>{titulo(z.municipio)} · AGEB {z.ageb}</small>
          </div>
          <div className="pre-zona__score">
            <b><Cifra valor={num(z.score)} formato={(n) => fmtNum(n, 1)} retraso={r} /></b>
            <small>de 100</small>
          </div>
          <ArrowUpRight size={16} className="pre-zona__ir" aria-hidden />
        </div>
        {enColonia && <div className="pre-zona__nota"><Pill tono={z.en_colonia_consultada ? 'verde' : 'gris'}>{enColonia}</Pill></div>}
        <div className="pre-zona__cifras">
          <Dato valor={z.prob_apertura_pct} formato={(n) => fmtPct(n)} etiqueta="prob. de apertura" fuente="modelo propio" retraso={r + 60} />
          <Dato valor={z.gasto_potencial_trim_mxn} formato={pesosCompacto} etiqueta="gasto potencial al trimestre" fuente="ENIGH 2024 y Censo 2020" retraso={r + 120} titulo="Gasto potencial del giro en el radio de influencia, por trimestre" />
          <Dato valor={z.competidores_ponderados} formato={(n) => fmtNum(n, 1)} etiqueta="competidores ponderados" fuente={`DENUE ${corte}`} retraso={r + 180} />
          <Dato valor={z.captura_huff_pct} formato={(n) => fmtPct(n)} etiqueta="captura de demanda" fuente="modelo propio (Huff)" retraso={r + 240} />
          <Dato valor={z.ingreso_trim_mediano_estimado_mxn} formato={pesosCompacto} etiqueta={`ingreso trimestral por hogar${z.nse_estimado ? `, NSE ${z.nse_estimado}` : ''}`} fuente="ENIGH 2024, estimado" retraso={r + 300} titulo="Ingreso trimestral mediano estimado por hogar (la ENIGH no representa colonias: es una estimación del proyecto)" />
          <Dato valor={z.edad_clave_pct} formato={(n) => fmtPct(n, 1)} etiqueta={`${z.edad_clave_etiqueta} (ZMVM ${num(z.edad_clave_pct_zmvm) != null ? fmtPct(num(z.edad_clave_pct_zmvm)!, 1) : 'NO ENCONTRADO'})`} fuente="Censo 2020 INEGI" retraso={r + 360} />
        </div>
      </a>
    </li>
  )
}

export function Datos({ datos, conMapa, onVerMapa, cargandoMapa }: { datos: DatosPregunta; conMapa: boolean; onVerMapa: () => void; cargandoMapa: boolean }) {
  const [avisos, setAvisos] = useState(false)
  const corte = datos.corte_denue ?? 'NO ENCONTRADO'
  const claveGiro = datos.giro?.clave ?? ''
  const valores = useMemo(() => datos.mapa?.valores, [datos.mapa])
  const resaltar = useMemo(() => datos.zonas.map((z) => z.ageb), [datos.zonas])
  const formato = useMemo(() => (v: number) => fmtNum(v), [])
  const filtros = Object.entries(datos.filtros ?? {})
  const sug = datos.sugerencias ?? []
  const hayZonas = datos.zonas.length > 0
  const sinGiro = !datos.giro && !hayZonas && !datos.fuera_de_alcance && !sug.length

  return (
    <section className="pre-datos" aria-label="Datos encontrados">
      {datos.fuera_de_alcance && (
        <div className="pre-fuera">
          <Pill tono="rojo">Fuera de alcance</Pill>
          <p>{datos.fuera_de_alcance.motivo}</p>
          <p className="chico">El modelo solo cubre las 5,875 AGEB urbanas de los 76 municipios de la ZMVM. Por eso no te doy colonias de ese lugar.</p>
          <Fuente>delimitación de zonas metropolitanas 2015 (SEDATU-CONAPO-INEGI); Censo 2020 INEGI</Fuente>
        </div>
      )}
      {sinGiro && datos.perfil_no_encontrado && (
        <div className="pre-fuera">
          <Pill tono="amarillo">No encontré el giro</Pill>
          <p>{datos.perfil_no_encontrado.motivo}</p>
          {datos.perfil_no_encontrado.propuestas_scian.length > 0 && (
            <p className="chico">Lo más parecido en el SCIAN: {datos.perfil_no_encontrado.propuestas_scian.map((p) => `${p.titulo} (${fmtNum(p.establecimientos_zmvm_2026)} establecimientos en la ZMVM)`).join('; ')}. Fuente: SCIAN 2023 INEGI, {`DENUE corte ${corte}`}.</p>
          )}
        </div>
      )}

      {(datos.giro || filtros.length > 0) && hayZonas && (
        <div className="pre-datos__cab">
          {datos.giro && <Pill tono="naranja">{datos.giro.nombre}</Pill>}
          {filtros.map(([k, v]) => <Pill key={k} tono="azul">{k === 'municipio' ? titulo(String(v)) : `${k.replace(/_/g, ' ')}: ${v}`}</Pill>)}
          <span className="chico">las {fmtNum(datos.zonas.length)} mejores de {fmtNum(datos.agebs_evaluadas)} AGEB evaluadas</span>
        </div>
      )}

      {datos.aviso_colonia && <Aviso tono="azul" etiqueta="Colonia" texto={datos.aviso_colonia} />}
      {datos.aviso_prob_baja && <Aviso tono="amarillo" etiqueta="Probabilidad baja" texto={datos.aviso_prob_baja} />}

      {sug.length > 0 && (
        <div className="pre-sug">
          <h3 className="pre-h">Giros que conviene considerar{datos.sugerencias_filtros?.municipio ? ` en ${titulo(datos.sugerencias_filtros.municipio)}` : ''}</h3>
          <GraficaBarras
            titulo="Viabilidad = prob. de apertura × prob. de seguir abierto"
            filas={sug.map((g) => ({ etiqueta: g.nombre ?? g.giro, valor: g.viabilidad_pct, tono: g.giro === claveGiro ? 'naranja' : 'gris' }))}
            formato={(v) => fmtPct(v)} dominio={[0, 100]} alto={sug.length * 40 + 30}
            fuente="modelo propio (modelo de aperturas, validación por municipio); DENUE corte 05/2026 vs 11/2020; el score de cada giro es relativo, esta barra no."
          />
          {datos.sugerencias_como_leer && <p className="chico pre-nota">{datos.sugerencias_como_leer}.</p>}
        </div>
      )}

      {hayZonas && (
        <div className="pre-rejilla">
          <div className="pre-mapa">
            {conMapa && datos.mapa && valores ? (
              <>
                <Mapa valores={valores} dominio={[0, 100]} etiqueta={`Score de ${(datos.giro?.nombre ?? 'este giro').toLowerCase()} (0–100)`} formatoValor={formato}
                  resaltar={resaltar} municipio={datos.mapa.municipio} alto={560} onClic={(cv) => ir('zona', cv, { giro: claveGiro })} />
                <Fuente>modelo propio (score por giro, relativo dentro del giro); Censo 2020 INEGI; DENUE corte {corte}; ENIGH 2024. Los números marcan las {fmtNum(datos.zonas.length)} zonas de la lista; un clic abre su ficha.</Fuente>
              </>
            ) : (
              <div className="pre-mapa__cerrado">
                <p>El mapa de {fmtNum(datos.agebs_evaluadas)} AGEB pesa unos 120 KB y se dibuja con WebGL.</p>
                <button className="c-boton" onClick={onVerMapa} disabled={cargandoMapa}>{cargandoMapa ? 'Cargando el mapa…' : 'Ver el mapa de esta pregunta'}</button>
              </div>
            )}
          </div>
          <div className="pre-zonas">
            <ol className="pre-zonas__lista">{datos.zonas.map((z, i) => <Tarjeta key={z.ageb} z={z} i={i} giro={claveGiro} corte={corte} />)}</ol>
            <Fuente>modelo propio; Censo 2020 INEGI; DENUE corte {corte}; ENIGH 2024. El score de 0 a 100 es un percentil dentro del giro: ordena colonias, no dice que el giro sea rentable.</Fuente>
            {(datos.avisos?.length ?? 0) > 0 && (
              <>
                <button className="pre-enlace" onClick={() => setAvisos((a) => !a)} aria-expanded={avisos}><Info size={15} />Qué tener en cuenta ({fmtNum(datos.avisos!.length)})</button>
                <Collapse open={avisos}><ul className="pre-avisos">{datos.avisos!.map((a, i) => <li key={i}>{a}</li>)}</ul></Collapse>
              </>
            )}
          </div>
        </div>
      )}

      {(datos.perfil || datos.macro || datos.municipio) && hayZonas && (
        <div className="pre-contexto">
          {datos.perfil && (
            <div>
              <h3 className="pre-h">El giro, con los supuestos del proyecto</h3>
              <ul className="pre-datos-lista">
                <li><b>{datos.perfil.ticket_promedio_mxn != null ? fmtPesos(datos.perfil.ticket_promedio_mxn) : 'NO ENCONTRADO'}</b> ticket promedio (supuesto)</li>
                <li><b>{datos.perfil.radio_influencia_m != null ? `${fmtNum(datos.perfil.radio_influencia_m)} m` : 'NO ENCONTRADO'}</b> radio de influencia</li>
              </ul>
              <Fuente>config/giros.yaml (supuestos del proyecto){datos.perfil.ticket_fuente ? `: ${datos.perfil.ticket_fuente}` : ''}</Fuente>
            </div>
          )}
          {datos.macro && (
            <div>
              <h3 className="pre-h">Entorno económico</h3>
              <p className="pre-ctx-p">{datos.macro.linea}</p>
              <Fuente>Banxico SIE e INEGI BIE (series en el texto)</Fuente>
            </div>
          )}
          {datos.municipio && (
            <div>
              <h3 className="pre-h">Sobre {titulo(datos.municipio.nombre)}</h3>
              <p className="pre-ctx-p">{datos.municipio.ficha.join(' ')}</p>
              <Fuente>Censo 2020 INEGI (fichas de carpetas/03_municipios)</Fuente>
            </div>
          )}
        </div>
      )}
    </section>
  )
}

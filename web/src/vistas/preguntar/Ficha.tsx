import { useEffect, useMemo, useState, type ReactNode } from 'react'
import { ArrowLeft, Search } from 'lucide-react'
import { Meter } from '../../kit'
import {
  apiGet, Cabecera, Cargando, ErrorApi, esCancelado, fijarQuery, fmtNum, fmtPct, fmtPesos, fmtCompacto, Fuente, GraficaBarras, GraficaLineas, href, ir,
  Kpi, Mapa, Pill, SelectorGiro, SelectorMunicipio, titulo, useApi, type VistaProps,
} from '../../comun'
import { Cifra, num } from './Cifra'
import { Comparativa } from './Comparativa'
import { Dato } from './Dato'
import type { FichaZona, RespuestaBusqueda } from './tipos'
import './preguntar.css'

// Vista Ficha de zona: todo lo que sabe el modelo de una AGEB (colonia), con o sin giro. Cada bloque dice su fuente.
// #/zona (sin AGEB) muestra el buscador; #/zona/<cvegeo>?giro= muestra la ficha.

const EJEMPLOS = ['Del Valle', 'Polanco', 'Roma Norte', 'Pedregal de Santo Domingo', 'Lindavista']
const pesos = (n: number) => fmtPesos(n)
const pesosC = (n: number) => fmtPesos(n, 0, true)
/** Marca del eje Y en porcentaje con los decimales que pida la escala (0 %, 5 %, 10 % o 0.5 %, 1 %, 1.5 %): todas las marcas con la misma regla, sin redondeos desiguales. */
const pctMarca = (n: number) => fmtPct(n, Math.abs(n * 10 - Math.round(n * 10)) < 1e-9 ? (Math.abs(n - Math.round(n)) < 1e-9 ? 0 : 1) : 2)

export default function Ficha({ ruta }: VistaProps) {
  return ruta.param ? <FichaDe cv={ruta.param} giro={ruta.query.giro || null} /> : <Buscador giro={ruta.query.giro || null} />
}

// ------------------------------------------------------------------------------------------------ buscador
function Buscador({ giro }: { giro: string | null }) {
  const [q, setQ] = useState('')
  const [mun, setMun] = useState<string | null>(null)
  const [res, setRes] = useState<RespuestaBusqueda | null>(null)
  const [cargando, setCargando] = useState(false)
  const [error, setError] = useState<Error | null>(null)
  const [intento, setIntento] = useState(0)
  const activo = q.trim().length >= 2 || !!mun

  useEffect(() => {
    if (!activo) { setRes(null); setError(null); setCargando(false); return }
    const ac = new AbortController()
    const t = setTimeout(() => {
      setCargando(true); setError(null)
      apiGet<RespuestaBusqueda>(`/api/buscar_zona?q=${encodeURIComponent(q.trim())}${mun ? `&municipio=${mun}` : ''}`, { signal: ac.signal })
        .then((r) => { setRes(r); setCargando(false) })
        .catch((e) => { if (!esCancelado(e)) { setError(e); setCargando(false) } })
    }, 220)
    return () => { clearTimeout(t); ac.abort() }
  }, [q, mun, activo, intento])

  return (
    <div className="mc-cuerpo pre pre-fic">
      <Cabecera seccion="Ficha de zona" titulo={<>Busca una colonia y mira <em>todo lo que sabe el modelo</em></>}>
        Escribe el nombre de una colonia o la clave de una AGEB. Si la colonia tiene varias AGEB (las áreas del Censo), eliges cuál abrir.
      </Cabecera>
      <div className="pre-buscar">
        <label className="pre-form__campo pre-buscar__q">
          <span className="sr-only">Colonia o AGEB</span>
          <Search size={18} aria-hidden />
          <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Colonia o clave AGEB (por ejemplo: Del Valle)" maxLength={80} autoComplete="off" autoFocus />
        </label>
        <SelectorMunicipio valor={mun} onCambio={setMun} etiqueta="Municipio" vacio="Toda la ZMVM" />
      </div>
      <div className="pre-ejemplos" aria-label="Ejemplos" style={{ marginTop: 14 }}>
        {EJEMPLOS.map((e) => <button key={e} type="button" className="pre-ejemplo" onClick={() => setQ(e)}>{e}</button>)}
      </div>

      <section className="pre-resultados" aria-live="polite">
        {!activo && <p className="chico">También puedes elegir un municipio para ver sus colonias más pobladas.</p>}
        {error && <ErrorApi error={error} reintentar={() => setIntento((n) => n + 1)} titulo="No pude buscar" />}
        {cargando && !res && <Cargando forma="lista" filas={4} />}
        {res && res.motivo && !res.resultados.length && (
          <div className="pre-vacio-res">
            <p>{res.motivo}</p>
            {res.sugerencias.length > 0 && <p className="chico">¿Quisiste decir? {res.sugerencias.map((s, i) => <button key={s} className="pre-enlace" onClick={() => setQ(s)}>{s}{i < res.sugerencias.length - 1 ? ',' : ''}</button>)}</p>}
          </div>
        )}
        {res && res.resultados.length > 0 && (
          <>
            <ol className="pre-res">
              {res.resultados.map((r) => (
                <li key={r.colonia + r.cvegeo_mun} className="pre-res__fila">
                  <div className="pre-res__t"><b>{titulo(r.colonia)}</b><small>{titulo(r.municipio)} · {fmtNum(r.n_agebs)} {r.n_agebs === 1 ? 'AGEB' : 'AGEB'} · {fmtNum(r.habitantes)} habitantes</small></div>
                  <div className="pre-res__agebs">
                    {r.agebs.map((a) => <a key={a.cvegeo} className="pre-chip" href={href('zona', a.cvegeo, { giro })}>AGEB {a.cvegeo}<small>{fmtNum(a.habitantes)} hab.</small></a>)}
                    {r.n_agebs > r.agebs.length && <span className="chico">y {fmtNum(r.n_agebs - r.agebs.length)} más</span>}
                  </div>
                </li>
              ))}
            </ol>
            <Fuente>{res.fuente}</Fuente>
          </>
        )}
      </section>
    </div>
  )
}

// ------------------------------------------------------------------------------------------------ ficha
function Bloque({ titulo: t, sub, children, ancho = false }: { titulo: string; sub?: string; children: ReactNode; ancho?: boolean }) {
  return (
    <section className="pre-bloque" data-ancho={ancho || undefined}>
      <h2 className="pre-bloque__t">{t}</h2>
      {sub && <p className="pre-bloque__sub">{sub}</p>}
      {children}
    </section>
  )
}

function FichaDe({ cv, giro }: { cv: string; giro: string | null }) {
  const ruta = `/api/zona/${encodeURIComponent(cv)}${giro ? `?giro=${encodeURIComponent(giro)}` : ''}`
  const { datos: f, cargando, error, recargar } = useApi<FichaZona>(ruta)
  const volver = <a className="pre-enlace" href={href('zona', undefined, { giro })}><ArrowLeft size={14} />Buscar otra colonia</a>

  if (error) return (
    <div className="mc-cuerpo pre pre-fic">
      <Cabecera seccion="Ficha de zona" titulo={<>No encontré esa <em>AGEB</em></>}>La clave que abriste no está entre las 5,875 AGEB urbanas de la ZMVM que cubre el modelo.</Cabecera>
      <div style={{ marginTop: 28 }}><ErrorApi error={error} reintentar={recargar} titulo="No pude abrir la ficha" /><p style={{ marginTop: 14 }}>{volver}</p></div>
    </div>
  )
  if (cargando || !f) return (
    <div className="mc-cuerpo pre pre-fic">
      <Cabecera seccion="Ficha de zona" titulo={<>Abriendo la <em>ficha</em>…</>}>Leyendo el Censo 2020, el DENUE y el modelo para la AGEB {cv}.</Cabecera>
      <div style={{ marginTop: 32 }}><Cargando forma="kpis" filas={4} /></div>
      <div style={{ marginTop: 28 }}><Cargando forma="mapa" alto={360} /></div>
    </div>
  )
  return <Contenido f={f} giro={giro} volver={volver} />
}

function Contenido({ f, giro, volver }: { f: FichaZona; giro: string | null; volver: ReactNode }) {
  const g = f.giro
  const v = f.vecinas
  const formatoMapa = useMemo(() => (n: number) => fmtNum(n), [])
  const seleccion = f.ageb
  const nombre = titulo(f.colonia ?? 'Sin nombre')
  const p = f.poblacion
  const emp = f.empleo
  const tr = f.transporte
  // si la estación más cercana de cualquier sistema es la misma estación de Metro, se muestra una sola vez (con la píldora «Metro»)
  const mismaEstacion = !!tr.metro && tr.estacion === tr.metro && tr.distancia_m != null && tr.distancia_m === tr.distancia_metro_m
  const grado = f.marginacion.grado

  const sectores = emp.sectores.slice(0, 8)
  const probBaja = g && num(g.prob_apertura_pct) != null && (num(g.prob_apertura_pct) as number) < 10

  return (
    <div className="mc-cuerpo pre pre-fic">
      <Cabecera seccion="Ficha de zona" sub={titulo(f.municipio)} titulo={<><em>{nombre}</em></>}>
        AGEB {f.ageb}{f.cp ? ` · código postal ${f.cp}` : ''}{f.tipo_asentamiento ? ` · ${f.tipo_asentamiento.toLowerCase()}` : ''}. Nombre de colonia tomado del {f.colonia_fuente === 'denue' ? 'DENUE' : 'Censo'}; el Censo no publica colonias, solo AGEB.
      </Cabecera>

      <div className="pre-fic__ctl">
        <SelectorGiro valor={giro} onCambio={(c) => fijarQuery({ giro: c })} etiqueta="Giro" vacio="Sin giro" />
        {volver}
      </div>

      <div className="pre-fic__cima">
        <div className="pre-mapa pre-mapa--ficha">
          {v ? (
            <>
              <Mapa valores={v.valores} dominio={v.dominio} etiqueta={v.etiqueta} formatoValor={formatoMapa} seleccion={seleccion} zoomMaxSeleccion={13} alto={430}
                onClic={(c) => ir('zona', c, { giro })} />
              <Fuente>{v.fuente}. Se pintan las AGEB a {fmtNum(v.radio_km, 1)} km o menos; el contorno grueso es esta zona y un clic en otra abre su ficha.</Fuente>
            </>
          ) : <p className="chico">NO ENCONTRADO: no pude armar las AGEB vecinas.</p>}
        </div>
        <div className="pre-fic__kpis">
          <Kpi valor={p.habitantes} etiqueta="habitantes" fuente={p.fuente} />
          <Kpi valor={p.hogares} etiqueta="hogares" fuente={p.fuente} retraso={80} />
          <Kpi valor={p.densidad_hab_km2} etiqueta="habitantes por km²" fuente={p.fuente} retraso={160} />
          <Kpi valor={emp.negocios_en_ageb} etiqueta="negocios en la AGEB" fuente={emp.fuente.split(' (')[0]} retraso={240} tono="accent" />
        </div>
      </div>

      {g ? (
        <section className="pre-giro" aria-label={`Para ${g.nombre}`}>
          <h2 className="seccion-t">Para {g.nombre?.toLowerCase() ?? g.clave}</h2>
          <div className="pre-giro__fila">
            <div className="pre-giro__score">
              <div className="pre-giro__n"><Cifra valor={num(g.score)} formato={(n) => fmtNum(n, 1)} duracion={1100} /><small>de 100</small></div>
              <Meter value={(num(g.score) ?? 0) / 100} />
              <p className="pre-giro__lugar">
                {g.en_top_5 ? <Pill tono="verde">Entre las 5 mejores</Pill> : <Pill tono="naranja">Mejor que {g.percentil != null ? fmtPct(g.percentil, 1) : 'NO ENCONTRADO'} de las AGEB</Pill>}
                <span>Lugar {fmtNum(g.rank_zmvm)} de {fmtNum(g.de_agebs)} para este giro</span>
              </p>
            </div>
            <div className="pre-giro__cifras">
              <Dato valor={g.prob_apertura_pct} formato={(n) => fmtPct(n)} etiqueta="prob. de apertura" fuente="modelo propio" acento />
              <Dato valor={g.prob_sigue_abierto_pct} formato={(n) => fmtPct(n)} etiqueta="prob. de seguir abierto" fuente="modelo propio (poco confiable)" retraso={60} titulo="El modelo de supervivencia es débil (AUC 0.59): úsalo como señal, no como promesa" />
              <Dato valor={g.competidores_ponderados} formato={(n) => fmtNum(n, 1)} etiqueta={`competidores ponderados a ${fmtNum(g.radio_m)} m`} fuente="DENUE (modelo propio)" retraso={120} />
              <Dato valor={g.captura_huff_pct} formato={(n) => fmtPct(n)} etiqueta="captura de demanda" fuente="modelo propio (Huff)" retraso={180} />
              <Dato valor={g.complementarios_ponderados} formato={(n) => fmtNum(n, 1)} etiqueta="negocios complementarios" fuente="DENUE (modelo propio)" retraso={240} />
              <Dato valor={g.gasto_potencial_trim_mxn} formato={pesosC} etiqueta="gasto potencial al trimestre" fuente="ENIGH 2024 y Censo 2020" retraso={300} titulo="Gasto potencial del giro en el radio de influencia" />
              <Dato valor={g.aperturas_esperadas_en_radio} formato={(n) => fmtNum(n, 2)} etiqueta="aperturas esperadas en el radio" fuente="modelo propio" retraso={360} />
              <Dato valor={g.demanda_de_personas.startsWith('empleos') ? g.empleos_en_radio : g.residentes_objetivo_en_radio} formato={(n) => fmtNum(n)}
                etiqueta={g.demanda_de_personas.startsWith('empleos') ? 'empleos en el radio' : 'residentes objetivo en el radio'} fuente={g.demanda_de_personas.startsWith('empleos') ? 'DENUE' : 'Censo 2020 INEGI'} retraso={420} />
            </div>
          </div>
          <p className="pre-giro__edad">{g.edad_clave_etiqueta}: {num(g.edad_clave_pct) != null ? fmtPct(num(g.edad_clave_pct)!, 1) : 'NO ENCONTRADO'} de la gente de esta AGEB, contra {num(g.edad_clave_pct_zmvm) != null ? fmtPct(num(g.edad_clave_pct_zmvm)!, 1) : 'NO ENCONTRADO'} en toda la ZMVM (Censo 2020 INEGI).</p>
          {probBaja && <div className="pre-aviso" data-tono="amarillo" role="note"><Pill tono="amarillo">Probabilidad baja</Pill><p>En esta AGEB abren pocos negocios de este giro. El score solo dice qué tan buena es la zona frente a las demás para el giro, no que el giro sea viable.</p></div>}
          <Fuente>{g.fuente}. El score de 0 a 100 es un percentil dentro del giro: no compara giros entre sí.</Fuente>
        </section>
      ) : (
        <section className="pre-giro pre-giro--vacio">
          <h2 className="seccion-t">Para un giro</h2>
          <p>{giro ? `NO ENCONTRADO: «${giro}» no es un giro del catálogo.` : 'Elige un giro arriba para ver aquí su score, su probabilidad de apertura, la competencia y los negocios complementarios de esta zona. El mapa pasa de mostrar el decil de ingreso a mostrar el score de ese giro.'}</p>
        </section>
      )}

      <div className="pre-bloques">
        <Bloque titulo="Quiénes viven aquí" sub="Edades de la AGEB contra el promedio de la ZMVM">
          <Comparativa nombreA="Esta AGEB" nombreB="ZMVM" formato={(n) => fmtPct(n, 1)} fuente={f.edades.fuente}
            filas={f.edades.grupos.map((e) => ({ etiqueta: e.etiqueta, a: e.pct, b: e.pct_zmvm, nota: e.personas != null ? `${fmtNum(e.personas)} personas` : undefined }))} />
        </Bloque>

        <Bloque titulo="Bienes de la vivienda" sub="Porcentaje de viviendas particulares habitadas">
          <Comparativa nombreA="Esta AGEB" nombreB="ZMVM" formato={(n) => fmtPct(n, 1)} maximo={100} fuente={f.vivienda.fuente}
            filas={f.vivienda.bienes.map((b) => ({ etiqueta: b.etiqueta, a: b.pct, b: b.pct_zmvm }))} />
        </Bloque>

        <Bloque titulo="Escolaridad y marginación" sub="Años de estudio y grado de marginación urbana">
          <Comparativa nombreA="Esta AGEB" nombreB="ZMVM" formato={(n) => `${fmtNum(n, 1)} años`} fuente={f.escolaridad.fuente}
            filas={[{ etiqueta: 'Escolaridad promedio', a: f.escolaridad.anios, b: f.escolaridad.anios_zmvm }]} />
          <div className="pre-marg">
            <div className="pre-marg__cab">
              <Pill tono={grado === 'Alto' || grado === 'Muy alto' ? 'rojo' : grado === 'Medio' ? 'amarillo' : 'verde'}>{grado ? `Marginación ${grado.toLowerCase().replace(/bajo$/, 'baja').replace(/alto$/, 'alta')}` : 'NO ENCONTRADO'}</Pill>
              <span className="chico">índice {f.marginacion.indice != null ? fmtNum(f.marginacion.indice, 1) : 'NO ENCONTRADO'} (más alto = menos marginada)</span>
            </div>
            <GraficaBarras orientacion="vertical" alto={200} titulo="AGEB de la ZMVM por grado de marginación (esta zona, en naranja)"
              filas={f.marginacion.grados_zmvm.map((x) => ({ etiqueta: x.grado, valor: x.agebs, tono: x.grado === grado ? 'naranja' : 'gris' }))} formato={(n) => fmtNum(n)} fuente={f.marginacion.fuente} />
          </div>
        </Bloque>

        <Bloque titulo="Ingreso estimado" sub="El decil lo estima el proyecto: la ENIGH no representa colonias">
          <div className="pre-ing">
            <Dato valor={f.ingreso.decil} formato={(n) => fmtNum(n)} etiqueta="decil de ingreso (1 a 10)" fuente="ENIGH 2024, estimado" grande acento />
            <Dato valor={f.ingreso.ingreso_trim_mediano} formato={pesos} etiqueta="ingreso trimestral mediano por hogar" fuente="ENIGH 2024, estimado" retraso={80} grande />
            <div className="pre-est"><b>{f.ingreso.nse ? <Pill tono="azul">{`NSE ${f.ingreso.nse}`}</Pill> : <span className="pre-nd">NO ENCONTRADO</span>}</b><span>nivel socioeconómico</span><small>modelo propio</small></div>
          </div>
          <GraficaLineas titulo="Probabilidad de cada decil: esta AGEB contra la ZMVM" alto={220} etiquetaX="Decil de ingreso (1 = el más bajo)" incluirCero formatoY={pctMarca}
            series={[
              { nombre: 'Esta AGEB', tono: 'naranja', puntos: f.ingreso.prob_deciles_pct.map((y, i) => ({ x: i + 1, y: y ?? 0 })) },
              { nombre: 'ZMVM', tono: 'azul', puntos: f.ingreso.prob_deciles_zmvm_pct.map((y, i) => ({ x: i + 1, y: y ?? 0 })) },
            ]}
            fuente={f.ingreso.fuente} />
        </Bloque>

        <Bloque titulo="Negocios y empleo cerca" sub="A 500 m y a 1 km de esta AGEB" ancho>
          <div className="pre-emp">
            <Dato valor={emp.negocios_500m} formato={(n) => fmtNum(n)} etiqueta="negocios a 500 m" fuente={emp.fuente.split(' (')[0]} />
            <Dato valor={emp.negocios_1km} formato={(n) => fmtNum(n)} etiqueta="negocios a 1 km" fuente={emp.fuente.split(' (')[0]} retraso={60} />
            <Dato valor={emp.empleos_500m} formato={fmtCompacto} etiqueta="empleos a 500 m" fuente={emp.fuente.split(' (')[0]} retraso={120} />
            <Dato valor={emp.empleos_1km} formato={fmtCompacto} etiqueta="empleos a 1 km" fuente={emp.fuente.split(' (')[0]} retraso={180} />
            <Dato valor={emp.escuelas_1km} formato={(n) => fmtNum(n)} etiqueta="escuelas a 1 km" fuente={emp.fuente.split(' (')[0]} retraso={240} />
            <Dato valor={emp.hospitales_1km} formato={(n) => fmtNum(n)} etiqueta="hospitales a 1 km" fuente={emp.fuente.split(' (')[0]} retraso={300} />
          </div>
          <Comparativa titulo="Negocios por sector (los 8 con más negocios a 1 km)" nombreA="A 1 km" nombreB="A 500 m" formato={(n) => fmtNum(n)} fuente={emp.fuente}
            filas={sectores.map((s) => ({ etiqueta: s.nombre, a: s.n_1km, b: s.n_500m }))} />
        </Bloque>

        <Bloque titulo="Transporte" sub="Estación más cercana de Metro, Metrobús y otros sistemas" ancho>
          <div className="pre-tr">
            <div>
              <p className="pre-tr__t"><b>{tr.estacion ?? 'NO ENCONTRADO'}</b>{tr.sistema && <Pill tono="azul">{tr.sistema}</Pill>}</p>
              <Dato valor={tr.distancia_m} formato={(n) => `${fmtNum(n)} m`} etiqueta="a la estación más cercana" fuente="datos.cdmx.gob.mx y OpenStreetMap" grande />
            </div>
            {!mismaEstacion && (
              <div>
                <p className="pre-tr__t"><b>{tr.metro ? `Metro ${tr.metro}` : 'NO ENCONTRADO'}</b></p>
                <Dato valor={tr.distancia_metro_m} formato={(n) => `${fmtNum(n)} m`} etiqueta="a la estación de Metro más cercana" fuente="datos.cdmx.gob.mx" grande retraso={80} />
              </div>
            )}
            <Dato valor={tr.afluencia_metro_anual} formato={fmtCompacto} etiqueta="entradas al año en esa estación del Metro" fuente="afluencia del Metro 2025, datos.cdmx.gob.mx" grande retraso={160} />
            <Dato valor={tr.estaciones_1km} formato={(n) => fmtNum(n)} etiqueta="estaciones a 1 km" fuente="datos.cdmx.gob.mx y OpenStreetMap" grande retraso={240} />
          </div>
          <Fuente>{tr.fuente}</Fuente>
        </Bloque>
      </div>

      <section className="pre-fuentes pre-fuentes--ficha" aria-label="Fuentes de la ficha">
        <h3 className="pre-h">Fuentes de esta ficha</h3>
        <ul>{f.fuentes.map((s) => <li key={s}>{s}</li>)}</ul>
      </section>
    </div>
  )
}

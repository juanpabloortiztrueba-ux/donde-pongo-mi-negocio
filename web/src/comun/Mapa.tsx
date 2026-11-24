import { useEffect, useMemo, useRef, useState, type CSSProperties } from 'react'
import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import { cargarGeoAgebs, cargarGeoMunicipios, ErrorApi as ErrorTipo, type GeoColeccion, type GeoFeature } from './api'
import { categorica, colorDeValor, gradienteSecuencial, SEC_VACIO } from './escalas'
import { useEstado } from './estado'
import { ErrorApi } from './ErrorApi'
import { Cargando } from './Cargando'
import { titulo } from './formato'
import { useTema } from './tema'
import './comun.css'

export interface MapaProps {
  /** cvegeo → valor (modo secuencial). Las AGEB sin valor salen en gris. */
  valores?: Record<string, number>
  /** Rango de la escala y de la leyenda. Por defecto [0, 100] (score). */
  dominio?: [number, number]
  /** Título de la leyenda: «Score de heladería (0–100)». */
  etiqueta?: string
  /** Cómo se escribe un valor en la leyenda y en el hover (por defecto, número es-MX). */
  formatoValor?: (v: number) => string
  /** Modo categórico: cvegeo → índice de categoría (0–7, orden fijo; más allá es «Otros»). Tiene prioridad sobre `valores`. */
  categorias?: Record<string, number>
  /** Nombres de las categorías, en el orden de los índices. */
  nombresCategorias?: string[]
  /** Lista de cvegeo que se marca con números 1, 2, 3… (en ese orden) y contorno fuerte. */
  resaltar?: string[]
  /** Encuadra (fitBounds con padding) las AGEB de `resaltar` cada vez que cambia esa lista, para que los números no se amontonen a la escala de toda la ZMVM.
   *  Tiene prioridad sobre el encuadre del municipio; una `seleccion` con vuelo la supera. Por defecto false. */
  encuadrarResaltadas?: boolean
  /** Acercamiento máximo al encuadrar `resaltar` (por defecto 14.5). */
  zoomMaxResaltadas?: number
  /** Un cvegeo seleccionado (contorno fuerte) y al que el mapa puede volar. */
  seleccion?: string | null
  /** Vuela a la `seleccion` cuando cambia (por defecto true). */
  volarASeleccion?: boolean
  /** cvegeo_mun (5 dígitos) para filtrar: encuadra (fitBounds) ese municipio y atenúa el resto. null = toda la ZMVM. */
  municipio?: string | null
  /** Capa de puntos opcional. `color` en CSS; `etiqueta` aparece en el hover. */
  puntos?: { lon: number; lat: number; color?: string; etiqueta?: string }[]
  /** Clic en una AGEB o en un número: recibe el cvegeo y sus propiedades (cvegeo, colonia, municipio). */
  onClic?: (cvegeo: string, props: { cvegeo: string; colonia: string | null; municipio: string }) => void
  /** Alto del mapa (px o CSS). Por defecto 560. */
  alto?: number | string
  /** Leyenda por pasos (variables ordinales): en vez del degradado continuo, un cuadro por nivel con el color que le toca en la escala. */
  pasosLeyenda?: { valor: number; nombre: string }[]
  /** Acercamiento máximo al volar a la `seleccion` (por defecto 15.5). Con valores bajos (13–14) se ven las AGEB vecinas. */
  zoomMaxSeleccion?: number
  /** Radio en px de los círculos de la capa `puntos` (por defecto 4). Con muchos puntos conviene 2–3. */
  radioPuntos?: number
  /** Muestra el interruptor «Mapa base (OpenStreetMap)». Solo funciona si hay internet. Por defecto true. */
  interruptorBase?: boolean
  /** Oculta la leyenda. */
  sinLeyenda?: boolean
}

// Plantilla de teselas OSM: única URL externa del build. Solo se usa si hay internet y el usuario prende el mapa base.
const OSM = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
const COLOR_LINEA = { light: 'rgba(24,24,27,0.20)', dark: 'rgba(255,255,255,0.16)' }
const COLOR_MUN = { light: 'rgba(24,24,27,0.55)', dark: 'rgba(255,255,255,0.45)' }
const COLOR_TINTA = { light: '#18181b', dark: '#f2f2f3' }
const FONDO = { light: '#ffffff', dark: '#0d0d0f' }

type Caja = [number, number, number, number]
const cajas = new WeakMap<GeoFeature, Caja>()
function cajaDe(f: GeoFeature): Caja {
  let c = cajas.get(f)
  if (c) return c
  let x0 = 180, y0 = 90, x1 = -180, y1 = -90
  const rec = (a: unknown): void => {
    if (Array.isArray(a) && typeof a[0] === 'number') {
      const [x, y] = a as number[]
      if (x < x0) x0 = x; if (x > x1) x1 = x; if (y < y0) y0 = y; if (y > y1) y1 = y
    } else if (Array.isArray(a)) a.forEach(rec)
  }
  rec(f.geometry.coordinates)
  c = [x0, y0, x1, y1]; cajas.set(f, c)
  return c
}
function unir(cs: Caja[]): Caja | null {
  if (!cs.length) return null
  return cs.reduce((a, c) => [Math.min(a[0], c[0]), Math.min(a[1], c[1]), Math.max(a[2], c[2]), Math.max(a[3], c[3])] as Caja)
}

// El tooltip va a +12 px del cursor; si no cabe a la derecha o abajo, pasa al otro lado (no se corta con el borde del mapa).
const TIP_W = 240, TIP_H = 84
function posTip(x: number, y: number, el: HTMLElement | null): CSSProperties {
  const w = el?.clientWidth ?? 9999, h = el?.clientHeight ?? 9999
  const izq = x + 12 + TIP_W > w, arr = y + 12 + TIP_H > h
  return { left: izq ? Math.max(4, x - 12 - TIP_W) : x + 12, top: arr ? Math.max(4, y - 12 - TIP_H) : y + 12, transform: 'none', ...(izq ? { textAlign: 'right' as const } : null) }
}

export function Mapa({
  valores, dominio = [0, 100], etiqueta, formatoValor = (v) => new Intl.NumberFormat('es-MX', { maximumFractionDigits: 1 }).format(v),
  categorias, nombresCategorias, resaltar, encuadrarResaltadas = false, zoomMaxResaltadas = 14.5, seleccion, pasosLeyenda, zoomMaxSeleccion = 15.5, radioPuntos = 4, volarASeleccion = true, municipio = null, puntos, onClic, alto = 560, interruptorBase = true, sinLeyenda,
}: MapaProps) {
  const { tema } = useTema()
  const { estado } = useEstado()
  const hayInternet = !!estado?.internet
  const [baseOSM, setBaseOSM] = useState(false)
  const osmActivo = baseOSM && hayInternet

  const caja = useRef<HTMLDivElement>(null)
  const mapa = useRef<maplibregl.Map | null>(null)
  const [listo, setListo] = useState(false)
  const [sinWebgl, setSinWebgl] = useState(false)
  const [geo, setGeo] = useState<GeoColeccion | null>(null)
  const [muns, setMuns] = useState<GeoColeccion | null>(null)
  const [error, setError] = useState<Error | null>(null)
  const [reintento, setReintento] = useState(0)
  const [tip, setTip] = useState<{ x: number; y: number; cv: string; colonia: string | null; mun: string } | null>(null)
  const marcadores = useRef<maplibregl.Marker[]>([])
  const estadoPrevio = useRef<Map<string, string>>(new Map())
  // lo último de las props, para los manejadores del mapa que se crean una sola vez
  const vivo = useRef({ valores, categorias, dominio, formatoValor, onClic, puntos, radioPuntos })
  vivo.current = { valores, categorias, dominio, formatoValor, onClic, puntos, radioPuntos }

  // geometrías (una vez por sesión)
  useEffect(() => {
    let activo = true
    setError(null)
    Promise.all([cargarGeoAgebs(), cargarGeoMunicipios()]).then(([a, m]) => { if (activo) { setGeo(a); setMuns(m) } })
      .catch((e) => activo && setError(e instanceof ErrorTipo ? e : new Error(String(e))))
    return () => { activo = false }
  }, [reintento])

  // crear el mapa (fondo liso, sin teselas)
  useEffect(() => {
    if (!caja.current) return
    let m: maplibregl.Map
    try {
      m = new maplibregl.Map({
        container: caja.current, attributionControl: false, dragRotate: false, pitchWithRotate: false,
        style: { version: 8, sources: {}, layers: [{ id: 'fondo', type: 'background', paint: { 'background-color': FONDO[tema] } }] },
        center: [-99.13, 19.43], zoom: 9, minZoom: 7, maxZoom: 17,
      })
    } catch { setSinWebgl(true); return }
    m.touchZoomRotate.disableRotation()
    m.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-left')
    m.addControl(new maplibregl.AttributionControl({ compact: true }), 'bottom-right')
    m.on('load', () => setListo(true))
    const ro = new ResizeObserver(() => m.resize())
    ro.observe(caja.current)
    mapa.current = m
    if (import.meta.env.DEV) (window as unknown as { __mapa?: unknown }).__mapa = m
    return () => { ro.disconnect(); marcadores.current.forEach((k) => k.remove()); marcadores.current = []; m.remove(); mapa.current = null; setListo(false); estadoPrevio.current = new Map() }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // fuentes y capas, cuando hay mapa y geometría
  useEffect(() => {
    const m = mapa.current
    if (!m || !listo || !geo || m.getSource('agebs')) return
    m.addSource('agebs', { type: 'geojson', data: geo as never, promoteId: 'cvegeo' })
    m.addLayer({ id: 'agebs-fill', type: 'fill', source: 'agebs', paint: {
      'fill-color': ['coalesce', ['feature-state', 'c'], SEC_VACIO.light],
      'fill-opacity': ['case', ['boolean', ['feature-state', 'f'], false], 0.12, 0.9] } })
    m.addLayer({ id: 'agebs-line', type: 'line', source: 'agebs', paint: {
      'line-color': ['case', ['boolean', ['feature-state', 's'], false], COLOR_TINTA.light, COLOR_LINEA.light],
      'line-width': ['interpolate', ['linear'], ['zoom'],
        8, ['case', ['boolean', ['feature-state', 's'], false], 2.5, ['boolean', ['feature-state', 'h'], false], 2, 0.1],
        13, ['case', ['boolean', ['feature-state', 's'], false], 2.5, ['boolean', ['feature-state', 'h'], false], 2, 0.7]] } })
    if (muns) {
      m.addSource('municipios', { type: 'geojson', data: muns as never })
      m.addLayer({ id: 'municipios-line', type: 'line', source: 'municipios', paint: { 'line-color': COLOR_MUN.light, 'line-width': ['interpolate', ['linear'], ['zoom'], 8, 0.6, 12, 1.4] } })
    }
    // líneas guía de los pines que se abren en abanico (1 px) y su punto de origen
    m.addSource('guias', { type: 'geojson', data: { type: 'FeatureCollection', features: [] } })
    m.addLayer({ id: 'guias-linea', type: 'line', source: 'guias', filter: ['==', '$type', 'LineString'], paint: { 'line-color': COLOR_TINTA.light, 'line-width': 1 } })
    m.addLayer({ id: 'guias-punto', type: 'circle', source: 'guias', filter: ['==', '$type', 'Point'], paint: { 'circle-radius': 2.5, 'circle-color': COLOR_TINTA.light } })
    m.addSource('puntos', { type: 'geojson', data: { type: 'FeatureCollection', features: [] } })
    m.addLayer({ id: 'puntos', type: 'circle', source: 'puntos', paint: { 'circle-radius': vivo.current.radioPuntos, 'circle-color': ['coalesce', ['get', 'color'], '#2563eb'], 'circle-stroke-width': 1.5, 'circle-stroke-color': '#ffffff' } })

    let previo: string | null = null
    m.on('mousemove', 'agebs-fill', (e) => {
      const f = e.features?.[0]; if (!f) return
      m.getCanvas().style.cursor = vivo.current.onClic ? 'pointer' : ''
      const cv = String(f.properties.cvegeo)
      if (previo && previo !== cv) m.setFeatureState({ source: 'agebs', id: previo }, { h: false })
      if (previo !== cv) m.setFeatureState({ source: 'agebs', id: cv }, { h: true })
      previo = cv
      setTip({ x: e.point.x, y: e.point.y, cv, colonia: (f.properties.colonia as string) ?? null, mun: String(f.properties.municipio) })
    })
    m.on('mouseleave', 'agebs-fill', () => {
      m.getCanvas().style.cursor = ''
      if (previo) m.setFeatureState({ source: 'agebs', id: previo }, { h: false })
      previo = null; setTip(null)
    })
    m.on('click', 'agebs-fill', (e) => {
      const f = e.features?.[0]; if (!f || !vivo.current.onClic) return
      vivo.current.onClic(String(f.properties.cvegeo), { cvegeo: String(f.properties.cvegeo), colonia: (f.properties.colonia as string) ?? null, municipio: String(f.properties.municipio) })
    })
    m.on('mousemove', 'puntos', (e) => {
      const f = e.features?.[0]; if (f?.properties?.etiqueta) setTip({ x: e.point.x, y: e.point.y, cv: '', colonia: String(f.properties.etiqueta), mun: '' })
    })
    setCapas((n) => n + 1)
  }, [listo, geo, muns])
  const [capas, setCapas] = useState(0)
  const hayCapas = capas > 0

  // fondo y líneas según el tema; mapa base OSM
  useEffect(() => {
    const m = mapa.current
    if (!m || !listo) return
    m.setPaintProperty('fondo', 'background-color', FONDO[tema])
    if (!hayCapas) return
    m.setPaintProperty('agebs-line', 'line-color', ['case', ['boolean', ['feature-state', 's'], false], COLOR_TINTA[tema], COLOR_LINEA[tema]])
    m.setPaintProperty('guias-linea', 'line-color', COLOR_TINTA[tema])
    m.setPaintProperty('guias-punto', 'circle-color', COLOR_TINTA[tema])
    if (m.getLayer('municipios-line')) m.setPaintProperty('municipios-line', 'line-color', COLOR_MUN[tema])
    m.setPaintProperty('puntos', 'circle-stroke-color', FONDO[tema])
  }, [tema, listo, hayCapas])

  useEffect(() => {
    const m = mapa.current
    if (!m || !hayCapas) return
    if (osmActivo && !m.getSource('osm')) {
      m.addSource('osm', { type: 'raster', tiles: [OSM], tileSize: 256, maxzoom: 19, attribution: '© colaboradores de OpenStreetMap' })
      m.addLayer({ id: 'osm', type: 'raster', source: 'osm' }, 'agebs-fill')
    } else if (!osmActivo && m.getSource('osm')) { m.removeLayer('osm'); m.removeSource('osm') }
    m.setPaintProperty('agebs-fill', 'fill-opacity', ['case', ['boolean', ['feature-state', 'f'], false], osmActivo ? 0.08 : 0.12, osmActivo ? 0.62 : 0.9])
  }, [osmActivo, hayCapas])

  // colores por AGEB (feature-state): solo se toca lo que cambió
  const mapaMun = useMemo(() => municipio, [municipio])
  useEffect(() => {
    const m = mapa.current
    if (!m || !geo || !hayCapas) return
    const previo = estadoPrevio.current
    for (const f of geo.features) {
      const cv = String(f.properties.cvegeo)
      let c: string
      if (categorias) c = cv in categorias ? categorica(categorias[cv], tema) : SEC_VACIO[tema]
      else c = colorDeValor(valores?.[cv], dominio, tema)
      const fuera = mapaMun ? !cv.startsWith(mapaMun) : false
      const llave = c + (fuera ? '|f' : '')
      if (previo.get(cv) !== llave) { m.setFeatureState({ source: 'agebs', id: cv }, { c, f: fuera }); previo.set(cv, llave) }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [valores, categorias, dominio[0], dominio[1], tema, geo, hayCapas, mapaMun])

  // contorno fuerte: lista resaltada + selección
  const sel = useRef<Set<string>>(new Set())
  useEffect(() => {
    const m = mapa.current
    if (!m || !hayCapas) return
    const nuevo = new Set([...(resaltar ?? []), ...(seleccion ? [seleccion] : [])])
    sel.current.forEach((cv) => { if (!nuevo.has(cv)) m.setFeatureState({ source: 'agebs', id: cv }, { s: false }) })
    nuevo.forEach((cv) => { if (!sel.current.has(cv)) m.setFeatureState({ source: 'agebs', id: cv }, { s: true }) })
    sel.current = nuevo
  }, [resaltar, seleccion, hayCapas])

  // números sobre la lista resaltada. Se dibujan del último al primero (el 1 queda encima) y los que caen a menos de 22 px
  // en pantalla se abren en abanico alrededor de su centro, con una línea guía de 1 px hacia su AGEB.
  useEffect(() => {
    const m = mapa.current
    marcadores.current.forEach((k) => k.remove()); marcadores.current = []
    const vaciarGuias = () => (m?.getSource('guias') as maplibregl.GeoJSONSource | undefined)?.setData({ type: 'FeatureCollection', features: [] } as never)
    if (!m || !geo || !resaltar?.length) { vaciarGuias(); return }
    const por = new Map(geo.features.map((f) => [String(f.properties.cvegeo), f]))
    const items: { i: number; lng: number; lat: number; k: maplibregl.Marker }[] = []
    for (let i = resaltar.length - 1; i >= 0; i--) {
      const cv = resaltar[i]; const f = por.get(cv); if (!f) continue
      const c = cajaDe(f)
      const el = document.createElement('div')
      el.className = 'c-mapa__num'; el.textContent = String(i + 1); el.title = titulo(String(f.properties.colonia ?? cv))
      el.addEventListener('click', (ev) => { ev.stopPropagation(); vivo.current.onClic?.(cv, { cvegeo: cv, colonia: (f.properties.colonia as string) ?? null, municipio: String(f.properties.municipio) }) })
      const lng = (c[0] + c[2]) / 2, lat = (c[1] + c[3]) / 2
      const k = new maplibregl.Marker({ element: el }).setLngLat([lng, lat]).addTo(m)
      items.push({ i, lng, lat, k }); marcadores.current.push(k)
    }
    const UMBRAL = 22
    const acomodar = () => {
      const pts = items.map((it) => m.project([it.lng, it.lat]))
      const grupos: number[][] = []
      items.forEach((_, a) => {
        const g = grupos.find((gr) => gr.some((b) => Math.hypot(pts[a].x - pts[b].x, pts[a].y - pts[b].y) < UMBRAL))
        if (g) g.push(a); else grupos.push([a])
      })
      const feats: unknown[] = []
      for (const g of grupos) {
        if (g.length === 1) { items[g[0]].k.setLngLat([items[g[0]].lng, items[g[0]].lat]); continue }
        const ord = [...g].sort((a, b) => items[a].i - items[b].i)  // el 1 arriba y los demás en el sentido del reloj
        const cx = g.reduce((t, a) => t + pts[a].x, 0) / g.length, cy = g.reduce((t, a) => t + pts[a].y, 0) / g.length
        const R = Math.max(24, 15 / Math.sin(Math.PI / g.length) + 2)
        ord.forEach((a, n) => {
          const ang = -Math.PI / 2 + (2 * Math.PI * n) / g.length
          const ll = m.unproject([cx + R * Math.cos(ang), cy + R * Math.sin(ang)])
          items[a].k.setLngLat(ll)
          feats.push({ type: 'Feature', properties: {}, geometry: { type: 'LineString', coordinates: [[items[a].lng, items[a].lat], [ll.lng, ll.lat]] } })
          feats.push({ type: 'Feature', properties: {}, geometry: { type: 'Point', coordinates: [items[a].lng, items[a].lat] } })
        })
      }
      ;(m.getSource('guias') as maplibregl.GeoJSONSource | undefined)?.setData({ type: 'FeatureCollection', features: feats } as never)
    }
    acomodar()
    m.on('move', acomodar)
    return () => { m.off('move', acomodar) }
  }, [resaltar, geo, hayCapas])

  // encuadre: municipio, o toda la ZMVM
  const ultimoEncuadre = useRef<{ mun: string | null; geo: GeoColeccion | null; capas: boolean; sel: string | null | undefined }>({ mun: null, geo: null, capas: false, sel: null })
  useEffect(() => {
    const m = mapa.current
    if (!m || !geo || !hayCapas) return
    // Solo encuadra cuando cambió el municipio (o llegó la geometría). Si en ese mismo momento cambió la selección,
    // manda la selección: el efecto de abajo vuela a ella y no corren dos fitBounds seguidos.
    const u = ultimoEncuadre.current
    const cambioMun = u.mun !== municipio || u.geo !== geo || u.capas !== hayCapas
    const cambioSel = u.sel !== seleccion
    ultimoEncuadre.current = { mun: municipio, geo, capas: hayCapas, sel: seleccion }
    if (!cambioMun) return
    if (cambioSel && seleccion && volarASeleccion && geo.features.some((x) => x.properties.cvegeo === seleccion)) return
    if (encuadrarResaltadas && resaltar?.length) return  // lo encuadra el efecto de las resaltadas
    const fs = municipio ? geo.features.filter((f) => String(f.properties.cvegeo).startsWith(municipio)) : geo.features
    const b = unir(fs.map(cajaDe)); if (!b) return
    m.fitBounds([[b[0], b[1]], [b[2], b[3]]], { padding: 14, duration: 700, maxZoom: 14 })
  }, [municipio, geo, hayCapas, seleccion, volarASeleccion])

  // encuadrar las AGEB resaltadas (el top de la respuesta): una sola animación, con padding para que los números no queden en el borde
  const llaveResaltadas = resaltar?.join(',') ?? ''
  useEffect(() => {
    const m = mapa.current
    if (!m || !geo || !hayCapas || !encuadrarResaltadas || !llaveResaltadas) return
    if (seleccion && volarASeleccion) return
    const por = new Set(llaveResaltadas.split(','))
    const b = unir(geo.features.filter((f) => por.has(String(f.properties.cvegeo))).map(cajaDe)); if (!b) return
    m.fitBounds([[b[0], b[1]], [b[2], b[3]]], { padding: { top: 56, bottom: sinLeyenda ? 56 : 108, left: 56, right: 56 }, duration: 700, maxZoom: zoomMaxResaltadas })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [llaveResaltadas, encuadrarResaltadas, zoomMaxResaltadas, sinLeyenda, geo, hayCapas])

  // volar a la selección
  useEffect(() => {
    const m = mapa.current
    if (!m || !geo || !seleccion || !volarASeleccion || !hayCapas) return
    const f = geo.features.find((x) => x.properties.cvegeo === seleccion); if (!f) return
    const c = cajaDe(f)
    m.fitBounds([[c[0], c[1]], [c[2], c[3]]], { padding: 90, duration: 800, maxZoom: zoomMaxSeleccion })
  }, [seleccion, volarASeleccion, zoomMaxSeleccion, geo, hayCapas])

  // capa de puntos
  useEffect(() => {
    const m = mapa.current
    const s = m?.getSource('puntos') as maplibregl.GeoJSONSource | undefined
    if (m && m.getLayer('puntos')) m.setPaintProperty('puntos', 'circle-radius', radioPuntos)
    s?.setData({ type: 'FeatureCollection', features: (puntos ?? []).map((p) => ({ type: 'Feature', properties: { color: p.color ?? null, etiqueta: p.etiqueta ?? null }, geometry: { type: 'Point', coordinates: [p.lon, p.lat] } })) } as never)
  }, [puntos, radioPuntos, hayCapas])

  const valorTip = tip?.cv ? (categorias ? (nombresCategorias?.[categorias[tip.cv]] ?? null) : valores?.[tip.cv] != null ? formatoValor(valores[tip.cv]) : null) : null
  return (
    <div className="c-mapa" style={{ height: alto }}>
      <div ref={caja} className="c-mapa__lienzo" aria-label="Mapa de la ZMVM por AGEB" />
      {sinWebgl && <div className="c-mapa__vacio">Tu navegador no pudo abrir el mapa (necesita WebGL).</div>}
      {!sinWebgl && !geo && !error && <div style={{ position: 'absolute', inset: 0 }}><Cargando forma="mapa" alto={typeof alto === 'number' ? alto : 560} /></div>}
      {error && <div style={{ position: 'absolute', inset: 0, padding: 16, background: 'var(--bg)' }}><ErrorApi error={error} reintentar={() => setReintento((n) => n + 1)} titulo="No pude cargar los polígonos del mapa" /></div>}
      {interruptorBase && (
        <div className="c-mapa__base" role="switch" aria-checked={osmActivo} aria-disabled={!hayInternet} tabIndex={0}
          title={hayInternet ? 'Dibuja las calles de OpenStreetMap debajo' : 'Sin internet: el mapa base no está disponible'}
          onClick={() => hayInternet && setBaseOSM((v) => !v)} onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && hayInternet && setBaseOSM((v) => !v)}>
          <span className="c-switch" data-on={osmActivo} />
          {hayInternet ? 'Mapa base (OpenStreetMap)' : 'Mapa base: sin internet'}
        </div>
      )}
      {tip && (
        <div className="c-mapa__tip" style={posTip(tip.x, tip.y, caja.current)}>
          <b>{!tip.colonia && tip.cv ? 'AGEB ' + tip.cv : titulo(tip.colonia)}</b>
          {tip.mun && <span>{titulo(tip.mun)}</span>}
          {valorTip != null && <div><em>{valorTip}</em></div>}
        </div>
      )}
      {!sinLeyenda && (
        <div className="c-mapa__leyenda">
          {etiqueta && <b>{etiqueta}</b>}
          {pasosLeyenda ? pasosLeyenda.map((p) => <div key={p.nombre} className="c-mapa__cat"><i style={{ background: colorDeValor(p.valor, dominio, tema) }} />{p.nombre}</div>)
            : categorias ? (nombresCategorias ?? []).map((n, i) => <div key={n} className="c-mapa__cat"><i style={{ background: categorica(i, tema) }} />{n}</div>)
            : <><div className="c-mapa__barra" style={{ background: gradienteSecuencial(tema) }} /><div className="c-mapa__ejes"><span>{formatoValor(dominio[0])}</span><span>{formatoValor(dominio[1])}</span></div></>}
        </div>
      )}
    </div>
  )
}

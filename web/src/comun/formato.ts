// Formatos es-MX: 1,234.5 · $1,234 · 63%. Todo el tablero escribe sus cifras con estas funciones.
const nf = (dec: number) => new Intl.NumberFormat('es-MX', { minimumFractionDigits: dec, maximumFractionDigits: dec })
const cache = new Map<number, Intl.NumberFormat>()
const f = (dec: number) => cache.get(dec) ?? (cache.set(dec, nf(dec)), cache.get(dec)!)
const VACIO = 'NO ENCONTRADO'

/** fmtNum(1234.5, 1) → «1,234.5». null/NaN → «NO ENCONTRADO». */
export function fmtNum(n: number | null | undefined, dec = 0): string {
  return n == null || !Number.isFinite(n) ? VACIO : f(dec).format(n)
}
/** fmtPesos(1234.5) → «$1,235»; con `compacto`: «$1.2 M» / «$3.4 mil». */
export function fmtPesos(n: number | null | undefined, dec = 0, compacto = false): string {
  if (n == null || !Number.isFinite(n)) return VACIO
  if (compacto) {
    const a = Math.abs(n)
    if (a >= 1e9) return `$${f(1).format(n / 1e9)} mil M`
    if (a >= 1e6) return `$${f(1).format(n / 1e6)} M`
    if (a >= 1e4) return `$${f(0).format(n / 1e3)} mil`
  }
  return `${n < 0 ? '−' : ''}$${f(dec).format(Math.abs(n))}`
}
/** Recibe el valor YA en porcentaje: fmtPct(63.2, 1) → «63.2%». Con fraccion=true recibe 0–1: fmtPct(0.632, 1, true) → «63.2%». */
export function fmtPct(n: number | null | undefined, dec = 0, fraccion = false): string {
  if (n == null || !Number.isFinite(n)) return VACIO
  return `${f(dec).format(fraccion ? n * 100 : n)}%`
}
/** Número compacto: 1,081,737 → «1.1 M». */
export function fmtCompacto(n: number | null | undefined, dec = 1): string {
  if (n == null || !Number.isFinite(n)) return VACIO
  const a = Math.abs(n)
  if (a >= 1e6) return `${f(dec).format(n / 1e6)} M`
  if (a >= 1e4) return `${f(0).format(n / 1e3)} mil`
  return f(0).format(n)
}

const MENORES = new Set(['de', 'del', 'la', 'las', 'el', 'los', 'y', 'e', 'en', 'a', 'al', 'con', 'por'])
// números romanos de las secciones: «Iii» → «III», «Xiii» → «XIII»
const ROMANO = /^(i{1,3}|iv|vi{0,3}|ix|x{1,3}(i{1,3}|iv|v|vi{1,3}|ix)?)$/i
// palabras frecuentes del DENUE y del Censo que llegan sin acento
const ACENTOS: Record<string, string> = {
  juarez: 'Juárez', aragon: 'Aragón', seccion: 'Sección', ampliacion: 'Ampliación', jimenez: 'Jiménez', cantu: 'Cantú', gonzalez: 'González',
  hernandez: 'Hernández', martinez: 'Martínez', perez: 'Pérez', rodriguez: 'Rodríguez', ramirez: 'Ramírez', sanchez: 'Sánchez', lopez: 'López',
  garcia: 'García', gutierrez: 'Gutiérrez', fernandez: 'Fernández', alvarez: 'Álvarez', alvaro: 'Álvaro', obregon: 'Obregón', tlahuac: 'Tláhuac',
  coyoacan: 'Coyoacán', atizapan: 'Atizapán', cuautitlan: 'Cuautitlán', chimalhuacan: 'Chimalhuacán', nezahualcoyotl: 'Nezahualcóyotl', tecamac: 'Tecámac',
  jardin: 'Jardín', mexico: 'México', mexicana: 'Mexicana', maria: 'María', jose: 'José', sebastian: 'Sebastián', andres: 'Andrés', periferico: 'Periférico',
  union: 'Unión', revolucion: 'Revolución', constitucion: 'Constitución', cooperacion: 'Cooperación', politecnico: 'Politécnico', lazaro: 'Lázaro',
  cardenas: 'Cárdenas', pantitlan: 'Pantitlán', vazquez: 'Vázquez', gomez: 'Gómez', ramon: 'Ramón', agricola: 'Agrícola', habitacion: 'Habitación',
  penon: 'Peñón', tepeyac: 'Tepeyac', republica: 'República', petroleo: 'Petróleo', electricistas: 'Electricistas', miguel: 'Miguel', ciudad: 'Ciudad',
}
function palabra(p: string, i: number, mayus: boolean): string {
  const bajo = p.toLowerCase()
  if (ROMANO.test(p) && p.length > 1) return p.toUpperCase()  // «I», «V» o «X» sueltas se dejan como vienen (podrían ser iniciales)
  if (ACENTOS[bajo] && (mayus || p === ACENTOS[bajo].normalize('NFD').replace(/[\u0300-\u036f]/g, '') || p === p[0].toUpperCase() + p.slice(1).toLowerCase())) return ACENTOS[bajo]
  if (!mayus) return p
  return i > 0 && MENORES.has(bajo) ? bajo : bajo.replace(/^(\p{L})/u, (c) => c.toUpperCase())
}
/** «FUENTES DE ARAGON» → «Fuentes de Aragón»; «Polanco Iii Sección» → «Polanco III Sección» (los datos del DENUE vienen en mayúsculas y sin acentos). Vacío → «NO ENCONTRADO». */
export function titulo(texto: string | null | undefined): string {
  if (!texto) return VACIO
  const mayus = texto === texto.toUpperCase()
  return texto.split(/(\s+)/).map((p, i) => (/^\s*$/.test(p) ? p : palabra(p, i, mayus))).join('')
}

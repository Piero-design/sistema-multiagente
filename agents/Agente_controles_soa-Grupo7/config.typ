//  CONFIGURACIÓN DEL INFORME  (aquí cambias todo, no en el texto)

// --- Portada: datos ---
#let curso    = "Auditoría de Sistemas (1704255)"
#let titulo   = "Agente de Controles y SoA para PIMS ISO/IEC 27701:2025"
#let subtitulo = "TIF – Primera Parte: De Prompt a Skill en Sistemas Multi-Agente"

#let integrantes = (
  "Ajra Huasco Jeans Anthony",
  "Gutierrez Ccama Juan Diego",
  "Suclle Suca Michael Benjamin",
  "Garambel Marín Fernando Miguel",
  "Hanco Mullisaca Sergio Danilo",
)
#let docente = "Mg. Edward Vicente Zárate Carlos"
#let lugar   = "Arequipa, Perú"
#let fecha   = "02 de Octubre de 2026"

// --- Encabezado e imágenes (aparece en todas las páginas) ---
#let facultad         = "FACULTAD DE INGENIERÍA DE PRODUCCIÓN Y SERVICIOS"
#let escuela          = "ESCUELA PROFESIONAL DE INGENIERÍA DE SISTEMAS"
#let logo-izquierdo   = "imagenes/logo-izquierdo.png"   // pon none para no usar logo
#let logo-derecho     = "imagenes/logo-derecho.png"
#let altura-logo      = 1.4cm       // tamaño/alto de los logos
#let tamano-encabezado = 7.5pt     // tamaño de fuente del texto del encabezado

// --- Posición del encabezado y separación ---
#let distancia-encabezado-arriba = 1.5cm   // distancia desde el borde superior de la hoja hasta el encabezado
#let separacion-encabezado-texto = 0.8cm // espacio libre entre el encabezado y el texto (índice, títulos, contenido)

// --- Opciones ---
#let portada            = true    // mostrar portada
#let indice             = true    // mostrar índice
#let numerar-paginas    = true
#let encabezado-paginas = true    // mostrar cabecera en todas las páginas

// --- Tipografía ---
#let fuente        = ("Times New Roman", "New Computer Modern")   // se usa la primera que exista
#let tamano        = 11pt
#let interlineado  = 0.7em
#let espacio-parrafo = 1.1em
#let justificar    = true
#let idioma        = "es"

// --- Portada: estilo ---
#let tamano-titulo-portada = 26pt
#let color-lineas-portada  = luma(140)

// --- Página y Márgenes ---
#let papel           = "a4"
#let margen-lateral  = 2cm
#let margen-inferior = 2.5cm

// --- Títulos ---
#let numeracion-titulos = "1.1"
#let ancho-numero = 1.2cm        // ancho de la columna del número; el texto se alinea aquí
#let tamano-titulos = (12pt, 11pt, 10.5pt)   // nivel 1, 2, 3
#let color-titulos  = rgb("#1f4e79")

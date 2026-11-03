//  PLANTILLA: aquí vive la lógica. Normalmente no la tocas.
#import "config.typ": *

#let informe(cuerpo) = {
  // ---------- Ajustes generales ----------
  set document(title: titulo, author: integrantes)
  // El logo se ajusta a la altura indicada respetando su proporción
  let logo(ruta, alin) = if ruta != none {
    align(alin + horizon, context {
      let m = measure(image(ruta))
      image(ruta, height: altura-logo, width: altura-logo * (m.width / m.height))
    })
  }

  let alto-cabecera = if (logo-izquierdo != none or logo-derecho != none) { altura-logo } else { 1.2em }
  let margen-superior = distancia-encabezado-arriba + alto-cabecera + separacion-encabezado-texto

  let encabezado = {
    set text(size: tamano-encabezado)
    grid(
      columns: (auto, 1fr, auto),
      column-gutter: 0.4cm,
      align: horizon,
      logo(logo-izquierdo, left),
      align(center)[
        #facultad \
        #text(weight: "bold", escuela)
      ],
      logo(logo-derecho, right),
    )
  }

  set page(
    paper: papel,
    margin: (
      x: margen-lateral,
      top: margen-superior,
      bottom: margen-inferior,
    ),
    header-ascent: separacion-encabezado-texto,
    header: if encabezado-paginas { encabezado } else { none },
    numbering: if numerar-paginas { "1" } else { none },
  )
  set text(font: fuente, size: tamano, lang: idioma)
  set par(justify: justificar, leading: interlineado, spacing: espacio-parrafo)

  // ---------- Títulos con sangría francesa ----------
  set heading(numbering: numeracion-titulos)
  show heading: it => {
    let tam = tamano-titulos.at(calc.min(it.level, tamano-titulos.len()) - 1)
    let num = if it.numbering != none {
      counter(heading).display(it.numbering)
    } else { none }
    // Cada nivel empieza una columna más adentro que el anterior.
    let estilo(x) = text(size: tam, weight: "bold", fill: color-titulos, x)
    if num == none {
      // Título sin número (por ejemplo «Índice»): empieza en el margen, sin columna vacía
      block(above: 1.6em, below: 1em, sticky: true, estilo(it.body))
    } else {
      // Cada nivel empieza una columna más adentro que el anterior.
      pad(left: (it.level - 1) * ancho-numero, block(
        width: 100%,
        above: 1.6em,
        below: 1em,
        sticky: true,
        grid(
          columns: (ancho-numero, 1fr),
          column-gutter: 0pt,
          estilo(num),
          estilo(it.body),
        ),
      ))
    }
  }

  // ---------- Portada ----------
  if portada {
    let etiqueta(t) = text(weight: "bold", size: 12pt, t)
    let campo(nombre, valor) = block(above: 0pt, below: 1.4em, breakable: false)[
      #etiqueta(nombre) \
      #if type(valor) == array { valor.join(linebreak()) } else { valor }
    ]
    let linea = line(length: 100%, stroke: 0.6pt + color-lineas-portada)

    page(numbering: none, {
      set par(justify: false, leading: 0.6em, spacing: 0.6em)
      set text(size: 12pt)

      v(1fr)

      // Bloque del título
      linea
      v(0.5cm)
      text(style: "italic", curso)
      v(0.2cm)
      par(leading: 1em, text(size: tamano-titulo-portada, weight: "bold", upper(titulo)))
      if subtitulo != none {
        v(0.1cm)
        text(style: "italic", subtitulo)
      }
      v(0.5cm)
      linea

      v(1.2cm)

      // Datos
      campo(if integrantes.len() > 1 { "AUTORES:" } else { "AUTOR:" }, integrantes)
      campo("DOCENTE:", docente)
      campo("CURSO:", curso)
      campo("LUGAR:", lugar)
      campo("FECHA:", fecha)

      v(1.4fr)
    })
    counter(page).update(1)
  }

  // ---------- Índice ----------
  if indice {
    page(numbering: none)[
      #outline(title: "Índice", indent: auto)
    ]
    counter(page).update(1)
  }

  // ---------- Contenido: el texto se sangra según el nivel del último título ----------
  // Se aplana el contenido en una lista de elementos.
  let aplanar(c) = if c.has("children") {
    c.children.map(aplanar).flatten()
  } else { (c,) }

  let items = aplanar(cuerpo)
  let bloque = ()      // texto acumulado bajo el título actual
  let nivel = 0

  let vaciar(bloque, nivel) = {
    if bloque.len() > 0 {
      pad(left: nivel * ancho-numero, bloque.join())
    }
  }

  for c in items {
    if c.func() == heading {
      vaciar(bloque, nivel)
      bloque = ()
      nivel = c.depth
      c
    } else {
      bloque.push(c)
    }
  }
  vaciar(bloque, nivel)
}

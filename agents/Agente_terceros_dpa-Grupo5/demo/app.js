/* =============================================================================
   app.js — Demo web del Agente 7 (Terceros/DPA) del PIMS Privacy Guard
   -----------------------------------------------------------------------------
   Envía SKILL.md (como system prompt) y el contrato pegado por el usuario a
   servidor_demo.py, que lanza el CLI de Claude Code con la suscripción del
   usuario (sin API Key) y devuelve su salida como Server-Sent Events.

   Los textos embebidos (SKILL.md, archivos de referencia y los 3 contratos de
   prueba) viven en `corpus.js`, que genera `build_embed.py` a partir de los
   archivos reales del proyecto.
   ========================================================================== */

'use strict';

/* ---------------------------------------------------------------------------
   Configuración
   ------------------------------------------------------------------------- */

const CONFIG = {
  // Modelo evaluador. `claude-sonnet-4-6` es el pedido para esta demo.
  // El Sonnet de generación actual es `claude-sonnet-5-5`: basta cambiar
  // esta línea para usarlo.
  modelo: 'claude-sonnet-4-6',

  // Endpoint del servidor local (servidor_demo.py), que lanza el CLI de
  // Claude Code en modo headless y reemite su salida como Server-Sent Events.
  // No hay API Key: la inferencia va por la suscripción del usuario.
  endpoint: '/api/auditar',

  // Cada cuántos ms se vuelve a renderizar el Markdown mientras llega el stream.
  msRefresco: 150,
};

/* ---------------------------------------------------------------------------
   System prompt
   ------------------------------------------------------------------------- */

/**
 * SKILL.md manda leer archivos de `references/` y `assets/` en pasos concretos
 * y ejecutar `scripts/calcular_resultado.py` en el Paso 8. En el navegador no
 * hay disco ni intérprete de Python, así que:
 *   - los archivos de referencia se entregan ya cargados, y
 *   - se activa la vía manual que el propio Paso 8 contempla
 *     (`trazabilidad.calculo: "manual"`).
 */
function construirSystemPrompt() {
  const c = window.PIMS_CORPUS;

  const referencias = c.referencias
    .map((r) => `### Archivo: ${r.ruta}\n\n${r.contenido}`)
    .join('\n\n---\n\n');

  return [
    c.skill_md,

    '---',

    '# Archivos de la skill (ya cargados en este contexto)',
    '',
    'Los archivos que el flujo de trabajo te indica leer están incluidos a',
    'continuación. Úsalos como fuente y no intentes leerlos del disco: esta',
    'ejecución corre en un navegador y no tiene acceso al sistema de archivos.',
    '',
    referencias,

    '---',

    '# Entorno de esta ejecución',
    '',
    '- No puedes ejecutar código. Por lo tanto, en el **Paso 8** aplica a mano',
    '  las fórmulas de `references/criterios_semaforo.md` §5 (dictamen) y §8',
    '  (puntaje), tal como el propio paso contempla, y registra',
    '  `trazabilidad.calculo: "manual"`. Muestra el cálculo del puntaje en la',
    '  sección 7 del informe (base, penalización y total) para que sea auditable.',
    '- No puedes calcular el hash SHA-256 del documento: deja',
    '  `contrato.hash_documento_sha256` en `null` con el supuesto correspondiente.',
    '- Entrega primero el **informe en Markdown** con las 11 secciones exactas y,',
    '  al final, el **JSON** del registro en un bloque de código ```json.',
    '- Escribe en español, con el tono corporativo y preventivo de la skill.',
  ].join('\n');
}

/* ---------------------------------------------------------------------------
   Referencias al DOM
   ------------------------------------------------------------------------- */

const el = {
  contrato:     document.getElementById('contrato'),
  proveedor:    document.getElementById('proveedor'),
  btnAuditar:   document.getElementById('btnAuditar'),
  btnDescargar: document.getElementById('btnDescargar'),
  zonaDescarga: document.getElementById('zonaDescarga'),
  informe:      document.getElementById('informe'),
  vacio:        document.getElementById('vacio'),
  cargando:     document.getElementById('cargando'),
  estadoCarga:  document.getElementById('estadoCarga'),
  error:        document.getElementById('error'),
  meta:         document.getElementById('meta'),
  botonesCaso:  Array.from(document.querySelectorAll('.btn-caso')),
};

/* Estado de la ejecución en curso */
const estado = {
  markdown: '',
  enCurso: false,
  proveedor: '',
};

/* ---------------------------------------------------------------------------
   Carga rápida de los contratos de prueba
   ------------------------------------------------------------------------- */

el.botonesCaso.forEach((boton) => {
  boton.addEventListener('click', () => {
    const caso = window.PIMS_CORPUS.contratos[boton.dataset.caso];
    if (!caso) return;

    el.contrato.value = caso.texto;
    el.proveedor.value = caso.proveedor;

    el.botonesCaso.forEach((b) => b.classList.toggle('activo', b === boton));
    el.contrato.scrollTop = 0;
  });
});

/* Si el usuario edita el texto a mano, deja de estar "activo" un caso de prueba */
el.contrato.addEventListener('input', () => {
  el.botonesCaso.forEach((b) => b.classList.remove('activo'));
});

/* ---------------------------------------------------------------------------
   Render del informe
   ------------------------------------------------------------------------- */

/**
 * Los emoji del semáforo (🟢🟡🔴⚪➖) son glifos con color propio: CSS no puede
 * recolorearlos ni ajustarlos a la paleta. Se sustituyen por glifos de texto
 * (●, ○, –) que sí toman el color del token correspondiente, conservando el
 * nombre del estado en `title`.
 */
const SEMAFORO = [
  ['🟢', 'sem-verde',    '●', 'Cumple'],
  ['🟡', 'sem-amarillo', '●', 'Parcial'],
  ['🔴', 'sem-rojo',     '●', 'No cumple'],
  ['⚪', 'sem-blanco',    '○', 'Sin evidencia'],
  ['➖', 'sem-gris',      '–', 'No aplica'],
];

/**
 * Convierte los iconos del semáforo en marcas con la paleta de la página, pero
 * solo fuera de los bloques de código (para no inyectar etiquetas HTML dentro
 * del JSON del registro).
 */
function colorearSemaforo(markdown) {
  return markdown
    .split('```')
    .map((trozo, i) => {
      if (i % 2 === 1) return trozo; // dentro de un bloque de código
      let salida = trozo;
      for (const [emoji, clase, glifo, estado] of SEMAFORO) {
        salida = salida.split(emoji).join(`<i class="sem ${clase}" title="${estado}">${glifo}</i>`);
      }
      return salida;
    })
    .join('```');
}

function renderizar(conCursor) {
  const html = DOMPurify.sanitize(
    marked.parse(colorearSemaforo(estado.markdown), { gfm: true, breaks: false })
  );
  el.informe.innerHTML = conCursor ? html + '<span class="cursor"></span>' : html;
  if (!conCursor) marcarCeldasDeControl();
}

/**
 * Marca las celdas que contienen un identificador de control (A.1.2.7, A.2.5.9,
 * A.3.10...) para darles tipografía monoespaciada. Se aplica por contenido y no
 * con `td:first-child`, porque en las otras tablas del informe la primera
 * columna lleva prosa que debe poder partirse en varias líneas.
 */
function marcarCeldasDeControl() {
  const celdas = el.informe.querySelectorAll
    ? el.informe.querySelectorAll('td:first-child')
    : [];
  for (const celda of celdas) {
    if (/^A\.[123]\.[0-9]+(\.[0-9]+)?$/.test(celda.textContent.trim())) {
      celda.classList.add('celda-control');
    }
  }
}

/* ---------------------------------------------------------------------------
   Mensajes de estado y de error
   ------------------------------------------------------------------------- */

function mostrarError(titulo, detalle) {
  el.error.innerHTML = '';

  const fuerte = document.createElement('strong');
  fuerte.textContent = titulo;
  el.error.appendChild(fuerte);

  if (detalle) {
    const codigo = document.createElement('code');
    codigo.textContent = detalle;
    el.error.appendChild(codigo);
  }

  el.error.hidden = false;
  el.vacio.hidden = true;
}

function limpiarError() {
  el.error.hidden = true;
  el.error.innerHTML = '';
}

function fijarEstadoCarga(texto) {
  el.estadoCarga.textContent = texto;
}

/**
 * La inferencia va por la suscripción a través del CLI, no por API Key: no hay
 * costo por token que mostrar. La meta informa del modelo, del esfuerzo de
 * razonamiento y de cuánto tardó la auditoría.
 */
function fijarMeta({ modelo, tokensRazonamiento, segundos, turnos }) {
  const partes = [modelo || CONFIG.modelo];
  if (tokensRazonamiento) {
    const miles = tokensRazonamiento >= 1000
      ? (tokensRazonamiento / 1000).toFixed(1) + 'K'
      : String(tokensRazonamiento);
    partes.push(`${miles} tokens de razonamiento`);
  }
  if (segundos) partes.push(`${segundos.toFixed(0)} s`);
  if (turnos) partes.push(`${turnos} ${turnos === 1 ? 'turno' : 'turnos'}`);
  partes.push('suscripción · sin API Key');
  el.meta.textContent = partes.join(' · ');
}

/* ---------------------------------------------------------------------------
   Llamada a la API (streaming SSE)
   ------------------------------------------------------------------------- */

async function auditar() {
  if (estado.enCurso) return;

  const contrato = el.contrato.value.trim();
  const proveedor = el.proveedor.value.trim();

  if (location.protocol === 'file:') {
    mostrarError(
      'Esta demo necesita el servidor local.',
      'Abierta como file:// no hay a quién pedirle la auditoría. Ejecuta ' +
      '"python servidor_demo.py" dentro de project/demo/ y abre http://localhost:8000/.'
    );
    return;
  }
  if (!contrato) {
    mostrarError('Falta el contrato.', 'Pega el texto del DPA o usa un botón de carga rápida.');
    el.contrato.focus();
    return;
  }

  /* --- Preparar la UI --- */
  estado.enCurso = true;
  estado.markdown = '';
  estado.proveedor = proveedor;
  el.btnAuditar.disabled = true;
  el.btnAuditar.textContent = 'Auditando...';
  el.zonaDescarga.hidden = true;
  el.informe.innerHTML = '';
  el.vacio.hidden = true;
  el.cargando.hidden = false;
  limpiarError();
  fijarEstadoCarga('Lanzando el Agente 7 en Claude Code...');
  fijarMeta({});

  let tokensRazonamiento = 0;
  let modeloUsado = CONFIG.modelo;
  let motivoParada = null;
  let refresco = null;
  const arranque = Date.now();

  try {
    const respuesta = await fetch(CONFIG.endpoint, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({
        // El system prompt lo sigue construyendo construirSystemPrompt(): el
        // servidor local lo escribe a un archivo temporal y lo pasa con
        // --append-system-prompt-file, porque como argumento no cabría
        // (43 000 caracteres contra el límite de 32 767 de Windows).
        system: construirSystemPrompt(),
        contrato,
        proveedor,
        modelo: CONFIG.modelo,
      }),
    });

    if (!respuesta.ok) {
      const cuerpo = await respuesta.text();
      let detalle = cuerpo.slice(0, 500);
      try {
        const json = JSON.parse(cuerpo);
        if (json.error) detalle = json.error;
      } catch (_) { /* el cuerpo no era JSON: se muestra tal cual */ }

      const titulos = {
        404: 'El servidor local no reconoce /api/auditar.',
        409: 'Ya hay una auditoría en curso.',
        413: 'El contrato es demasiado largo para el servidor local.',
        500: 'El servidor local falló al lanzar el CLI.',
      };
      throw new Error(
        (titulos[respuesta.status] || `El servidor local respondió ${respuesta.status}.`) +
        '\u0000' + detalle
      );
    }

    /* --- Refresco periódico del Markdown mientras llega el stream --- */
    refresco = setInterval(() => {
      if (estado.markdown) renderizar(true);
    }, CONFIG.msRefresco);

    /* --- Lectura del stream de Server-Sent Events --- */
    const lector = respuesta.body.getReader();
    const decodificador = new TextDecoder();
    const tiposBloque = {};
    let bufer = '';

    for (;;) {
      const { done, value } = await lector.read();
      if (done) break;

      bufer += decodificador.decode(value, { stream: true });
      const trozos = bufer.split('\n\n');
      bufer = trozos.pop();

      for (const trozo of trozos) {
        const datos = trozo
          .split('\n')
          .filter((l) => l.startsWith('data:'))
          .map((l) => l.slice(5).trim())
          .join('');

        if (!datos) continue;

        let sobre;
        try {
          sobre = JSON.parse(datos);
        } catch (_) {
          continue; // línea incompleta o no-JSON
        }

        /* El CLI envuelve los eventos de la API dentro de `stream_event`, y
           añade sus propios eventos de sesión. Primero el sobre del CLI. */
        if (sobre.type === 'system') {
          if (sobre.subtype === 'init') {
            modeloUsado = sobre.model || modeloUsado;
            fijarEstadoCarga('Cargando la skill y los criterios del semáforo...');
            fijarMeta({ modelo: modeloUsado });
          } else if (sobre.subtype === 'thinking_tokens') {
            tokensRazonamiento = sobre.estimated_tokens || tokensRazonamiento;
            fijarEstadoCarga('Analizando los 26 controles ISO/IEC 27701...');
            fijarMeta({ modelo: modeloUsado, tokensRazonamiento });
          }
          continue;
        }

        if (sobre.type === 'result') {
          motivoParada = sobre.stop_reason || motivoParada;
          fijarMeta({
            modelo: modeloUsado,
            tokensRazonamiento,
            segundos: (sobre.duration_ms || 0) / 1000,
            turnos: sobre.num_turns,
          });
          if (sobre.subtype && sobre.subtype !== 'success' && !estado.markdown.trim()) {
            throw new Error(
              `El agente terminó con subtype "${sobre.subtype}".\u0000` +
              (sobre.result || JSON.stringify(sobre).slice(0, 400))
            );
          }
          continue;
        }

        if (sobre.type === 'shim_error') {
          throw new Error('El servidor local falló.\u0000' + (sobre.mensaje || ''));
        }

        if (sobre.type === 'shim_fin') {
          if (sobre.codigo !== 0 && !estado.markdown.trim()) {
            throw new Error(
              `El CLI terminó con código ${sobre.codigo}.\u0000` + (sobre.stderr || '')
            );
          }
          continue;
        }

        if (sobre.type !== 'stream_event') continue;

        /* Dentro de `stream_event` viene el evento tal cual lo emite la API,
           así que el tratamiento es el mismo de siempre. */
        const ev = sobre.event || {};

        switch (ev.type) {
          case 'content_block_start':
            tiposBloque[ev.index] = ev.content_block && ev.content_block.type;
            if (tiposBloque[ev.index] === 'thinking') {
              fijarEstadoCarga('Analizando los 26 controles ISO/IEC 27701...');
            } else if (tiposBloque[ev.index] === 'text') {
              fijarEstadoCarga('Redactando el informe de 11 secciones...');
            }
            break;

          case 'content_block_delta':
            if (ev.delta && ev.delta.type === 'text_delta') {
              estado.markdown += ev.delta.text;
            }
            break;

          case 'message_delta':
            if (ev.delta && ev.delta.stop_reason) motivoParada = ev.delta.stop_reason;
            break;

          case 'error':
            throw new Error(
              'El modelo interrumpió el stream.\u0000' +
              ((ev.error && ev.error.message) || JSON.stringify(ev.error || {}))
            );

          default:
            break;
        }
      }
    }

    clearInterval(refresco);
    refresco = null;

    /* --- Cierre --- */
    if (!estado.markdown.trim()) {
      if (motivoParada === 'refusal') {
        mostrarError(
          'El modelo declinó procesar esta solicitud.',
          'Revisa el contenido del contrato y vuelve a intentarlo.'
        );
      } else {
        mostrarError('La respuesta llegó vacía.', `stop_reason: ${motivoParada || 'desconocido'}`);
      }
    } else {
      renderizar(false);
      el.zonaDescarga.hidden = false;

      if (motivoParada === 'max_tokens') {
        mostrarError(
          'El informe se cortó antes de terminar.',
          'El agente alcanzó su tope de salida. Vuelve a auditar; si se repite, ' +
          'revisa el límite de contexto de la sesión.'
        );
      }
    }

    fijarMeta({
      modelo: modeloUsado,
      tokensRazonamiento,
      segundos: (Date.now() - arranque) / 1000,
    });
  } catch (err) {
    if (refresco) clearInterval(refresco);

    if (err instanceof TypeError) {
      // fetch lanza TypeError si el servidor local no está escuchando.
      mostrarError(
        'No hay respuesta del servidor local.',
        'Comprueba que "python servidor_demo.py" sigue corriendo en project/demo/ ' +
        'y que abriste la página en http://localhost:8000/. Detalle: ' + err.message
      );
    } else {
      const [titulo, detalle] = String(err.message).split('\u0000');
      mostrarError(titulo, detalle);
    }

    // Si alcanzó a llegar texto parcial, se muestra igual: es útil en una demo.
    if (estado.markdown.trim()) {
      renderizar(false);
      el.zonaDescarga.hidden = false;
    }
  } finally {
    estado.enCurso = false;
    el.cargando.hidden = true;
    el.btnAuditar.disabled = false;
    el.btnAuditar.textContent = '🔍 Auditar DPA';
    if (!estado.markdown.trim() && el.error.hidden) el.vacio.hidden = false;
  }
}

/* ---------------------------------------------------------------------------
   Descarga del informe
   ------------------------------------------------------------------------- */

function descargar() {
  if (!estado.markdown.trim()) return;

  const fecha = new Date().toISOString().slice(0, 10);
  const nombre = (estado.proveedor || 'proveedor')
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')   // quita acentos
    .replace(/[^A-Za-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '')
    .slice(0, 50) || 'proveedor';

  const blob = new Blob([estado.markdown], { type: 'text/markdown;charset=utf-8' });
  const url = URL.createObjectURL(blob);

  const enlace = document.createElement('a');
  enlace.href = url;
  enlace.download = `informe_DPA_${nombre}_${fecha}.md`;
  document.body.appendChild(enlace);
  enlace.click();
  document.body.removeChild(enlace);

  URL.revokeObjectURL(url);
}

/* ---------------------------------------------------------------------------
   Arranque
   ------------------------------------------------------------------------- */

el.btnAuditar.addEventListener('click', auditar);
el.btnDescargar.addEventListener('click', descargar);

// Ctrl/Cmd + Enter desde el textarea lanza la auditoría.
el.contrato.addEventListener('keydown', (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
    e.preventDefault();
    auditar();
  }
});

// Abierta como file:// no hay servidor local al que pedir la auditoría.
if (location.protocol === 'file:') {
  mostrarError(
    'Esta demo necesita el servidor local.',
    'Ejecuta "python servidor_demo.py" dentro de project/demo/ y abre ' +
    'http://localhost:8000/ en lugar de abrir el archivo directamente.'
  );
  el.btnAuditar.disabled = true;
}

// Comprobación de que el corpus embebido se cargó.
if (!window.PIMS_CORPUS || !window.PIMS_CORPUS.skill_md) {
  mostrarError(
    'No se cargó corpus.js.',
    'Genera el archivo con: python build_embed.py (dentro de project/demo/).'
  );
  el.btnAuditar.disabled = true;
}

#!/usr/bin/env python3
"""
probar_pagina.py — Recorre la página en un navegador real (Chromium con Playwright) contra n8n.

    python web/pruebas/probar_pagina.py --raiz <COPIA del proyecto> [--n8n http://localhost:5678]
           [--chromium /ruta/a/chrome] [--capturas carpeta]

Requisitos: n8n con los flujos instalados, el modelo simulado configurado
(n8n/pruebas/modelo_simulado.py + proveedor "ollama" apuntando a él) y `pip install playwright`.
Crea expedientes y aprobaciones de prueba: úsalo sobre una COPIA del proyecto.
"""
import argparse
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

RES = []


def paso(nombre, fn):
    try:
        d = fn()
        RES.append((True, nombre, d or ""))
    except Exception as e:  # noqa: BLE001
        RES.append((False, nombre, f"{type(e).__name__}: {str(e)[:400]}"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", required=True)
    ap.add_argument("--n8n", default="http://localhost:5678")
    ap.add_argument("--chromium")
    ap.add_argument("--capturas", default="capturas_pagina")
    a = ap.parse_args()
    raiz = Path(a.raiz)
    cap = Path(a.capturas); cap.mkdir(parents=True, exist_ok=True)
    contrato = (raiz / "pims-dpa-auditor_pruebas/contratos/dpa_nubeandina.md").read_text(encoding="utf-8")

    # Un .docx real para probar la conversión en el navegador (mammoth servido por n8n)
    import docx
    d = docx.Document()
    for linea in (raiz / "pims-dpa-auditor_pruebas/contratos/dpa_andescloud_bueno.md").read_text(encoding="utf-8").splitlines():
        d.add_paragraph(linea.replace("**", "").lstrip("# "))
    ruta_docx = cap / "Contrato AndesCloud.docx"
    d.save(ruta_docx)

    errores_consola = []
    with sync_playwright() as p:
        nav = p.chromium.launch(executable_path=a.chromium) if a.chromium else p.chromium.launch()
        pg = nav.new_page(viewport={"width": 1366, "height": 900}, accept_downloads=True)
        pg.on("console", lambda m: errores_consola.append(m.text) if m.type == "error" else None)
        pg.on("pageerror", lambda e: errores_consola.append(f"pageerror: {e}"))
        url = f"{a.n8n}/webhook/pims/app"

        def abrir():
            pg.goto(url)
            pg.wait_for_selector("#f-auditar", timeout=20000)
            opciones = pg.eval_on_selector_all("#org option", "els => els.map(e => e.value)")
            assert "inversiones_altiplano" in opciones, opciones
            pg.select_option("#org", "inversiones_altiplano")
            pg.fill("#usuario", "Luis Pérez")
            pg.screenshot(path=str(cap / "01_auditar.png"), full_page=True)
            return f"{len(opciones)} organizaciones en el selector"
        paso("La página carga desde n8n (sandbox) y lista las organizaciones", abrir)

        estado = {}

        def auditar_texto():
            pg.fill("#a-proveedor", "NubeAndina Contact Services S.A.C.")
            pg.fill("#a-texto", contrato)
            pg.click("#a-enviar")
            pg.wait_for_selector("#a-panel .progreso", timeout=15000)
            pg.screenshot(path=str(cap / "02_progreso.png"), full_page=True)
            pg.wait_for_selector("#a-panel button:has-text('Abrir expediente')", timeout=180000)
            pg.click("#a-panel button:has-text('Abrir expediente')")
            pg.wait_for_selector(".huella .casilla", timeout=20000)
            n = pg.eval_on_selector_all(".huella .casilla", "els => els.length")
            valor = pg.inner_text(".cifra .v")
            assert n == 26 and valor.startswith("22"), (n, valor)
            pg.wait_for_selector(".informe h2")
            pg.screenshot(path=str(cap / "03_expediente.png"), full_page=True)
            estado["vista"] = pg.inner_text("main h1")
            return f"26 casillas · puntaje {valor.splitlines()[0]}"
        paso("Auditar pegando el texto → progreso → expediente con huella y 22/100", auditar_texto)

        def aprobar():
            pg.fill("#d-com", "Aprobado sujeto a las enmiendas de la sección 8")
            pg.click("#d-ok")
            pg.wait_for_selector(".sello.puesto", timeout=20000)
            assert "APROBADO" in pg.inner_text(".sellos")
            pg.screenshot(path=str(cap / "04_sello_dpo.png"), full_page=False)
            assert pg.query_selector("#d-ok") is None, "el DPO no debería poder decidir dos veces"
            pg.click(".roles button[data-rol='Legal']")
            pg.fill("#usuario", "Ana Torres")
            pg.wait_for_selector("#d-ok", timeout=5000)
            pg.click("#d-ok")
            pg.wait_for_function("document.querySelectorAll('.sello.puesto').length === 2", timeout=20000)
            pg.click(".pestanas button[data-p='historial']")
            filas = pg.eval_on_selector_all("#x-cuerpo tbody tr", "els => els.length")
            assert filas == 2, filas
            pg.screenshot(path=str(cap / "05_aprobado_dos_sellos.png"), full_page=False)
            return "DPO y Legal aprobaron; historial con 2 decisiones"
        paso("Doble puerta: el DPO estampa su sello, luego Legal; historial", aprobar)

        def descargas():
            pg.click(".pestanas button[data-p='informe']")
            with pg.expect_download() as d1:
                pg.click("#x-md")
            md = Path(d1.value.path()).read_text(encoding="utf-8")
            assert "Valores calculados por n8n" in md
            with pg.expect_download() as d2:
                pg.click("#x-json")
            assert '"puntaje_proveedor"' in Path(d2.value.path()).read_text(encoding="utf-8")
            return f"{d1.value.suggested_filename} y {d2.value.suggested_filename}"
        paso("Descargar informe (.md) y registro (.json) desde el sandbox", descargas)

        def chat_expediente():
            pg.click(".pestanas button[data-p='chat']")
            pg.wait_for_selector(".chat .chat-sugerencias button", timeout=10000)
            pg.click(".chat .chat-sugerencias button >> nth=0")
            pg.wait_for_selector(".msg.asistente:not(.pensando) >> text=Respuesta simulada (expediente)", timeout=60000)
            pg.fill(".chat-form textarea", "¿Qué cláusula le pido al proveedor?")
            pg.press(".chat-form textarea", "Control+Enter")
            pg.wait_for_function("document.querySelectorAll('.chat .msg:not(.pensando)').length === 4", timeout=60000)
            assert "Mensajes previos del usuario: 1" in pg.inner_text(".chat-lista")
            pg.screenshot(path=str(cap / "11_chat_expediente.png"), full_page=False)
            # Al volver al expediente, la conversación sigue ahí (la guarda n8n)
            pg.click(".pestanas button[data-p='informe']")
            pg.click(".pestanas button[data-p='chat']")
            pg.wait_for_function("document.querySelectorAll('.chat .msg').length === 4", timeout=10000)
            return "2 preguntas; la conversación persiste"
        paso("Chat del expediente: sugerencia, pregunta con Ctrl+Enter e historial", chat_expediente)

        def docx_y_bandeja():
            pg.click(".roles button[data-rol='DPO']")
            pg.select_option("#org", "altiplano_perfil")
            pg.click("#nav button[data-vista='auditar']")
            pg.set_input_files("#a-archivo", str(ruta_docx))
            pg.wait_for_function("document.querySelector('#a-texto').value.includes('AndesCloud')", timeout=20000)
            pg.click("#a-enviar")
            pg.wait_for_selector("#a-panel button:has-text('Abrir expediente')", timeout=180000)
            pg.click("#nav button[data-vista='bandeja']")
            pg.wait_for_selector("tr.clic", timeout=10000)
            pg.screenshot(path=str(cap / "06_bandeja_dpo.png"), full_page=True)
            pg.click("tr.clic")
            pg.wait_for_selector(".huella .casilla")
            valor = pg.inner_text(".cifra .v")
            assert valor.startswith("100"), valor
            return "docx convertido en el navegador → AndesCloud 100/100 en la bandeja del DPO"
        paso("Subir un .docx (mammoth vía n8n), auditar y verlo en la bandeja del DPO", docx_y_bandeja)

        def organizacion():
            pg.select_option("#org", "altiplano_docs")
            pg.click("#nav button[data-vista='organizacion']")
            pg.wait_for_selector("#o-generar", timeout=20000)
            pg.click("#o-generar")
            pg.wait_for_selector("text=Perfil generado", timeout=180000)
            pg.wait_for_selector("#o-validar:not([disabled])", timeout=20000)
            pg.click("#o-validar")
            pg.wait_for_selector(".estado.aprobado", timeout=20000)
            pg.click("details summary:has-text('Ver el perfil completo')")
            pg.screenshot(path=str(cap / "07_organizacion_perfil.png"), full_page=True)
            pg.fill("#o-chat textarea", "¿Qué proveedores tienen riesgo alto?")
            pg.click("#o-chat button[type=submit]")
            pg.wait_for_selector("#o-chat .msg.asistente:not(.pensando) >> text=Respuesta simulada (organizacion)", timeout=60000)
            return pg.inner_text(".estado.aprobado") + " · chat de la organización respondió"
        paso("Organización: generar perfil, validarlo como DPO y preguntar en el chat", organizacion)

        def crear_org():
            oid = f"pagina_{int(time.time()) % 100000}"
            pg.click("details summary:has-text('Crear otra organización')")
            pg.fill("#o-nueva input[name=nombre]", "Organización creada desde la página")
            pg.fill("#o-nueva input[name=id]", oid)
            pg.fill("#o-nueva input[name=cargo_dpo]", "Oficial de Datos Personales")
            pg.click("#o-nueva button[type=submit]")
            pg.wait_for_function(f"document.querySelector('#org').value === '{oid}'", timeout=20000)
            pg.set_input_files("#o-archivos", str(raiz / "pims-dpa-auditor_pruebas/organizaciones_prueba/altiplano_con_perfil/documentos/D1_rof_altiplano.md"))
            pg.wait_for_selector("text=D1_rof_altiplano.md", timeout=20000)
            return oid
        paso("Crear una organización y subirle un documento", crear_org)

        def renov_config():
            pg.select_option("#org", "inversiones_altiplano")
            pg.click("#nav button[data-vista='renovaciones']")
            pg.wait_for_selector("main .hoja table, main .vacio", timeout=20000)
            pg.screenshot(path=str(cap / "08_renovaciones.png"), full_page=True)
            pg.click("#nav button[data-vista='configuracion']")
            pg.wait_for_selector("#c-form")
            pg.select_option("#c-form select[name=proveedor]", "anthropic")
            assert pg.is_visible("#c-form input[name=api_key]") and not pg.is_visible("#c-form input[name=url_ollama]")
            pg.select_option("#c-form select[name=proveedor]", "ollama")
            pg.fill("#c-form input[name=modelo]", "modelo-simulado")
            pg.click("#c-form button[type=submit]")
            pg.wait_for_selector("text=Configuración guardada", timeout=10000)
            pg.screenshot(path=str(cap / "09_configuracion.png"), full_page=True)
            pg.set_viewport_size({"width": 390, "height": 844})
            pg.click("#nav button[data-vista='expedientes']")
            pg.wait_for_selector("tr.clic")
            pg.screenshot(path=str(cap / "10_movil_expedientes.png"), full_page=False)
            ancho = pg.evaluate("document.documentElement.scrollWidth")
            return f"ancho en móvil: {ancho}px"
        paso("Renovaciones, configuración del modelo y vista móvil", renov_config)

        # Sin conexión a internet la fuente de Google Fonts no carga: no es un error de la página (usa la fuente del sistema).
        RED = ("ERR_TUNNEL_CONNECTION_FAILED", "ERR_NAME_NOT_RESOLVED", "ERR_INTERNET_DISCONNECTED", "ERR_PROXY_CONNECTION_FAILED")
        reales = [e for e in errores_consola if not any(r in e for r in RED)]
        paso("Sin errores de JavaScript en la consola",
             lambda: (_ for _ in ()).throw(AssertionError("; ".join(reales[:5]))) if reales
             else f"0 errores ({len(errores_consola) - len(reales)} avisos de red por la fuente externa)")
        nav.close()

    ok = sum(1 for r in RES if r[0])
    print(f"\nPruebas de la página (Chromium + n8n)\n{'=' * 38}")
    for bien, n, d in RES:
        print(f"[{'OK  ' if bien else 'FALLA'}] {n}" + (f"\n         {d}" if d else ""))
    print(f"\n{ok}/{len(RES)} correctas · capturas en {cap}")
    sys.exit(0 if ok == len(RES) else 1)


if __name__ == "__main__":
    main()

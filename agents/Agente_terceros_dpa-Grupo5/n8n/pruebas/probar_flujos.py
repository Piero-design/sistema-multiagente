#!/usr/bin/env python3
"""
probar_flujos.py — Pruebas de extremo a extremo de los flujos de n8n con el MODELO SIMULADO.

Requisitos (ver n8n/INSTALACION_N8N.md, sección "Probar sin modelo"):
  1. n8n corriendo con los 11 flujos importados y publicados (construidos con --raiz <RAIZ>).
  2. python n8n/pruebas/modelo_simulado.py --puerto 11435      (en otra terminal)
  3. Para probar Claude Code: un ejecutable llamado `claude` que ejecute claude_simulado.py,
     o la opción --sin-claude para omitir ese proveedor.

    python n8n/pruebas/probar_flujos.py --raiz <RAIZ> [--n8n http://localhost:5678] [--sin-claude]

ATENCIÓN: crea registros, trabajos y organizaciones de prueba dentro de <RAIZ>. Úsalo sobre
una COPIA del proyecto, no sobre la carpeta con datos reales.
"""
import argparse
import hashlib
import json
import sys
import time
import urllib.error
import urllib.request
import zlib
from pathlib import Path

A = None
RES = []


def http(metodo, ruta, cuerpo=None):
    datos = json.dumps(cuerpo).encode("utf-8") if cuerpo is not None else None
    req = urllib.request.Request(f"{A.n8n}/webhook/{ruta}", data=datos, method=metodo,
                                 headers={"Content-Type": "application/json"} if datos else {})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, json.loads(r.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as e:
        texto = e.read().decode("utf-8")
        try:
            return e.code, json.loads(texto)
        except json.JSONDecodeError:
            return e.code, {"_texto": texto[:300]}


def esperar(trabajo, limite=180):
    t0 = time.time()
    while time.time() - t0 < limite:
        c, j = http("GET", f"pims/trabajo?id={trabajo}")
        if c == 200 and j.get("estado") in ("terminado", "error", "terminado_con_errores"):
            return j
        time.sleep(1.5)
    raise AssertionError(f"El trabajo {trabajo} no terminó en {limite} s (último: {j})")


def prueba(nombre):
    def deco(f):
        try:
            d = f()
            RES.append((True, nombre, d or ""))
        except AssertionError as e:
            RES.append((False, nombre, str(e)[:600]))
        except Exception as e:  # noqa: BLE001
            RES.append((False, nombre, f"{type(e).__name__}: {e}"[:600]))
        return f
    return deco


def nucleo(r):
    return {"resumen": r.get("resumen"), "puntaje": json.loads(json.dumps(r.get("puntaje_proveedor")), parse_int=float),
            "dictamen": r.get("dictamen"),
            "controles": [(c["control"], c["estado"], c["severidad"], c["ambito"]) for c in r["controles"]],
            "alertas": r.get("alertas")}


def pdf_minimo(paginas):
    """PDF válido de varias páginas con texto (Helvetica, WinAnsi), sin dependencias."""
    objs = []
    kids = []
    n_pag = len(paginas)
    font_id = 3 + 2 * n_pag
    for i, lineas in enumerate(paginas):
        pid, cid = 3 + 2 * i, 4 + 2 * i
        kids.append(f"{pid} 0 R")
        flujo = "BT /F1 10 Tf 40 800 Td 12 TL\n" + "".join(
            "(" + l.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)") + ") '\n" for l in lineas) + "ET"
        comp = zlib.compress(flujo.encode("cp1252", "replace"))
        objs.append((pid, f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents {cid} 0 R "
                          f"/Resources << /Font << /F1 {font_id} 0 R >> >> >>".encode()))
        objs.append((cid, b"<< /Length " + str(len(comp)).encode() + b" /Filter /FlateDecode >>\nstream\n" + comp + b"\nendstream"))
    objs.insert(0, (2, f"<< /Type /Pages /Kids [{' '.join(kids)}] /Count {n_pag} >>".encode()))
    objs.insert(0, (1, b"<< /Type /Catalog /Pages 2 0 R >>"))
    objs.append((font_id, b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>"))
    objs.sort()
    salida = bytearray(b"%PDF-1.4\n")
    offs = {}
    for num, cuerpo in objs:
        offs[num] = len(salida)
        salida += f"{num} 0 obj\n".encode() + cuerpo + b"\nendobj\n"
    xref = len(salida)
    salida += f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n".encode()
    for num, _ in objs:
        salida += f"{offs[num]:010d} 00000 n \n".encode()
    salida += f"trailer << /Size {len(objs) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    return bytes(salida)


def configurar(**cambios):
    c, j = http("POST", "pims/config", cambios)
    assert c == 200 and j.get("ok"), f"No se pudo configurar el modelo: {c} {j}"


def auditar(org, contrato, proveedor="", fecha="2026-10-01", archivo=None):
    cuerpo = {"organizacion": org, "proveedor": proveedor, "fecha_ref": fecha}
    if archivo:
        cuerpo["archivo"] = archivo
    else:
        cuerpo["contrato_texto"] = contrato
    c, j = http("POST", "pims/auditar", cuerpo)
    assert c == 202 and j.get("trabajo"), f"auditar respondió {c}: {j}"
    return esperar(j["trabajo"])


def main():
    global A
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raiz", required=True)
    ap.add_argument("--n8n", default="http://localhost:5678")
    ap.add_argument("--simulado", default="http://127.0.0.1:11435")
    ap.add_argument("--sin-claude", action="store_true")
    ap.add_argument("--log", help="Registro del modelo simulado (--log de modelo_simulado.py), para revisar los prompts")
    A = ap.parse_args()
    raiz = Path(A.raiz)
    pr = raiz / "pims-dpa-auditor_pruebas"
    contrato = {n: (pr / "contratos" / f).read_text(encoding="utf-8") for n, f in
                [("NubeAndina", "dpa_nubeandina.md"), ("AndesCloud", "dpa_andescloud_bueno.md"), ("DigiServ", "dpa_ambiguo_inyeccion.md")]}
    ref = {n: json.loads((pr / "resultados" / f"resultado_{n}.json").read_text(encoding="utf-8")) for n in contrato}
    reg = {}

    @prueba("Estado: GET /pims/estado responde y oculta la API key")
    def _():
        configurar(api_key="sk-prueba-1234567890")
        c, j = http("GET", "pims/estado")
        assert c == 200 and j["ok"] and j["version"] == "2.0", j
        assert j["modelo"]["api_key"].startswith("********") and j["modelo"]["api_key"].endswith("7890"), j["modelo"]
        assert "_plantilla" not in [o["id"] for o in j["organizaciones"]]
        return f"{len(j['organizaciones'])} organizaciones"

    @prueba("Config: valores inválidos → 400 con la lista de errores")
    def _():
        c, j = http("POST", "pims/config", {"proveedor": "gpt9", "num_ctx": 5, "url_ollama": "ftp://x"})
        assert c == 400 and len(j.get("errores", [])) == 3, (c, j)

    proveedores = [("ollama", {"url_ollama": A.simulado}), ("anthropic", {"url_anthropic": A.simulado}),
                   ("openai", {"url_openai": A.simulado + "/v1"})]
    if not A.sin_claude:
        proveedores.append(("claude_code", {"claude_bin": "claude"}))
    for prov, extra in proveedores:
        @prueba(f"Auditar NubeAndina con proveedor '{prov}' → 22/100, idéntico a Python")
        def _(prov=prov, extra=extra):
            configurar(proveedor=prov, modelo="modelo-prueba", **extra)
            t = auditar("inversiones_altiplano", contrato["NubeAndina"], "NubeAndina")
            assert t["estado"] == "terminado", t
            c, d = http("GET", f"pims/registro/detalle?id={t['id_registro']}")
            assert c == 200, d
            r = d["resultado"]
            assert nucleo(r) == nucleo(ref["NubeAndina"]), "el resultado difiere del cálculo de Python"
            assert r["_registro"]["proveedor"] == prov and r["trazabilidad"]["calculo"] == "script"
            assert r["contrato"]["hash_documento_sha256"] == hashlib.sha256(contrato["NubeAndina"].encode()).hexdigest()
            assert "Valores calculados por n8n" in d["informe"] and "Trazabilidad registrada por n8n" in d["informe"]
            assert list(r["puntaje_proveedor"]["por_dimension"])[0] == "Condiciones de recolección y tratamiento"
            assert len(r["puntaje_proveedor"]["por_dimension"]) == 5, "el desglose debe tener las 5 secciones del Anexo A"
            assert "<svg" in d["informe"] and "A.2.3 · 50" in d["informe"], "falta el radar en la sección 7 del informe"
            assert "## 12. Cláusulas de la norma aplicadas" in d["informe"] and "6.1.3 e)" in d["informe"], "falta la sección 12 (cláusulas 4 a 10)"
            assert len(r["controles"]) == 26 and {"A.3.18", "A.3.24"} <= {c["control"] for c in r["controles"]}
            reg[prov] = t["id_registro"]
            return f"{t['puntaje']}/100 · {t['dictamen']}"

    configurar(proveedor="ollama", url_ollama=A.simulado, modelo="modelo-prueba")

    @prueba("Auditar AndesCloud (organización con perfil) → 100/100; el perfil llega al prompt como no confiable")
    def _():
        t = auditar("altiplano_perfil", contrato["AndesCloud"], "AndesCloud")
        assert t["estado"] == "terminado" and t["puntaje"] == 100 and t["dictamen"] == "Recomendable", t
        _, d = http("GET", f"pims/registro/detalle?id={t['id_registro']}")
        p = d["resultado"]["organizacion"]["perfil"]
        sha = hashlib.sha256((raiz / "organizaciones/altiplano_perfil/perfil_organizacion.md").read_bytes()).hexdigest()
        assert p and p["hash_sha256"] == sha and p["estado"] == "Borrador", p
        assert any("sin validar" in a for a in d["resultado"]["trazabilidad"]["advertencias"])
        ultimo = [json.loads(l) for l in open(A.log, encoding="utf-8")][-1] if A.log else None
        if ultimo:
            assert "CONTENIDO NO CONFIABLE" in ultimo["system"] and "Oficina de Cumplimiento" in ultimo["system"]
        reg["andes"] = t["id_registro"]
        return "perfil registrado con hash y advertencia de borrador"

    @prueba("Auditar DigiServ (inyección) → 0/100")
    def _():
        t = auditar("inversiones_altiplano", contrato["DigiServ"], "DigiServ")
        assert t["estado"] == "terminado" and t["puntaje"] == 0, t
        reg["digi"] = t["id_registro"]

    @prueba("JSON roto en la primera respuesta → una corrección automática → 22/100")
    def _():
        t = auditar("inversiones_altiplano", contrato["NubeAndina"] + "\nMOCK:JSON_ROTO", "NubeAndina")
        assert t["estado"] == "terminado" and t["puntaje"] == 22, t
        _, d = http("GET", f"pims/registro/detalle?id={t['id_registro']}")
        assert d["resultado"]["_registro"]["reintentos"] == 1, d["resultado"]["_registro"]
        if A.log:
            ultimo = [json.loads(l) for l in open(A.log, encoding="utf-8")][-1]
            assert ultimo.get("formato") == "json", f"la corrección con Ollama no pidió JSON ({ultimo.get('formato')})"
        return "reintentos = 1; corrección con format=json"

    @prueba("JSON abreviado con comentarios (1 de 26 controles) → se repara, se detecta y se corrige → 22/100")
    def _():
        t = auditar("inversiones_altiplano", contrato["NubeAndina"] + "\nMOCK:JSON_ABREVIADO", "NubeAndina")
        assert t["estado"] == "terminado" and t["puntaje"] == 22, t
        if A.log:
            ultimo = [json.loads(l) for l in open(A.log, encoding="utf-8")][-1]
            assert "faltan 25 de 26" in ultimo["usuario"], "la corrección no indicó los controles faltantes"
            assert "Tu matriz de controles del informe" in ultimo["usuario"], "la corrección no incluyó la matriz del informe"
            assert ultimo.get("formato") == "json"
        configurar(formato_correccion="esquema")
        t2 = auditar("inversiones_altiplano", contrato["NubeAndina"] + "\nMOCK:JSON_ABREVIADO", "NubeAndina")
        configurar(formato_correccion="json")
        assert t2["estado"] == "terminado" and t2["puntaje"] == 22, t2
        if A.log:
            assert [json.loads(l) for l in open(A.log, encoding="utf-8")][-1].get("formato") == "esquema"
        return "faltan 25 de 26 → corrección con la matriz; format=json y, configurado, el esquema completo"

    @prueba("JSON con 'controles' vacío (solo un comentario) → se detecta y se corrige; nunca un 0/100 sin controles")
    def _():
        t = auditar("inversiones_altiplano", contrato["NubeAndina"] + "\nMOCK:SIN_CONTROLES", "NubeAndina")
        assert t["estado"] == "terminado" and t["puntaje"] == 22, t
        _, d = http("GET", f"pims/registro/detalle?id={t['id_registro']}")
        assert d["resultado"]["_registro"]["reintentos"] == 1 and len(d["resultado"]["controles"]) == 26, d["resultado"]["_registro"]
        u = [json.loads(l) for l in open(A.log, encoding="utf-8")][-1] if A.log else None
        if u:
            assert "la lista está vacía" in u["usuario"], "la corrección no explicó el error"
        return "lista vacía → corrección → 26 controles, 22/100"

    @prueba("Identificadores con adornos, fila A.1.2.7 y null opcional → ajustes de forma sin corrección → 22/100")
    def _():
        t = auditar("inversiones_altiplano", contrato["NubeAndina"] + "\nMOCK:IDS_ADORNADOS", "NubeAndina")
        assert t["estado"] == "terminado" and t["puntaje"] == 22, t
        _, d = http("GET", f"pims/registro/detalle?id={t['id_registro']}")
        rg = d["resultado"]["_registro"]
        assert rg["reintentos"] == 0 and len(rg["ajustes_automaticos"]) == 3, rg
        assert nucleo(d["resultado"]) == nucleo(ref["NubeAndina"])
        return "; ".join(a[:40] for a in rg["ajustes_automaticos"])

    @prueba("JSON inválido también tras la corrección → error y datos/fallidos con errores y ambas respuestas")
    def _():
        t = auditar("inversiones_altiplano", contrato["NubeAndina"] + "\nMOCK:JSON_ROTO_SIEMPRE", "NubeAndina")
        assert t["estado"] == "error" and "incluso tras una corrección" in t["mensaje"], t
        assert t.get("errores"), t
        f = raiz / "datos" / "fallidos" / f"{t['trabajo']}.md"
        txt = f.read_text(encoding="utf-8")
        assert "## Errores de esquema" in txt and "## Primera respuesta del modelo" in txt and "## Respuesta a la corrección" in txt
        return f"{len(t['errores'])} error(es) registrados en datos/fallidos"

    @prueba("Contrato en PDF de 2 páginas → texto con marcadores de página y hash de los bytes del PDF")
    def _():
        lineas = contrato["NubeAndina"].splitlines()
        pdf = pdf_minimo([lineas[:12], lineas[12:]])
        import base64
        t = auditar("inversiones_altiplano", None, "NubeAndina",
                    archivo={"nombre": "Contrato NubeAndina.pdf", "base64": base64.b64encode(pdf).decode()})
        assert t["estado"] == "terminado" and t["puntaje"] == 22, t
        _, d = http("GET", f"pims/registro/detalle?id={t['id_registro']}")
        assert d["resultado"]["contrato"]["hash_documento_sha256"] == hashlib.sha256(pdf).hexdigest()
        if A.log:
            ultimo = [json.loads(l) for l in open(A.log, encoding="utf-8")][-1]
            assert "[Página 1]" in ultimo["usuario"] and "[Página 2]" in ultimo["usuario"], "faltan marcadores de página"
        return "PDF leído por n8n (Extract from File)"

    @prueba("Errores: organización inexistente → trabajo en error con mensaje claro")
    def _():
        t = auditar("no_existe_org", contrato["NubeAndina"])
        assert t["estado"] == "error" and "no existe" in t["mensaje"], t

    @prueba("Errores: petición inválida → 400 sin crear trabajo")
    def _():
        c, j = http("POST", "pims/auditar", {"organizacion": "../etc", "contrato_texto": "x"})
        assert c == 400 and not j["ok"], (c, j)
        c, j = http("POST", "pims/auditar", {"organizacion": "unsa"})
        assert c == 400 and "contrato_texto" in j["error"], (c, j)

    @prueba("Errores: proveedor caído (Ollama sin servicio) → trabajo en error, no se queda colgado")
    def _():
        configurar(proveedor="ollama", url_ollama="http://127.0.0.1:9")
        try:
            t = auditar("inversiones_altiplano", contrato["NubeAndina"])
        finally:
            configurar(proveedor="ollama", url_ollama=A.simulado)
        assert t["estado"] == "error" and "ollama" in t["mensaje"].lower(), t
        return t["mensaje"][:90]

    @prueba("Aprobaciones: orden obligatorio DPO → Legal y estados cerrados")
    def _():
        rid = reg.get("ollama") or next(iter(reg.values()))
        reg["aprobado"] = rid
        c, j = http("POST", "pims/aprobar", {"id_registro": rid, "rol": "Legal", "decision": "aprobar", "usuario": "Ana"})
        assert c == 409 and "DPO" in j["error"], (c, j)
        c, j = http("POST", "pims/aprobar", {"id_registro": rid, "rol": "DPO", "decision": "aprobar", "usuario": "Luis", "comentario": "ok con enmiendas"})
        assert c == 200 and j["estado"] == "Pendiente Legal", (c, j)
        c, j = http("POST", "pims/aprobar", {"id_registro": rid, "rol": "Legal", "decision": "aprobar", "usuario": "Ana"})
        assert c == 200 and j["estado"] == "Aprobado" and len(j["historial"]) == 2, (c, j)
        c, j = http("POST", "pims/aprobar", {"id_registro": rid, "rol": "DPO", "decision": "rechazar", "usuario": "Luis"})
        assert c == 409, (c, j)
        _, d = http("GET", f"pims/registro/detalle?id={rid}")
        assert d["resultado"]["contrato"]["estado_dpa"] == "Aprobado" and "✅ aprobó" in d["informe"]
        c, j = http("POST", "pims/aprobar", {"id_registro": reg["digi"], "rol": "DPO", "decision": "rechazar", "usuario": "Luis"})
        assert c == 200 and j["estado"] == "Rechazado", (c, j)
        c, j = http("POST", "pims/aprobar", {"id_registro": "NO_EXISTE_1", "rol": "DPO", "decision": "aprobar", "usuario": "x"})
        assert c == 404, (c, j)
        return "409 → Pendiente Legal → Aprobado → 409; rechazo y 404"

    @prueba("Registro: listado filtrable por organización y estado")
    def _():
        c, j = http("GET", "pims/registro?organizacion=inversiones_altiplano")
        assert c == 200 and j["total"] >= 5, j
        c, j = http("GET", "pims/registro?estado=Aprobado")
        assert c == 200 and reg.get("aprobado") in [x["id_registro"] for x in j["registros"]], j
        assert all(x["estado"] == "Aprobado" for x in j["registros"]), j

    def chat(cuerpo, limite=120):
        c, j = http("POST", "pims/chat", cuerpo)
        assert c == 202 and j.get("trabajo"), (c, j)
        return esperar(j["trabajo"], limite)

    def ultimo_pedido():
        return [json.loads(l) for l in open(A.log, encoding="utf-8")][-1] if A.log else None

    @prueba("Chat sobre un expediente: responde con el contexto, guarda la conversación y no modifica el expediente")
    def _():
        rid = reg["ollama"]
        archivos = [raiz / "datos" / "registro" / f"{rid}.{e}" for e in ("json", "md")]
        antes = [hashlib.sha256(a.read_bytes()).hexdigest() for a in archivos]
        assert (raiz / "datos" / "registro" / f"{rid}.contrato.txt").is_file(), "la auditoría no guardó el texto del contrato"
        base = {"ambito": "expediente", "id": rid, "organizacion": "inversiones_altiplano", "usuario": "Prueba"}
        t = chat(dict(base, pregunta="¿Por qué A.3.10 no cumple?"))
        assert t["estado"] == "terminado" and "Respuesta simulada (expediente)" in t["respuesta_chat"], t
        import re
        n = int(re.search(r"Controles en el contexto: (\d+)", t["respuesta_chat"]).group(1))
        assert n >= 26, f"el contexto solo tenía {n} controles"
        u = ultimo_pedido()
        if u:
            assert "Eres el asistente del Agente 7" in u["system"] and "CONTENIDO NO CONFIABLE" in u["system"]
            assert "72 horas" in u["system"] and "Informe de la auditoría" in u["system"], "falta el contrato o el informe en el contexto"
        t2 = chat(dict(base, pregunta="¿Y qué cláusula propones?"))
        assert t2["estado"] == "terminado" and "Mensajes previos del usuario: 1" in t2["respuesta_chat"], t2
        c, j = http("GET", f"pims/chat?ambito=expediente&id={rid}")
        assert c == 200 and len(j["mensajes"]) == 4 and j["mensajes"][0]["usuario"] == "Prueba", j
        despues = [hashlib.sha256(a.read_bytes()).hexdigest() for a in archivos]
        assert antes == despues, "el chat modificó el expediente"
        return "2 preguntas con historial; expediente intacto"

    @prueba("Chat sobre una organización: incluye solo sus expedientes")
    def _():
        t = chat({"ambito": "organizacion", "organizacion": "inversiones_altiplano", "pregunta": "¿Qué proveedores tienen riesgo alto?"})
        assert t["estado"] == "terminado" and "Respuesta simulada (organizacion)" in t["respuesta_chat"], t
        u = ultimo_pedido()
        if u:
            assert "| Id | Proveedor |" in u["system"] and reg["ollama"] in u["system"]
            assert reg["andes"] not in u["system"], "se filtraron expedientes de otra organización"
        c, j = http("GET", "pims/chat?ambito=organizacion&id=inversiones_altiplano")
        assert c == 200 and len(j["mensajes"]) >= 2, j

    @prueba("Chat: errores (petición inválida, expediente inexistente o de otra organización)")
    def _():
        for cuerpo in ({"ambito": "x", "organizacion": "inversiones_altiplano", "pregunta": "a"},
                       {"ambito": "organizacion", "organizacion": "inversiones_altiplano", "pregunta": "  "}):
            c, j = http("POST", "pims/chat", cuerpo)
            assert c == 400 and not j.get("ok"), (c, j)
        t = chat({"ambito": "expediente", "id": "DPA-NO-EXISTE_1", "organizacion": "inversiones_altiplano", "pregunta": "¿?"})
        assert t["estado"] == "error" and "No existe el expediente" in t["mensaje"], t
        t = chat({"ambito": "expediente", "id": reg["andes"], "organizacion": "inversiones_altiplano", "pregunta": "¿?"})
        assert t["estado"] == "error" and "es de la organización" in t["mensaje"], t
        c, j = http("GET", "pims/chat")
        assert c == 400, (c, j)

    @prueba("Chat con Ollama y un informe enorme: el contexto se recorta para caber en 32 768 tokens")
    def _():
        rid = reg["ollama"]
        d = raiz / "datos" / "registro"
        nuevo = f"{rid}_GRANDE"
        r = json.loads((d / f"{rid}.json").read_text(encoding="utf-8"))
        r["_registro"]["id_registro"] = nuevo
        (d / f"{nuevo}.json").write_text(json.dumps(r, ensure_ascii=False), encoding="utf-8")
        (d / f"{nuevo}.md").write_text("# Informe\n" + ("Texto del informe muy largo. " * 25000), encoding="utf-8")
        try:
            t = chat({"ambito": "expediente", "id": nuevo, "organizacion": "inversiones_altiplano", "pregunta": "Resume"})
            assert t["estado"] == "terminado" and "Informe de la auditoría" in t.get("contexto_recortado", []), t
            u = ultimo_pedido()
            if u:
                total = len(u["system"]) + len(u["usuario"])
                assert total <= (32768 - 3000) * 3, f"el pedido ({total} caracteres) no cabe en 32 768 tokens"
            return "informe recortado"
        finally:
            for e in ("json", "md"):
                (d / f"{nuevo}.{e}").unlink(missing_ok=True)

    @prueba("Perfilar organización (2 documentos) → perfil válido en Borrador, hashes reales, nota de inyección en §8")
    def _():
        c, j = http("POST", "pims/perfilar", {"organizacion": "altiplano_docs"})
        assert c == 202, (c, j)
        t = esperar(j["trabajo"])
        assert t["estado"] == "terminado", t
        md = (raiz / "organizaciones/altiplano_docs/perfil_organizacion.md").read_text(encoding="utf-8")
        for d in ("D1_rof_altiplano.md", "D2_manual_procesos_cobranza.md"):
            sha = hashlib.sha256((raiz / "organizaciones/altiplano_docs/documentos" / d).read_bytes()).hexdigest()
            assert sha in md, f"falta el hash de {d}"
        assert t["validacion"]["valido"] and len(t["validacion"]["documentos"]) == 2, t["validacion"]
        return t["mensaje"]

    @prueba("Perfil: GET devuelve validación y terceros; el DPO lo valida; segunda validación sigue siendo válida")
    def _():
        c, j = http("GET", "pims/perfil?organizacion=altiplano_docs")
        assert c == 200 and j["validacion"]["valido"] and len(j["terceros"]) == 4, j
        c, j = http("POST", "pims/perfil/validar", {"organizacion": "altiplano_docs", "validado_por": "María Quispe (DPO)"})
        assert c == 200 and j["estado"].startswith("Validado por DPO"), (c, j)
        c, j = http("GET", "pims/perfil?organizacion=altiplano_docs")
        assert j["validacion"]["estado"].startswith("Validado por DPO") and j["validacion"]["valido"], j["validacion"]
        c, j = http("POST", "pims/perfil/validar", {"organizacion": "unsa", "validado_por": "x"})
        assert c == 404, (c, j)

    @prueba("Organizaciones: perfil, registros y terceros sin DPA evaluado (brechas)")
    def _():
        c, j = http("GET", "pims/organizaciones")
        o = {x["id"]: x for x in j["organizaciones"]}
        assert o["altiplano_perfil"]["perfil"]["existe"] and reg["andes"] in [r["id_registro"] for r in o["altiplano_perfil"]["registros"]]
        b = o["altiplano_perfil"]["terceros_sin_dpa_evaluado"]
        assert any("NubeAndina" in x for x in b) and not any("AndesCloud" in x for x in b), b
        return f"brechas altiplano_perfil: {len(b)}"

    @prueba("Crear organización desde la API (Execute Command) y subir un documento")
    def _():
        oid = f"muni_prueba_{int(time.time()) % 100000}"
        c, j = http("POST", "pims/organizacion", {"id": oid, "nombre": "Municipalidad de Prueba", "jurisdiccion": "peru",
                                                  "cargo_dpo": "Oficial de Datos", "cargo_legal": "Procuraduría"})
        assert c == 201, (c, j)
        cfg = json.loads((raiz / f"organizaciones/{oid}/config_organizacion.json").read_text(encoding="utf-8"))
        assert cfg["aprobadores_cargos"]["Legal"] == "Procuraduría" and cfg["jurisdiccion"] == "peru"
        c, j = http("POST", "pims/organizacion", {"id": oid, "nombre": "x"})
        assert c == 409, (c, j)
        c, j = http("POST", "pims/organizacion", {"id": "otra", "nombre": "x", "jurisdiccion": "_plantilla"})
        assert c == 400, (c, j)
        c, j = http("POST", "pims/documento", {"organizacion": oid, "nombre": "ROF 2026.docx", "texto": "Artículo 1. Prueba."})
        assert c == 201 and j["nombre"] == "ROF_2026.txt", (c, j)
        assert (raiz / f"organizaciones/{oid}/documentos/ROF_2026.txt").read_text(encoding="utf-8") == "Artículo 1. Prueba."
        c, j = http("POST", "pims/documento", {"organizacion": "no_existe_x", "nombre": "a.txt", "texto": "x"})
        assert c == 404, (c, j)

    @prueba("Perfil con documentos extensos y respuesta defectuosa → notas compactadas, cabecera y documentos corregidos, filas sin fuente como Supuesto")
    def _():
        import shutil
        oid = f"perfil_grande_{int(time.time()) % 100000}"
        base = raiz / "organizaciones" / oid
        (base / "documentos").mkdir(parents=True)
        cfg = json.loads((raiz / "organizaciones/_plantilla/config_organizacion.json").read_text(encoding="utf-8"))
        cfg.update({"id_organizacion": oid, "organizacion": "Universidad de Prueba", "jurisdiccion": "peru"})
        (base / "config_organizacion.json").write_text(json.dumps(cfg, ensure_ascii=False), encoding="utf-8")
        texto = "\n".join(f"Artículo {i}. La unidad {i} gestiona información institucional y registros." for i in range(1, 4500))
        (base / "documentos" / "MOCK_NOTAS_LARGAS_A.md").write_text(texto, encoding="utf-8")
        (base / "documentos" / "MOCK_NOTAS_LARGAS_B.md").write_text(texto, encoding="utf-8")
        (base / "documentos" / "MOCK_PERFIL_SIN_FUENTES.md").write_text("Artículo 1. Documento breve.", encoding="utf-8")
        try:
            c, j = http("POST", "pims/perfilar", {"organizacion": oid})
            assert c == 202, (c, j)
            t = esperar(j["trabajo"], 300)
            assert t["estado"] == "terminado", t
            assert "Supuesto" in t["mensaje"] and "Se omitieron" in t["mensaje"], t["mensaje"]
            val = json.loads((base / "validacion_perfil.json").read_text(encoding="utf-8"))
            assert val["valido"] and len(val["ajustes_automaticos"]) == 3 and val["notas_recortadas"] > 0, val
            perfil = (base / "perfil_organizacion.md").read_text(encoding="utf-8")
            assert f"| Id | {oid} |" in perfil and "| D3 | MOCK_PERFIL_SIN_FUENTES |" in perfil
            if A.log:
                pedido = [json.loads(l) for l in open(A.log, encoding="utf-8") if "Redacta el perfil completo" in json.loads(l)["usuario"]][-1]
                total = len(pedido["system"]) + len(pedido["usuario"])
                assert total <= (32768 - 7000) * 3, f"el pedido final ({total} caracteres) no cabe en 32 768 tokens"
                assert "### D1" in pedido["usuario"] and "### D2" in pedido["usuario"] and "### D3" in pedido["usuario"]
            return f"{val['notas_recortadas']} notas omitidas; {len(val['ajustes_automaticos'])} ajustes"
        finally:
            shutil.rmtree(base, ignore_errors=True)

    @prueba("Renovaciones: GET calcula alertas con la fecha de hoy y omite los rechazados")
    def _():
        c, j = http("GET", "pims/renovaciones")
        assert c == 200 and j["ok"], j
        ids = [x["id_registro"] for x in j["registros_con_alertas"]]
        assert reg["digi"] not in ids, "incluyó un registro rechazado"
        assert any(x["fin_vigencia"] is None for x in j["registros_con_alertas"])
        return f"{len(ids)} registros con alertas al {j['fecha_referencia']}"

    @prueba("Jurisdicciones: lista Perú utilizable y la plantilla no")
    def _():
        c, j = http("GET", "pims/jurisdicciones")
        d = {x["id"]: x for x in j["jurisdicciones"]}
        assert d["peru"]["usable"] and not d["_plantilla"]["usable"], d

    ok = sum(1 for r in RES if r[0])
    print(f"\nPruebas de los flujos de n8n (modelo simulado)\n{'=' * 46}")
    for paso, nombre, det in RES:
        print(f"[{'OK  ' if paso else 'FALLA'}] {nombre}" + (f"\n         {det}" if det else ""))
    print(f"\n{ok}/{len(RES)} pruebas correctas")
    sys.exit(0 if ok == len(RES) else 1)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(errors="replace")
    except (AttributeError, ValueError):
        pass
    main()

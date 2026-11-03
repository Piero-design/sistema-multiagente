#!/usr/bin/env python3
"""
validar_perfil.py — Perfilador de organización (Agente 1) · v1.0

Comprueba que un perfil_organizacion.md respete el formato fijo de assets/plantilla_perfil.md
y las reglas de trazabilidad y asimetría:
  - cabecera completa y estado válido (Borrador / Validado por DPO …)
  - inventario de documentos fuente (D1, D2…)
  - secciones 1 a 8 presentes y en orden
  - cada fila de las secciones 2 a 6 con fuente [Dn …] o "Supuesto", y cada Dn citado existe
  - columna "¿DPA localizado?" solo con Sí / No / Desconocido
  - sin juicios de cumplimiento (cumple, aprobado, homologado, exento, no requiere DPA…)
    fuera de la sección 8

Uso:
  python scripts/validar_perfil.py perfil_organizacion.md [--json]

Códigos de salida: 0 válido (puede haber advertencias) · 1 con errores · 2 archivo ilegible.
Solo biblioteca estándar.
"""
import argparse
import json
import re
import sys
from pathlib import Path

CAMPOS_CABECERA = ["Organización", "Id", "Jurisdicción", "Versión", "Estado", "Fecha",
                   "Generado por", "Validado por"]
SECCIONES = {1: "Identificación", 2: "Estructura", 3: "Aprobadores", 4: "Procesos",
             5: "Condiciones de riesgo", 6: "Terceros", 7: "Supuestos", 8: "Observaciones"}
SECCIONES_CON_FUENTE = (1, 2, 3, 4, 5, 6)
VALORES_DPA = {"sí", "si", "no", "desconocido"}
JUICIO = re.compile(r"\b(cumplen?|conformes?|aprobad[oa]s?|homologad[oa]s?|exent[oa]s?|"
                    r"no\s+requieren?\s+(?:un\s+)?(?:dpa|contrato|evaluaci[oó]n))\b", re.IGNORECASE)
REF_DOC = re.compile(r"\bD(\d+)\b")


def celdas(linea: str):
    return [c.strip() for c in linea.strip().strip("|").split("|")]


def es_marcador(celda: str) -> bool:
    """Texto de plantilla entre corchetes, p. ej. '[Pública / Privada]'. Una fuente '[D1, art. 2]' no lo es."""
    return bool(re.search(r"\[[^\]]*\]", celda)) and not REF_DOC.search(celda) and celda.startswith("[")


def es_fila(linea: str) -> bool:
    return linea.strip().startswith("|") and not re.match(r"^\|\s*:?-{2,}", linea.strip())


def tablas(lineas):
    """Devuelve las tablas de un bloque como listas [cabecera, filas...] (sin la línea separadora)."""
    resultado, actual = [], []
    for ln in lineas:
        if ln.strip().startswith("|"):
            if es_fila(ln):
                actual.append(celdas(ln))
        elif actual:
            resultado.append(actual)
            actual = []
    if actual:
        resultado.append(actual)
    return resultado


def validar(texto: str):
    errores, advertencias = [], []
    lineas = texto.splitlines()

    # --- Secciones ---
    pos = {}
    for i, ln in enumerate(lineas):
        m = re.match(r"^##\s+(\d+)\.\s", ln)
        if m:
            pos[int(m.group(1))] = i
    for n, nombre in SECCIONES.items():
        if n not in pos:
            errores.append(f"Falta la sección '## {n}. {nombre}…'.")
    orden = [pos[n] for n in sorted(pos) if n in SECCIONES]
    if orden != sorted(orden):
        errores.append("Las secciones numeradas no están en orden.")

    inicio_doc = next((i for i, ln in enumerate(lineas) if ln.strip().lower().startswith("## documentos fuente")), None)
    primera_sec = min(pos.values()) if pos else len(lineas)

    # --- Cabecera ---
    cab = {}
    for t in tablas(lineas[: inicio_doc if inicio_doc is not None else primera_sec]):
        for fila in t[1:] if t and t[0][:1] == ["Campo"] else t:
            if len(fila) >= 2:
                cab[fila[0]] = fila[1]
    for campo in CAMPOS_CABECERA:
        valor = cab.get(campo, "")
        if not valor:
            errores.append(f"Cabecera: falta el campo '{campo}'.")
        elif valor.startswith("["):
            errores.append(f"Cabecera: el campo '{campo}' conserva el marcador de plantilla ({valor}).")
    estado = re.sub(r"[*`]", "", cab.get("Estado", "")).strip()
    if estado and not (estado == "Borrador" or estado.lower().startswith("validado por dpo")):
        errores.append(f"Cabecera: estado {estado!r} no válido (usa 'Borrador' o 'Validado por DPO (nombre, fecha)').")
    if estado == "Borrador":
        advertencias.append("Perfil en estado Borrador: debe validarlo el DPO antes de un uso formal.")

    # --- Documentos fuente ---
    docs = set()
    if inicio_doc is None:
        errores.append("Falta la sección '## Documentos fuente'.")
    else:
        for t in tablas(lineas[inicio_doc:primera_sec]):
            for fila in t[1:]:
                m = re.fullmatch(r"D(\d+)", fila[0]) if fila else None
                if not m:
                    continue
                docs.add(int(m.group(1)))
                if any(c.startswith("[") for c in fila[1:3]):
                    errores.append(f"Documentos fuente: D{m.group(1)} conserva marcadores de plantilla.")
                h = fila[-1] if len(fila) >= 6 else ""
                if h.lower() == "pendiente":
                    advertencias.append(f"Documentos fuente: D{m.group(1)} sin hash SHA-256.")
                elif not re.fullmatch(r"[0-9a-fA-F]{64}", h):
                    errores.append(f"Documentos fuente: D{m.group(1)} con hash inválido ({h or 'vacío'}).")
        if not docs:
            errores.append("Documentos fuente: no hay ningún documento D1, D2…")

    # --- Secciones con tablas ---
    limites = sorted(pos.items(), key=lambda kv: kv[1])
    for idx, (n, ini) in enumerate(limites):
        fin = limites[idx + 1][1] if idx + 1 < len(limites) else len(lineas)
        bloque = lineas[ini:fin]
        if n in SECCIONES_CON_FUENTE:
            filas_validas = 0
            for t in tablas(bloque):
                cabecera = [c.lower() for c in t[0]]
                if "fuente" not in cabecera:
                    continue
                i_fuente = cabecera.index("fuente")
                i_dpa = next((i for i, c in enumerate(cabecera) if "dpa" in c), None)
                for fila in t[1:]:
                    if not any(fila):
                        errores.append(f"Sección {n}: fila vacía (borra las filas de plantilla no usadas).")
                        continue
                    filas_validas += 1
                    etiqueta = f"Sección {n}, fila '{fila[0][:40]}'"
                    if any(es_marcador(c) for c in fila):
                        errores.append(f"{etiqueta}: conserva marcadores de plantilla.")
                    fuente = fila[i_fuente] if i_fuente < len(fila) else ""
                    refs = {int(x) for x in REF_DOC.findall(fuente)}
                    if not refs and "supuesto" not in fuente.lower():
                        errores.append(f"{etiqueta}: sin fuente [Dn …] ni 'Supuesto'.")
                    for r in sorted(refs - docs):
                        errores.append(f"{etiqueta}: cita D{r}, que no está en 'Documentos fuente'.")
                    if i_dpa is not None and i_dpa < len(fila):
                        if fila[i_dpa].strip("* ").lower() not in VALORES_DPA:
                            errores.append(f"{etiqueta}: '¿DPA localizado?' = {fila[i_dpa]!r}; "
                                           "solo se admite Sí / No / Desconocido.")
                    for c in fila:
                        for m in JUICIO.finditer(c):
                            errores.append(f"{etiqueta}: juicio de cumplimiento no permitido ({m.group(0)!r}). "
                                           "El perfil es contexto, no evidencia.")
            if filas_validas == 0:
                advertencias.append(f"Sección {n}: sin filas con datos.")
        elif n == 7:
            for ln in bloque[1:]:
                for m in JUICIO.finditer(ln):
                    advertencias.append(f"Sección 7: posible juicio de cumplimiento ({m.group(0)!r}); revísalo.")

    return {"valido": not errores, "estado": estado or None, "documentos": len(docs),
            "errores": errores, "advertencias": advertencias}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("perfil")
    ap.add_argument("--json", action="store_true", help="Salida en JSON (para integraciones como n8n)")
    a = ap.parse_args()
    try:
        texto = Path(a.perfil).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        print(f"No se pudo leer el perfil: {exc}")
        sys.exit(2)

    r = validar(texto)
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        print(f"Perfil: {a.perfil} | estado: {r['estado']} | documentos: {r['documentos']}")
        for e in r["errores"]:
            print(f"ERROR: {e}")
        for w in r["advertencias"]:
            print(f"ADVERTENCIA: {w}")
        print("Formato: valido" if r["valido"] else f"Formato: INVALIDO ({len(r['errores'])} errores)")
    sys.exit(0 if r["valido"] else 1)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(errors="replace")
    except (AttributeError, ValueError):
        pass
    main()

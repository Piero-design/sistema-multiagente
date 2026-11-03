"""
Generador Formal de Declaración de Aplicabilidad (SoA)
Norma Técnica Internacional ISO/IEC 27701:2025 (PIMS) & Ley N° 29733

Universidad Nacional de San Agustín de Arequipa (UNSA)
Dirección Universitaria de Tecnologías de la Información y Comunicación (DUTIC)
Oficialía de Protección de Datos Personales (OPD)
"""

import os
from datetime import datetime
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def aplicar_estilo_celda(celda, color_fondo=None, negrita=False, tamano=9, color_texto=(51, 51, 51), alineacion=WD_ALIGN_PARAGRAPH.LEFT):
    """Aplica formato visual sobrio y corporativo a una celda de tabla."""
    if color_fondo:
        shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_fondo}"/>')
        celda._tc.get_or_add_tcPr().append(shading)
    
    for parrafo in celda.paragraphs:
        parrafo.alignment = alineacion
        parrafo.paragraph_format.space_before = Pt(3)
        parrafo.paragraph_format.space_after = Pt(3)
        for run in parrafo.runs:
            run.font.name = "Calibri"
            run.font.size = Pt(tamano)
            run.font.bold = negrita
            run.font.color.rgb = RGBColor(*color_texto)

def generar_documento_soa(datos_soa, ruta_salida=None):
    """
    Construye la Declaración de Aplicabilidad (SoA) con rigor técnico,
    estructura corporativa y lenguaje formal de auditoría de sistemas.
    """
    if ruta_salida is None:
        base = os.path.dirname(os.path.abspath(__file__))
        ruta_salida = os.path.join(base, "Declaracion_de_Aplicabilidad_ISO_27701_UNSA.docx")

    doc = Document()

    # Márgenes ejecutivos estrechos para acomodar matrices de auditoría
    for section in doc.sections:
        section.top_margin = Inches(0.7)
        section.bottom_margin = Inches(0.7)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

    # 1. ENCABEZADO INSTITUCIONAL
    p_meta = doc.add_paragraph()
    p_meta.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_meta = p_meta.add_run(
        "CÓDIGO: DUTIC-OPD-SOA-27701-2026\n"
        "VERSIÓN: 2.0 (REVISIÓN FINAL DE AUDITORÍA)\n"
        "CLASIFICACIÓN: CONFIDENCIAL / USO INSTITUCIONAL EXCLUSIVO"
    )
    r_meta.font.name = "Calibri"
    r_meta.font.size = Pt(8)
    r_meta.font.color.rgb = RGBColor(100, 116, 139)

    # TÍTULO PRINCIPAL
    p_titulo = doc.add_paragraph()
    p_titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_titulo.paragraph_format.space_before = Pt(8)
    p_titulo.paragraph_format.space_after = Pt(2)
    run_institucion = p_titulo.add_run("UNIVERSIDAD NACIONAL DE SAN AGUSTÍN DE AREQUIPA\n")
    run_institucion.font.name = "Calibri"
    run_institucion.font.size = Pt(13)
    run_institucion.font.bold = True
    run_institucion.font.color.rgb = RGBColor(15, 23, 42)

    run_doc_nombre = p_titulo.add_run("DECLARACIÓN DE APLICABILIDAD DE CONTROLES DE PRIVACIDAD (SoA)\n")
    run_doc_nombre.font.name = "Calibri"
    run_doc_nombre.font.size = Pt(16)
    run_doc_nombre.font.bold = True
    run_doc_nombre.font.color.rgb = RGBColor(30, 58, 138)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(14)
    run_sub = p_sub.add_run(
        "Sistema de Gestión de Información de Privacidad (PIMS) — ISO/IEC 27701:2025\n"
        "En concordancia con la Ley N° 29733 de Protección de Datos Personales del Perú y la Directiva DIR-OTIC-004-UNSA"
    )
    run_sub.font.name = "Calibri"
    run_sub.font.size = Pt(10)
    run_sub.font.italic = True
    run_sub.font.color.rgb = RGBColor(71, 85, 105)

    # 2. CUADRO DE CONTROL DE DOCUMENTO Y METADATOS
    t_meta = doc.add_table(rows=5, cols=4)
    t_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_meta.autofit = False

    meta_info = [
        ("Entidad Titular:", "Universidad Nacional de San Agustín de Arequipa (UNSA)", "Fecha de Evaluación:", datetime.now().strftime("%d de octubre de %Y")),
        ("Alcance Institucional:", "Sistemas SISUNSA, Comedor Biométrico, Plataforma de Matrícula y Admisión", "Vigencia Documental:", "Periodo Académico 2026 - 2027"),
        ("Rol Normativo PIMS:", "Responsable del Tratamiento de PII (PII Controller - Anexo A.1)", "Cláusula Marco:", "Cláusula 6.1.3 d) ISO/IEC 27701:2025"),
        ("Marco Jurídico Base:", "Ley N° 29733 y D.S. N° 003-2013-JUS (ANPD)", "Directiva Interna:", "DIR-OTIC-004-UNSA (RAT Institucional)"),
        ("Responsable Técnico:", "Comité de Auditoría de Sistemas y Seguridad de la Información", "Aprobación Formal:", "Oficial de Protección de Datos (DPO) & DUTIC")
    ]

    for i, row in enumerate(meta_info):
        t_meta.cell(i, 0).text = row[0]
        t_meta.cell(i, 1).text = row[1]
        t_meta.cell(i, 2).text = row[2]
        t_meta.cell(i, 3).text = row[3]
        aplicar_estilo_celda(t_meta.cell(i, 0), color_fondo="F1F5F9", negrita=True, tamano=8.5, color_texto=(30, 41, 59))
        aplicar_estilo_celda(t_meta.cell(i, 1), tamano=8.5)
        aplicar_estilo_celda(t_meta.cell(i, 2), color_fondo="F1F5F9", negrita=True, tamano=8.5, color_texto=(30, 41, 59))
        aplicar_estilo_celda(t_meta.cell(i, 3), tamano=8.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # 3. SECCIÓN 1: OBJETIVO, ALCANCE Y METODOLOGÍA
    h1 = doc.add_heading(level=2)
    r_h1 = h1.add_run("1. Objetivo, Alcance y Criterios de Evaluación")
    r_h1.font.name = "Calibri"
    r_h1.font.color.rgb = RGBColor(15, 23, 42)

    p_obj = doc.add_paragraph()
    p_obj.paragraph_format.space_after = Pt(6)
    r_obj = p_obj.add_run(
        "El presente documento constituye la Declaración de Aplicabilidad (Statement of Applicability - SoA) oficial de la "
        "Universidad Nacional de San Agustín de Arequipa (UNSA), formulada bajo los requerimientos de la norma internacional "
        "ISO/IEC 27701:2025 (extensión de privacidad para ISO/IEC 27001). Su propósito es documentar formalmente qué controles de "
        "privacidad aplican a los sistemas institucionales de tratamiento de datos personales, justificar las inclusiones o exclusiones "
        "normativas, verificar la suficiencia de las evidencias documentales probatorias y trazar las acciones de remediación necesarias "
        "previas a la auditoría de certificación."
    )
    r_obj.font.name = "Calibri"
    r_obj.font.size = Pt(9.5)
    r_obj.font.color.rgb = RGBColor(51, 65, 85)

    p_alcance = doc.add_paragraph()
    p_alcance.paragraph_format.space_after = Pt(10)
    r_alcance = p_alcance.add_run(
        "Criterio de Rol Institucional: De acuerdo con la estructura armonizada de ISO/IEC 27701:2025, la UNSA califica primariamente como "
        "Responsable del Tratamiento (PII Controller) sobre los datos de estudiantes, docentes y postulantes. En consecuencia, se activan de "
        "forma obligatoria los controles del Anexo A.1 (Cláusula 7) y los controles comunes de seguridad del Anexo A.3. Los controles del "
        "Anexo A.2 (específicos para Encargados / PII Processors) quedan legalmente excluidos, salvo acuerdos contractuales puntuales."
    )
    r_alcance.font.name = "Calibri"
    r_alcance.font.size = Pt(9.5)
    r_alcance.font.color.rgb = RGBColor(51, 65, 85)

    # 4. SECCIÓN 2: DICTAMEN EJECUTIVO Y DIAGNÓSTICO DE MADUREZ
    resumen = datos_soa.get("resumen", {})
    analisis_texto = datos_soa.get("analisis_ejecutivo")
    if isinstance(analisis_texto, dict):
        analisis_texto = analisis_texto.get("texto", "")

    h2 = doc.add_heading(level=2)
    r_h2 = h2.add_run("2. Dictamen Ejecutivo de Conformidad y Evaluación de Madurez")
    r_h2.font.name = "Calibri"
    r_h2.font.color.rgb = RGBColor(15, 23, 42)

    # Métricas en tabla visual de indicadores
    t_kpi = doc.add_table(rows=2, cols=6)
    t_kpi.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_kpi.autofit = False

    kpi_headers = ["Controles Auditados", "Controles Aplicables", "Conformidad Plena", "En Proceso (Parcial)", "Brechas Críticas", "Excluidos por Rol"]
    kpi_values = [
        str(resumen.get("controles_evaluados", 10)),
        str(resumen.get("aplican", 9)),
        str(resumen.get("implementados", 2)),
        str(resumen.get("parciales", 2)),
        str(resumen.get("no_implementados", 5)),
        str(resumen.get("excluidos", 1))
    ]

    for j in range(6):
        c_h = t_kpi.cell(0, j)
        c_h.text = kpi_headers[j]
        aplicar_estilo_celda(c_h, color_fondo="1E293B", negrita=True, tamano=8, color_texto=(255, 255, 255), alineacion=WD_ALIGN_PARAGRAPH.CENTER)
        
        c_v = t_kpi.cell(1, j)
        c_v.text = kpi_values[j]
        bg_val = "F8FAFC"
        if j == 2: bg_val = "DCFCE7"  # verde
        elif j == 3: bg_val = "FEF9C3"  # amarillo
        elif j == 4: bg_val = "FEE2E2"  # rojo
        aplicar_estilo_celda(c_v, color_fondo=bg_val, negrita=True, tamano=11, color_texto=(15, 23, 42), alineacion=WD_ALIGN_PARAGRAPH.CENTER)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # Texto del Dictamen de Auditoría
    p_dictamen_box = doc.add_paragraph()
    p_dictamen_box.paragraph_format.space_before = Pt(4)
    p_dictamen_box.paragraph_format.space_after = Pt(12)
    
    r_dt_title = p_dictamen_box.add_run("Conclusiones del Comité de Auditoría y Estado de Cumplimiento:\n")
    r_dt_title.font.name = "Calibri"
    r_dt_title.font.bold = True
    r_dt_title.font.size = Pt(9.5)
    r_dt_title.font.color.rgb = RGBColor(30, 41, 59)

    texto_final_dictamen = analisis_texto or (
        "La evaluación cuantitativa revela un nivel de madurez de privacidad en desarrollo para la UNSA. "
        "Si bien la institución cuenta con el registro formal de sus bancos de datos personales (RAT) ante el Ministerio de Justicia "
        "y reglamentos aprobados mediante Resolución del Consejo Universitario (RCU-0127-2020), se detectan deficiencias críticas "
        "en la realización de Evaluaciones de Impacto en la Privacidad (DPIA) para sistemas biométricos y en la formalización de acuerdos "
        "de procesamiento de datos (DPA) con terceros proveedores tecnológicos."
    )
    
    r_dt_body = p_dictamen_box.add_run(texto_final_dictamen)
    r_dt_body.font.name = "Calibri"
    r_dt_body.font.size = Pt(9.5)
    r_dt_body.font.color.rgb = RGBColor(71, 85, 105)

    # 5. SECCIÓN 3: MATRIZ DE DECLARACIÓN DE APLICABILIDAD (SoA)
    h3 = doc.add_heading(level=2)
    r_h3 = h3.add_run("3. Matriz de Aplicabilidad de Controles de Privacidad (ISO/IEC 27701:2025)")
    r_h3.font.name = "Calibri"
    r_h3.font.color.rgb = RGBColor(15, 23, 42)

    columnas = [
        ("Control", 0.75),
        ("Requisito Normativo PIMS", 1.8),
        ("¿Aplica?", 0.65),
        ("Justificación Técnica / Base Legal", 2.2),
        ("Evidencias Documentales Verificadas", 2.0),
        ("Estado de Conformidad", 1.05)
    ]

    filas_soa = datos_soa.get("soa", [])
    tabla_soa = doc.add_table(rows=1 + len(filas_soa), cols=len(columnas))
    tabla_soa.alignment = WD_TABLE_ALIGNMENT.CENTER
    tabla_soa.autofit = False

    for j, (col_nombre, ancho) in enumerate(columnas):
        celda = tabla_soa.cell(0, j)
        celda.width = Inches(ancho)
        celda.text = col_nombre
        aplicar_estilo_celda(celda, color_fondo="1E293B", negrita=True, tamano=8.5, color_texto=(255, 255, 255), alineacion=WD_ALIGN_PARAGRAPH.CENTER)

    for i, f in enumerate(filas_soa, start=1):
        estado = f.get("estado", "no implementado")
        if estado == "implementado":
            bg_estado = "DCFCE7"
            txt_estado = "Conforme"
            color_txt_estado = (22, 101, 52)
        elif estado == "parcial":
            bg_estado = "FEF9C3"
            txt_estado = "En Proceso"
            color_txt_estado = (133, 77, 14)
        elif estado == "no aplica":
            bg_estado = "F1F5F9"
            txt_estado = "Excluido"
            color_txt_estado = (100, 116, 139)
        else:
            bg_estado = "FEE2E2"
            txt_estado = "Brecha"
            color_txt_estado = (153, 27, 27)

        evidencias_lista = f.get("evidencias", [])
        evidencias_str = "\n".join(evidencias_lista) if evidencias_lista else "Sin artefacto probatorio registrado"
        if f.get("politica_relacionada"):
            evidencias_str += f"\n[Directiva: {f.get('politica_relacionada')}]"

        datos_fila = [
            f.get("control", ""),
            f.get("nombre", ""),
            "SÍ" if f.get("aplica") else "NO",
            f.get("justificacion", ""),
            evidencias_str,
            txt_estado
        ]

        for j, texto in enumerate(datos_fila):
            celda = tabla_soa.cell(i, j)
            celda.width = Inches(columnas[j][1])
            celda.text = texto
            if j == 5:
                aplicar_estilo_celda(celda, color_fondo=bg_estado, negrita=True, tamano=8, color_texto=color_txt_estado, alineacion=WD_ALIGN_PARAGRAPH.CENTER)
            elif j == 0:
                aplicar_estilo_celda(celda, color_fondo="F8FAFC", negrita=True, tamano=8, alineacion=WD_ALIGN_PARAGRAPH.CENTER)
            elif j == 2:
                aplicar_estilo_celda(celda, negrita=True, tamano=8, alineacion=WD_ALIGN_PARAGRAPH.CENTER)
            else:
                aplicar_estilo_celda(celda, tamano=8)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # 6. SECCIÓN 4: PLAN DE TRATAMIENTO DE BRECHAS Y ACCIONES CORRECTIVAS (CAPA)
    brechas = datos_soa.get("brechas", [])
    if brechas:
        h4 = doc.add_heading(level=2)
        r_h4 = h4.add_run("4. Plan Prescriptivo de Tratamiento de Brechas Normativas (CAPA)")
        r_h4.font.name = "Calibri"
        r_h4.font.color.rgb = RGBColor(15, 23, 42)

        p_br_intro = doc.add_paragraph()
        p_br_intro.paragraph_format.space_after = Pt(6)
        r_bi = p_br_intro.add_run(
            "Con el fin de mitigar los riesgos de sanciones legales bajo la Ley N° 29733 y alcanzar la conformidad previa a la "
            "auditoría externa de certificación, se asignan de forma prescriptiva las siguientes acciones correctivas inmediatas:"
        )
        r_bi.font.name = "Calibri"
        r_bi.font.size = Pt(9.5)
        r_bi.font.color.rgb = RGBColor(51, 65, 85)

        t_br = doc.add_table(rows=1 + len(brechas), cols=4)
        t_br.alignment = WD_TABLE_ALIGNMENT.CENTER
        t_br.autofit = False

        cols_b = [("Control", 0.9), ("Requisito Normativo Incumplido", 2.6), ("Estado Actual", 1.2), ("Área Responsable de Remediación", 2.4)]
        for j, (cb, wb) in enumerate(cols_b):
            c = t_br.cell(0, j)
            c.width = Inches(wb)
            c.text = cb
            aplicar_estilo_celda(c, color_fondo="334155", negrita=True, tamano=8.5, color_texto=(255, 255, 255), alineacion=WD_ALIGN_PARAGRAPH.CENTER)

        for i, b in enumerate(brechas, start=1):
            t_br.cell(i, 0).text = b.get("control", "")
            t_br.cell(i, 1).text = b.get("nombre", "")
            t_br.cell(i, 2).text = "No Conforme" if b.get("estado") == "no implementado" else "En Revisión"
            t_br.cell(i, 3).text = b.get("solicitar_a", "").replace("Agente de ", "Dirección Universitaria de ")
            
            aplicar_estilo_celda(t_br.cell(i, 0), color_fondo="FFF1F2", negrita=True, tamano=8, alineacion=WD_ALIGN_PARAGRAPH.CENTER)
            aplicar_estilo_celda(t_br.cell(i, 1), tamano=8)
            aplicar_estilo_celda(t_br.cell(i, 2), tamano=8, color_texto=(153, 27, 27), negrita=True, alineacion=WD_ALIGN_PARAGRAPH.CENTER)
            aplicar_estilo_celda(t_br.cell(i, 3), tamano=8, negrita=True)

        doc.add_paragraph().paragraph_format.space_after = Pt(14)

    # 7. SECCIÓN 5: GOBERNANZA, SUPERVISIÓN Y APROBACIÓN INSTITUCIONAL
    h5 = doc.add_heading(level=2)
    r_h5 = h5.add_run("5. Gobernanza, Aprobación Institucional y Firmas de Responsabilidad")
    r_h5.font.name = "Calibri"
    r_h5.font.color.rgb = RGBColor(15, 23, 42)

    p_gob = doc.add_paragraph()
    p_gob.paragraph_format.space_after = Pt(25)
    r_gt = p_gob.add_run(
        "El presente informe de Declaración de Aplicabilidad ha sido emitido con rigor técnico metodológico. "
        "En cumplimiento del principio de gobernanza institucional y responsabilidad demostrada (Accountability), "
        "el documento adquiere validez jurídica y ejecutiva con el refrendo de las autoridades competentes de la "
        "Universidad Nacional de San Agustín de Arequipa."
    )
    r_gt.font.name = "Calibri"
    r_gt.font.size = Pt(9)
    r_gt.font.color.rgb = RGBColor(100, 116, 139)

    t_firmas = doc.add_table(rows=2, cols=3)
    t_firmas.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_firmas.autofit = False

    t_firmas.cell(0, 0).text = "____________________________________\nMg. Edward Vicente Zárate Carlos\nAuditor Líder / Cátedra de Auditoría\nEPIS — UNSA"
    t_firmas.cell(0, 1).text = "____________________________________\nOficial de Protección de Datos (DPO)\nOficialía de Privacidad\nUNSA"
    t_firmas.cell(0, 2).text = "____________________________________\nDirector General de OTIC\nDirección Universitaria de TIC\nUNSA"
    
    t_firmas.cell(1, 0).text = "Fecha: ____ / ____ / 2026"
    t_firmas.cell(1, 1).text = "Fecha: ____ / ____ / 2026"
    t_firmas.cell(1, 2).text = "Fecha: ____ / ____ / 2026"

    for r in range(2):
        for c in range(3):
            aplicar_estilo_celda(t_firmas.cell(r, c), tamano=8, color_texto=(70, 70, 70), alineacion=WD_ALIGN_PARAGRAPH.CENTER)

    doc.save(ruta_salida)
    return ruta_salida


if __name__ == "__main__":
    from agents.controles import AgenteControles
    agente = AgenteControles()
    entrada_ejemplo = {
        "operacion": "generar_soa",
        "perfil": {"organizacion": "Universidad Nacional de San Agustín (UNSA)", "rol": "responsable"},
        "riesgos": [
            {"id": "R-UNSA-01", "controles": ["A.1.2.6"]},
            {"id": "R-UNSA-02", "controles": ["A.1.2.6", "A.1.3.7"]}
        ],
        "evidencias": [
            {"control": "A.1.2.2", "descripcion": "RCU-0127-2020 Reglamento Matrícula", "estado": "implementado"},
            {"control": "A.1.2.9", "descripcion": "RCU-0009-2026 Registro RAT Nacional", "estado": "implementado"},
            {"control": "A.1.2.6", "descripcion": "Borrador DPIA Comedor Universitario", "estado": "parcial"},
            {"control": "A.3.11", "descripcion": "Protocolo CSIRT en revisión", "estado": "parcial"}
        ]
    }
    resultado = agente.ejecutar(entrada_ejemplo)
    ruta = generar_documento_soa(resultado["datos"])
    print(f"Documento SoA ISO 27701 generado exitosamente en: {ruta}")

#!/usr/bin/env python3
"""
construir_referencia.py — Evaluaciones de referencia de los 5 contratos supuestos de la UNSA.

    python pims-dpa-auditor_pruebas/unsa/construir_referencia.py [--fecha-ref 2026-10-13]

Para cada contrato define, control por control, la calificación que daría un auditor aplicando
literalmente references/criterios_semaforo.md (calibrada con los casos de referencia de la v1.1).
Luego:
  1. Verifica que cada cita exista textualmente en el contrato y tenga 20 palabras o menos.
  2. Escribe referencia/ref_<caso>.json: lo que debería entregar un modelo ideal (sin campos calculados).
  3. Ejecuta scripts/calcular_resultado.py --org organizaciones/unsa y escribe esperado/esperado_<caso>.json.

Controles "discutibles": cuando un auditor razonable podría calificar distinto, se registra la
alternativa aceptable en `_alternativas`. comparar_con_referencia.py los cuenta aparte.

Estas evaluaciones las redactó el asistente de IA a partir de los criterios de la skill:
el grupo debe revisarlas antes de usarlas como verdad de referencia en el informe.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
TITULOS = {'A.2.2.2': 'Acuerdo con el cliente', 'A.2.2.3': 'Fines de la organización', 'A.2.2.4': 'Uso para marketing y publicidad',
           'A.2.2.5': 'Instrucción infractora', 'A.2.2.6': 'Obligaciones del cliente', 'A.2.2.7': 'Registros del tratamiento',
           'A.2.3.2': 'Obligaciones con titulares', 'A.2.4.2': 'Archivos temporales', 'A.2.4.3': 'Devolución o eliminación',
           'A.2.4.4': 'Controles de transmisión', 'A.2.5.2': 'Base para transferencias', 'A.2.5.3': 'Países destino',
           'A.2.5.4': 'Registros de comunicaciones', 'A.2.5.5': 'Aviso de solicitudes de autoridades',
           'A.2.5.6': 'Comunicaciones legalmente vinculantes', 'A.2.5.7': 'Divulgación de subcontratistas',
           'A.2.5.8': 'Contratación de subcontratistas', 'A.2.5.9': 'Cambio de subcontratista', 'A.3.9': 'Derechos de acceso',
           'A.3.10': 'Seguridad en acuerdos con proveedores', 'A.3.11': 'Planificación de incidentes',
           'A.3.12': 'Respuesta a incidentes', 'A.3.13': 'Requisitos legales', 'A.3.15': 'Revisión independiente',
           'A.3.18': 'Acuerdos de confidencialidad', 'A.3.24': 'Respaldo de información'}
C, P, NC, SE = "Cumple", "Parcial", "No cumple", "Sin evidencia"
ISO, MIX = "ISO 27701", "Mixta"
NL = "No localizada"


def ctl(estado, clausula=NL, evidencia="", fuente=ISO, obs="", alt=None):
    return {"estado": estado, "clausula_dpa": clausula, "evidencia": evidencia, "fuente_requisito": fuente,
            "observacion": obs, "_alternativas": alt or []}


CASOS = {
    # ------------------------------------------------------------------ 1. Aula virtual
    "unsa_01_aula_virtual": {
        "proveedor": "Plataforma Aprende Andes S.A.C.",
        "id": "DPA-20261013-PAA",
        "riesgo": "Alto",
        "tercero": {"rol": "Encargado", "servicio": "Plataforma de aula virtual (pregrado y posgrado)",
                    "paises_tratamiento": ["Perú", "Estados Unidos"],
                    "categorias_datos": ["Identificativos", "Académicos (calificaciones, trabajos)", "Registros de actividad", "Datos de menores de edad"],
                    "subencargados": [{"nombre": "CloudCore Inc.", "pais": "Estados Unidos", "servicio": "Alojamiento", "garantias_transferencia": False},
                                      {"nombre": "MailFlow LLC", "pais": "Estados Unidos", "servicio": "Envío de notificaciones", "garantias_transferencia": False}]},
        "contrato": {"fecha_firma": None, "fecha_vigencia_inicio": "2026-03-01", "fecha_vigencia_fin": "2027-02-28",
                     "renovacion_automatica": True, "preaviso_terminacion_dias": 30},
        "certificaciones": [{"nombre": "ISO/IEC 27001:2022", "tipo": "Aceptada", "estado": "Verificada con evidencia", "vencida": False,
                             "fecha_vencimiento": "2027-08-31", "observacion": "Certificado anexo (Anexo B) con alcance declarado."}],
        "uso_ia": {"detectado": True, "descripcion": "Entrenamiento de modelos de recomendación y analítica de aprendizaje con registros seudonimizados",
                   "limitado_a_fines_responsable": False, "evidencia_gobernanza_ia": "No presentada"},
        "controles": {
            "A.2.2.2": ctl(C, "1", "conforme a sus instrucciones documentadas en el Anexo A", obs="Instrucciones documentadas, anexo de tratamiento y asistencia definida.", alt=[P]),
            "A.2.2.3": ctl(NC, "3", "para entrenar y mejorar sus modelos de recomendación y analítica de aprendizaje, que ofrece a otros clientes", MIX,
                           "Fines propios (entrenamiento de IA para otros clientes); la seudonimización no elimina el dato personal."),
            "A.2.2.4": ctl(C, "3", "no utilizará los datos con fines publicitarios ni de marketing"),
            "A.2.2.5": ctl(SE, obs="Sin deber de avisar instrucciones infractoras."),
            "A.2.2.6": ctl(C, "4", "permitirá una auditoría anual de la UNSA o de un tercero designado"),
            "A.2.2.7": ctl(C, "5", "mantendrá un registro de las actividades de tratamiento realizadas por cuenta de la UNSA"),
            "A.2.3.2": ctl(P, "6", "colaborará en su atención dentro de los 10 días hábiles siguientes", MIX, "10 días hábiles superan el máximo interno de 5."),
            "A.2.4.2": ctl(SE, obs="Sin plazo para archivos temporales."),
            "A.2.4.3": ctl(P, "8", "incluidas las copias de respaldo, dentro de los 60 días siguientes", MIX, "60 días superan el máximo interno de 30."),
            "A.2.4.4": ctl(C, "7", "Toda transmisión de datos se realiza con cifrado TLS 1.2 o superior"),
            "A.2.5.2": ctl(NC, "9", "que aplica medidas de seguridad adecuadas", MIX, "Transferencia a EE. UU. sin garantías contractuales ni mecanismo identificado."),
            "A.2.5.3": ctl(P, "9, 10", "Los datos se alojan en centros de datos de CloudCore Inc. en Estados Unidos", MIX,
                           "Lista concreta, pero el país está fuera de los aprobados y sin garantías."),
            "A.2.5.4": ctl(SE),
            "A.2.5.5": ctl(C, "11", "lo comunicará a la UNSA antes de entregar información, salvo prohibición legal"),
            "A.2.5.6": ctl(P, "11", "lo comunicará a la UNSA antes de entregar información", obs="No obliga a rechazar requerimientos no vinculantes ni a entregar solo lo exigido.", alt=[SE]),
            "A.2.5.7": ctl(C, "10", "CloudCore Inc., alojamiento, Estados Unidos; MailFlow LLC, envío de notificaciones, Estados Unidos"),
            "A.2.5.8": ctl(C, "10", "asume por contrato escrito obligaciones de protección equivalentes a las de este acuerdo"),
            "A.2.5.9": ctl(P, "10", "comunicándolo a la UNSA con 15 días de anticipación", MIX, "15 días son menos que los 30 de la política interna."),
            "A.3.9": ctl(C, "12", "El acceso a los datos se limita al personal del Proveedor que lo requiera"),
            "A.3.10": ctl(NC, "13", "dentro de las 72 horas de conocida", MIX, "72 h superan el máximo interno de 24 h (la UNSA debe notificar a la ANPD en 48 h)."),
            "A.3.11": ctl(C, "13", "cuenta con un procedimiento de respuesta a incidentes de seguridad"),
            "A.3.12": ctl(C, "13", "indicando su naturaleza, los datos y titulares afectados, las medidas adoptadas y un punto de contacto", MIX,
                          "Contenido mínimo y cooperación completos; el plazo se evalúa en A.3.10.", alt=[P]),
            "A.3.13": ctl(C, "14", "se obliga a cumplir la Ley N.° 29733, Ley de Protección de Datos Personales, y su Reglamento", MIX),
            "A.3.15": ctl(C, "4", "certificado ISO/IEC 27001:2022 vigente hasta el 31 de agosto de 2027"),
            "A.3.18": ctl(C, "12", "sujeto a obligaciones de confidencialidad que subsisten después de terminado el contrato"),
            "A.3.24": ctl(P, "8", "incluidas las copias de respaldo, dentro de los 60 días siguientes", obs="Elimina los respaldos al término, pero no informa los límites del servicio de respaldo ni la restauración.", alt=[SE]),
        },
        "alertas": [
            ("Alta", "Riesgo", "Uso de registros de actividad para entrenar modelos de IA ofrecidos a otros clientes (fines propios).", ["A.2.2.3"]),
            ("Alta", "Seguridad", "Aviso de incidentes en 72 h, mayor al máximo interno de 24 h.", ["A.3.10"]),
            ("Alta", "Riesgo", "Alojamiento y sub-encargados en EE. UU. (fuera de países aprobados) sin garantías contractuales.", ["A.2.5.2", "A.2.5.3"]),
            ("Media", "Riesgo", "Uso de IA sobre los datos sin evidencia de gobernanza de IA.", ["A.2.2.3"]),
        ],
    },
    # ------------------------------------------------------------------ 2. Laboratorio clínico
    "unsa_02_laboratorio_clinico": {
        "proveedor": "Laboratorio Clínico Misti S.A.C.",
        "id": "DPA-20261013-LCM",
        "riesgo": "Alto",
        "tercero": {"rol": "Encargado", "servicio": "Análisis clínicos para el servicio médico universitario", "paises_tratamiento": ["Perú"],
                    "categorias_datos": ["Datos de salud (sensibles)", "Identificativos"], "subencargados": []},
        "contrato": {"fecha_firma": None, "fecha_vigencia_inicio": "2026-01-01", "fecha_vigencia_fin": "2026-12-31",
                     "renovacion_automatica": False, "preaviso_terminacion_dias": None},
        "certificaciones": [{"nombre": "ISO 15189", "tipo": "No reconocida", "estado": "Declarada sin evidencia", "vencida": None,
                             "fecha_vencimiento": None, "observacion": "Acreditación de calidad analítica; no figura entre las certificaciones aceptadas."}],
        "uso_ia": {"detectado": "No indicado"},
        "controles": {
            "A.2.2.2": ctl(P, "1", "según las instrucciones escritas de la UNSA", obs="Objeto e instrucciones, pero sin anexo de categorías ni asistencia al Responsable.", alt=[C]),
            "A.2.2.3": ctl(C, "1, 2", "no utilizará los datos ni las muestras para investigación, fines comerciales o propios"),
            "A.2.2.4": ctl(C, "2", "ni para publicidad o marketing"),
            "A.2.2.5": ctl(C, "3", "informará de inmediato a la UNSA si considera que una instrucción vulnera la normativa"),
            "A.2.2.6": ctl(C, "4", "permitirá visitas de verificación coordinadas con cinco días de anticipación"),
            "A.2.2.7": ctl(SE),
            "A.2.3.2": ctl(C, "5", "en un plazo máximo de 5 días hábiles", MIX),
            "A.2.4.2": ctl(SE),
            "A.2.4.3": ctl(P, "7", "eliminará la información que no esté obligado a conservar", MIX,
                           "Conservación legal sanitaria razonable, pero sin plazo de eliminación ni certificado."),
            "A.2.4.4": ctl(C, "6", "a través de una plataforma web con conexión cifrada (HTTPS)", obs="Cubre la entrega de resultados.", alt=[P]),
            "A.2.5.2": ctl(C, "8", "requerirá autorización previa y por escrito de la UNSA", MIX, alt=[P]),
            "A.2.5.3": ctl(C, "8", "Los datos se tratan exclusivamente en el Perú", MIX),
            "A.2.5.4": ctl(SE),
            "A.2.5.5": ctl(SE),
            "A.2.5.6": ctl(SE),
            "A.2.5.7": ctl(NC, "9", "laboratorios de referencia nacionales cuando el análisis lo requiera", obs="Sin lista de sub-encargados (nombre, servicio, país)."),
            "A.2.5.8": ctl(P, "9", "los que guardarán confidencialidad sobre la información recibida", obs="Autorización general; solo confidencialidad, sin obligaciones equivalentes por escrito."),
            "A.2.5.9": ctl(NC, "9", obs="Sin aviso previo de cambios ni derecho de objeción."),
            "A.3.9": ctl(SE, obs="Sin limitación del acceso a los datos (la confidencialidad del personal se evalúa en A.3.18)."),
            "A.3.10": ctl(NC, "11", "dentro de las 48 horas de conocido", MIX, "48 h superan el máximo interno de 24 h."),
            "A.3.11": ctl(SE),
            "A.3.12": ctl(P, "11", "notificará a la UNSA cualquier incidente que comprometa datos de pacientes", MIX, "Sin contenido mínimo del aviso ni cooperación."),
            "A.3.13": ctl(C, "12", "se rige por la Ley N.° 29733 y su Reglamento", MIX),
            "A.3.15": ctl(SE, "4", "declara contar con acreditación ISO 15189", obs="Acreditación no reconocida y sin evidencia; no hay informe independiente.", alt=[P]),
            "A.3.18": ctl(P, "10", "El personal del Laboratorio está sujeto al secreto profesional", obs="Secreto profesional del personal y confidencialidad de los laboratorios de referencia; sin duración ni deber de cumplir las políticas de protección de datos.", alt=[C]),
            "A.3.24": ctl(SE, obs="Sin condiciones de respaldo ni de eliminación de datos en respaldos."),
        },
        "alertas": [
            ("Alta", "Seguridad", "Aviso de incidentes en 48 h, mayor al máximo interno de 24 h; datos de salud.", ["A.3.10", "A.3.12"]),
        ],
    },
    # ------------------------------------------------------------------ 3. Pasarela de pagos
    "unsa_03_pasarela_pagos": {
        "proveedor": "Recaudo Sur Pagos S.A.",
        "id": "DPA-20261013-RSP",
        "riesgo": "Alto",
        "tercero": {"rol": "Encargado", "servicio": "Pasarela de pagos en línea (admisión, matrícula, trámites)", "paises_tratamiento": ["Perú", "Irlanda"],
                    "categorias_datos": ["Identificativos", "Datos de pago (tokenizados)"],
                    "subencargados": [{"nombre": "AntiFraude Europa Ltd.", "pais": "Irlanda", "servicio": "Prevención de fraude", "garantias_transferencia": True}]},
        "contrato": {"fecha_firma": "2026-02-20", "fecha_vigencia_inicio": "2026-03-01", "fecha_vigencia_fin": "2027-02-28",
                     "renovacion_automatica": True, "preaviso_terminacion_dias": 90},
        "certificaciones": [{"nombre": "SOC 2 Tipo II", "tipo": "Aceptada", "estado": "Verificada con evidencia", "vencida": True,
                             "fecha_vencimiento": None, "observacion": "Período cerrado el 31/03/2025: más de 12 meses de antigüedad."}],
        "uso_ia": {"detectado": False, "descripcion": "La cláusula 2 declara que no aplica IA sobre los datos", "limitado_a_fines_responsable": True,
                   "evidencia_gobernanza_ia": "No requerida"},
        "controles": {
            "A.2.2.2": ctl(C, "1", "solo según las instrucciones documentadas del Anexo 1"),
            "A.2.2.3": ctl(C, "2", "Se prohíbe su uso para fines propios, analítica, entrenamiento de modelos de IA"),
            "A.2.2.4": ctl(C, "2", "marketing o publicidad"),
            "A.2.2.5": ctl(C, "3", "avisará de inmediato si una instrucción infringe la Ley N.° 29733"),
            "A.2.2.6": ctl(C, "4", "permite auditorías con preaviso de 10 días hábiles"),
            "A.2.2.7": ctl(C, "4", "mantiene un registro de las actividades de tratamiento por cuenta del Responsable"),
            "A.2.3.2": ctl(C, "5", "asistirá en su atención en un máximo de 5 días hábiles", MIX),
            "A.2.4.2": ctl(C, "6", "Los archivos temporales se eliminan en 7 días"),
            "A.2.4.3": ctl(C, "7", "devolverá o eliminará los datos y respaldos en 30 días y emitirá certificado de eliminación", MIX),
            "A.2.4.4": ctl(C, "6", "Toda transmisión se cifra con TLS 1.2 o superior"),
            "A.2.5.2": ctl(C, "8", "cláusulas contractuales que imponen protección equivalente a la Ley N.° 29733", MIX),
            "A.2.5.3": ctl(C, "8", "Los datos se tratan solo en Perú e Irlanda (Anexo 2)", MIX),
            "A.2.5.4": ctl(C, "9", "Registra toda comunicación a terceros"),
            "A.2.5.5": ctl(C, "9", "notificará al Responsable antes de comunicar, salvo prohibición legal"),
            "A.2.5.6": ctl(C, "9", "rechazará los no vinculantes y solo entregará lo legalmente exigido"),
            "A.2.5.7": ctl(C, "10", "AntiFraude Europa Ltd., prevención de fraude, Irlanda"),
            "A.2.5.8": ctl(C, "10", "Todo sub-encargado firma contrato con obligaciones equivalentes"),
            "A.2.5.9": ctl(C, "10", "Cambios con aviso previo de 30 días y derecho de objeción", MIX),
            "A.3.9": ctl(C, "11", "Acceso limitado al personal que lo necesita"),
            "A.3.10": ctl(C, "12", "notificará al Responsable en máximo 24 horas", MIX),
            "A.3.11": ctl(C, "12", "mantiene un procedimiento de gestión de incidentes"),
            "A.3.12": ctl(C, "12", "indicando naturaleza, datos y titulares afectados, consecuencias, medidas y contacto", MIX),
            "A.3.13": ctl(C, "13", "Cumplirá la Ley N.° 29733 y su Reglamento (D.S. 016-2024-JUS)", MIX),
            "A.3.15": ctl(P, "4", "corresponde al período cerrado el 31 de marzo de 2025", MIX,
                          "Informe SOC 2 Tipo II con más de 12 meses: vencido según la política interna.", alt=[SE]),
            "A.3.18": ctl(C, "11", "con confidencialidad que subsiste tras la relación"),
            "A.3.24": ctl(C, "6", "Respaldos diarios cifrados, conservados 30 días, con restauración en máximo 24 horas"),
        },
        "alertas": [
            ("Media", "Renovación", "Informe SOC 2 Tipo II con antigüedad mayor a 12 meses (período cerrado el 31/03/2025).", ["A.3.15"]),
        ],
    },
    # ------------------------------------------------------------------ 4. Videovigilancia
    "unsa_04_videovigilancia": {
        "proveedor": "Seguridad Integral Characato S.A.C.",
        "id": "DPA-20261013-SIC",
        "riesgo": "Alto",
        "tercero": {"rol": "Encargado", "servicio": "Seguridad y videovigilancia con centro de monitoreo", "paises_tratamiento": ["Perú (Supuesto)"],
                    "categorias_datos": ["Imágenes", "Datos biométricos (reconocimiento facial)"], "subencargados": []},
        "contrato": {"fecha_firma": None, "fecha_vigencia_inicio": "2025-07-01", "fecha_vigencia_fin": "2026-06-30",
                     "renovacion_automatica": False, "preaviso_terminacion_dias": None},
        "certificaciones": [],
        "uso_ia": {"detectado": True, "descripcion": "Analítica de video y reconocimiento facial; mejora de algoritmos propios con las grabaciones",
                   "limitado_a_fines_responsable": False, "evidencia_gobernanza_ia": "No presentada"},
        "controles": {
            "A.2.2.2": ctl(NC, "Primera", "determinará la ubicación de las cámaras y la configuración de las grabaciones según su experiencia",
                           obs="El tratamiento lo define el proveedor, no instrucciones documentadas del Responsable.", alt=[P]),
            "A.2.2.3": ctl(NC, "Tercera", "podrá utilizarlas para mejorar sus algoritmos de analítica", MIX, "Fines propios con datos biométricos."),
            "A.2.2.4": ctl(SE),
            "A.2.2.5": ctl(SE),
            "A.2.2.6": ctl(SE),
            "A.2.2.7": ctl(SE),
            "A.2.3.2": ctl(SE),
            "A.2.4.2": ctl(SE),
            "A.2.4.3": ctl(NC, "Séptima", "el Contratista retirará sus equipos", MIX, "Sin devolución ni eliminación de grabaciones al término."),
            "A.2.4.4": ctl(SE, "Cuarta", obs="Acceso remoto sin medidas de protección de la transmisión.", alt=[P]),
            "A.2.5.2": ctl(SE),
            "A.2.5.3": ctl(NC, obs="Sin lista de países de tratamiento."),
            "A.2.5.4": ctl(SE),
            "A.2.5.5": ctl(SE),
            "A.2.5.6": ctl(SE),
            "A.2.5.7": ctl(NC, "Sexta", "podrá subcontratar el mantenimiento de los equipos", obs="Sin lista de sub-encargados."),
            "A.2.5.8": ctl(NC, "Sexta", "podrá subcontratar el mantenimiento de los equipos", obs="Autorización general sin condiciones ni obligaciones equivalentes."),
            "A.2.5.9": ctl(NC, obs="Sin aviso de cambios."),
            "A.3.9": ctl(SE, obs="Acceso remoto amplio a cámaras y grabaciones (cláusula cuarta) sin reglas de control de acceso.", alt=[NC]),
            "A.3.10": ctl(NC, obs="Sin requisitos de seguridad ni aviso de incidentes."),
            "A.3.11": ctl(SE),
            "A.3.12": ctl(NC, obs="Sin aviso ni contenido mínimo."),
            "A.3.13": ctl(P, "Octava", "se rige por la normativa de contrataciones del Estado", MIX,
                          "Identifica normativa aplicable, pero no la de protección de datos.", alt=[SE]),
            "A.3.15": ctl(SE),
            "A.3.18": ctl(P, "Quinta", "guardará reserva sobre lo observado en el ejercicio de sus funciones", obs="Reserva limitada a lo observado, sin duración ni alcance a los datos y grabaciones."),
            "A.3.24": ctl(SE, obs="Conserva grabaciones 180 días, pero no hay condiciones de respaldo ni de su eliminación."),
        },
        "alertas": [
            ("Alta", "Riesgo", "El proveedor puede usar las grabaciones (biométricas) para mejorar sus algoritmos: fines propios.", ["A.2.2.3"]),
            ("Alta", "Seguridad", "Sin obligación de aviso de incidentes.", ["A.3.10", "A.3.12"]),
            ("Alta", "Riesgo", "Sin obligación de devolver o eliminar las grabaciones al término.", ["A.2.4.3"]),
            ("Media", "Riesgo", "Reconocimiento facial y analítica de video sin evidencia de gobernanza de IA.", ["A.2.2.3"]),
            ("Media", "Riesgo", "Sin derecho de auditoría ni informes independientes.", ["A.2.2.6", "A.3.15"]),
        ],
    },
    # ------------------------------------------------------------------ 5. Soporte del sistema académico (contrato público)
    "unsa_05_soporte_sistema_academico": {
        "proveedor": "Ingeniería de Software Altoandino S.A.C.",
        "id": "DPA-20261013-ISA",
        "riesgo": "Medio",
        "tercero": {"rol": "Encargado", "servicio": "Mantenimiento y soporte del Sistema de Gestión Académica (acceso remoto a producción)",
                    "paises_tratamiento": ["Perú (Supuesto)"], "categorias_datos": ["Identificativos", "Registros académicos"], "subencargados": []},
        "contrato": {"fecha_firma": None, "fecha_vigencia_inicio": "2026-02-01", "fecha_vigencia_fin": "2027-01-31",
                     "renovacion_automatica": False, "preaviso_terminacion_dias": None},
        "certificaciones": [],
        "uso_ia": {"detectado": "No indicado"},
        "controles": {
            "A.2.2.2": ctl(P, "segunda", "contará con acceso remoto a los servidores y bases de datos de producción",
                           obs="Objeto definido, pero sin instrucciones de tratamiento ni categorías.", alt=[NC]),
            "A.2.2.3": ctl(NC, obs="La reserva no limita el uso a los fines de la UNSA."),
            "A.2.2.4": ctl(SE),
            "A.2.2.5": ctl(SE),
            "A.2.2.6": ctl(SE, obs="La conformidad del servicio no es un derecho de auditoría."),
            "A.2.2.7": ctl(SE),
            "A.2.3.2": ctl(SE),
            "A.2.4.2": ctl(SE),
            "A.2.4.3": ctl(P, "novena", "entregará toda la documentación técnica y la información generada", MIX,
                           "Devolución sin plazo; sin eliminación ni certificado."),
            "A.2.4.4": ctl(SE, obs="Acceso remoto sin medidas de transmisión."),
            "A.2.5.2": ctl(SE),
            "A.2.5.3": ctl(NC, obs="Sin lista de países."),
            "A.2.5.4": ctl(SE),
            "A.2.5.5": ctl(SE),
            "A.2.5.6": ctl(SE),
            "A.2.5.7": ctl(C, "undécima", "sin autorización previa y escrita de la Entidad",
                           obs="Prohíbe subcontratar sin autorización previa: la UNSA conoce al sub-encargado antes de su uso.", alt=[NC]),
            "A.2.5.8": ctl(P, "undécima", "no podrá subcontratar total ni parcialmente la ejecución del servicio",
                           obs="Autorización específica, pero sin obligaciones equivalentes por escrito.", alt=[C]),
            "A.2.5.9": ctl(C, "undécima", "sin autorización previa y escrita de la Entidad",
                           obs="Todo cambio requiere autorización previa.", alt=[NC]),
            "A.3.9": ctl(SE, obs="Acceso remoto a producción sin reglas de control de acceso (la reserva se evalúa en A.3.18)."),
            "A.3.10": ctl(NC, obs="Sin requisitos de seguridad ni aviso de incidentes."),
            "A.3.11": ctl(SE),
            "A.3.12": ctl(NC),
            "A.3.13": ctl(C, "décima", "cumplirá lo dispuesto en la Ley N.° 29733, Ley de Protección de Datos Personales", MIX),
            "A.3.15": ctl(SE),
            "A.3.18": ctl(P, "octava", "guardar reserva absoluta sobre la información a la que tenga acceso", obs="Obliga al Contratista, no se extiende expresamente a su personal.", alt=[C]),
            "A.3.24": ctl(SE, obs="Sin condiciones de respaldo pese al acceso a bases de datos de producción."),
        },
        "alertas": [
            ("Alta", "Seguridad", "Sin obligación de aviso de incidentes, con acceso remoto a bases de datos de producción.", ["A.3.10", "A.3.12"]),
            ("Media", "Riesgo", "Sin derecho de auditoría ni informes independientes.", ["A.2.2.6", "A.3.15"]),
        ],
    },
}


def construir(caso, d, fecha):
    texto = (AQUI / "contratos" / f"{caso}.md").read_text(encoding="utf-8")
    plano = re.sub(r"\s+", " ", texto.replace("**", ""))
    errores = []
    controles = []
    assert list(d["controles"]) == list(TITULOS), f"{caso}: faltan o sobran controles"
    for cid, c in d["controles"].items():
        ev = c["evidencia"]
        if ev and ev not in plano:
            errores.append(f"{caso} {cid}: la cita no está en el contrato: «{ev}»")
        if len(ev.split()) > 20:
            errores.append(f"{caso} {cid}: la cita tiene {len(ev.split())} palabras")
        controles.append({"control": cid, "titulo": TITULOS[cid], "ambito": "Insumo SoA (Agente 3)", "clausula_dpa": c["clausula_dpa"],
                          "evidencia": ev or "—", "estado": c["estado"], "severidad": "Ninguna", "fuente_requisito": c["fuente_requisito"],
                          "observacion": c["observacion"], "_alternativas": c["_alternativas"]})
    res = {
        "id_evaluacion": d["id"], "fecha": fecha, "norma_referencia": "ISO/IEC 27701:2025",
        "marco_legal": ["Ley N.° 29733", "D.S. 016-2024-JUS"],
        "tercero": dict({"id_tercero": None, "nombre": d["proveedor"], "encargado_principal": None}, **d["tercero"]),
        "contrato": dict({"id_contrato": None, "version_documento": None, "hash_documento_sha256": None, "estado_dpa": "Pendiente DPO"}, **d["contrato"]),
        "nivel_riesgo_pii": d["riesgo"], "certificaciones": d["certificaciones"], "uso_ia": d["uso_ia"],
        "controles": controles,
        "alertas": [{"prioridad": p, "tipo": t, "descripcion": s, "controles_relacionados": rel, "origen": "modelo"} for p, t, s, rel in d["alertas"]],
        "remediacion": [{"control": c["control"], "accion": f"Enmendar: {c['observacion'] or c['titulo']}",
                         "clausula_propuesta": "Plantilla baseline", "prioridad": "Alta" if c["estado"] == NC else "Media"}
                        for c in controles if c["estado"] != C],
        "supuestos": ["Contrato ficticio de pruebas (Etapa 4)", "Evaluación de referencia redactada a partir de criterios_semaforo.md; revisar por el grupo"],
        "trazabilidad": {"version_skill": "2.0", "version_config": "2.0", "evaluador": "Referencia (criterios de la skill aplicados manualmente)",
                         "calculo": "script"},
    }
    return res, errores


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fecha-ref", default="2026-10-13")
    a = ap.parse_args()
    todos = []
    resumen = []
    for caso, d in CASOS.items():
        res, err = construir(caso, d, a.fecha_ref)
        todos += err
        ref = AQUI / "referencia" / f"ref_{caso}.json"
        ref.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
        esp = AQUI / "esperado" / f"esperado_{caso}.json"
        p = subprocess.run([sys.executable, str(RAIZ / "pims-dpa-auditor/scripts/calcular_resultado.py"), str(ref),
                            "--org", str(RAIZ / "organizaciones/unsa"), "--documento", str(AQUI / "contratos" / f"{caso}.md"),
                            "--fecha-ref", a.fecha_ref, "--salida", str(esp)], capture_output=True, text=True, encoding="utf-8")
        if p.returncode:
            todos.append(f"{caso}: calcular_resultado.py falló:\n{p.stdout}{p.stderr}")
            continue
        e = json.loads(esp.read_text(encoding="utf-8"))
        disc = sum(1 for c in e["controles"] if c.get("_alternativas"))
        resumen.append((caso, d["proveedor"], e["nivel_riesgo_pii"], e["resumen"], e["puntaje_proveedor"], e["dictamen"], disc,
                        [a2["descripcion"] for a2 in e["alertas"] if a2["origen"] == "script"]))
    if todos:
        print("ERRORES:\n  " + "\n  ".join(todos))
        sys.exit(1)
    print(f"Referencias de la UNSA (fecha de referencia {a.fecha_ref})\n")
    for caso, prov, riesgo, s, p, dic, disc, renov in resumen:
        print(f"{caso}\n  {prov} · riesgo {riesgo} · 🟢{s['cumple']} 🟡{s['parcial']} 🔴{s['no_cumple']} ⚪{s['sin_evidencia']}"
              f" · {s['alertas_altas']} alertas altas\n  {p['valor']}/100 ({p['banda']}, base {p['base']} − {p['penalizacion']}) · {dic}"
              f" · {disc} controles discutibles" + (f"\n  renovación: {'; '.join(renov)}" if renov else ""))
    print("\nTodas las citas verificadas contra el texto de los contratos (≤ 20 palabras).")


if __name__ == "__main__":
    main()

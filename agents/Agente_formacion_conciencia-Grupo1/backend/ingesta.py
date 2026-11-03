import os
import uuid
from pathlib import Path
from config import KNOWLEDGE_BASE_PATH
from rag import col_normas_iso, col_politicas_negocio

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

def chunk_text(text: str, chunk_size: int = 1500, overlap: int = 150) -> list[str]:
    chunks = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == text_len:
            break
        start += chunk_size - overlap
    return chunks

DOCUMENTOS_SEMILLA_NORMAS = [
    {
        "doc_id": "ISO_27701_2025_RESUMEN",
        "fuente": "ISO/IEC 27701:2025 - Gestión de la Privacidad de la Información (PIMS)",
        "contenido": (
            "La norma internacional ISO/IEC 27701:2025 especifica los requisitos y directrices para establecer, "
            "implementar, mantener y mejorar continuamente un Sistema de Gestión de Información de Privacidad (PIMS). "
            "El Control A.3.17 exige que todo el personal de la organización reciba formación continua y concienciación apropiada "
            "en materia de privacidad antes de acceder a datos personales o procesar información sensible. "
            "Asimismo, conforme a las cláusulas 7.2 y 7.3, la institución debe evaluar la competencia del personal, "
            "asegurar la toma de conciencia sobre las políticas de privacidad y documentar la eficacia de los programas de capacitación."
        )
    },
    {
        "doc_id": "LEY_29733_PERU",
        "fuente": "Ley N° 29733 - Ley de Protección de Datos Personales (Perú)",
        "contenido": (
            "La Ley N° 29733 de la República del Perú tiene por objeto garantizar el derecho fundamental a la protección "
            "de los datos personales, previsto en el artículo 2, numeral 6, de la Constitución Política del Perú. "
            "El tratamiento de datos personales en universidades públicas como la UNSA debe realizarse con consentimiento "
            "del titular, salvo las excepciones de ley. Se reconocen los derechos ARCO: Acceso, Rectificación, Cancelación "
            "y Oposición. El titular del banco de datos personales y el encargado del tratamiento están obligados a guardar "
            "secreto profesional respecto de los mismos y adoptar medidas de seguridad técnicas y organizativas para evitar su alteración o pérdida."
        )
    },
    {
        "doc_id": "DS_003_2013_JUS",
        "fuente": "Decreto Supremo N° 003-2013-JUS - Reglamento de la Ley 29733",
        "contenido": (
            "El D.S. 003-2013-JUS detalla las medidas de seguridad organizativas y técnicas exigibles. Todo titular de banco "
            "de datos personales debe implementar un programa continuo de capacitación y formación periódica para todo "
            "el personal que intervenga en el tratamiento de datos personales (Artículo 38). La institución debe evaluar "
            "periódicamente los conocimientos del personal sobre el deber de confidencialidad, derechos ARCO y respuesta rápida ante brechas."
        )
    },
    {
        "doc_id": "ISO_29100_PRINCIPIOS",
        "fuente": "ISO/IEC 29100 - Marco de Privacidad de la Información",
        "contenido": (
            "El marco de privacidad ISO 29100 define los principios fundamentales: consentimiento y elección, legitimidad del propósito, "
            "limitación de la recopilación, minimización de datos, limitación de uso y retención, exactitud y calidad, "
            "transparencia y notificación, e individual participation. Estos principios guían las políticas de privacidad en la UNSA."
        )
    }
]

DOCUMENTOS_SEMILLA_POLITICAS = [
    {
        "doc_id": "ESTATUTO_UNSA",
        "fuente": "Estatuto Universitario de la UNSA (Arequipa)",
        "contenido": (
            "El Estatuto de la Universidad Nacional de San Agustín establece que la comunidad agustina (docentes, "
            "estudiantes, egresados y personal no docente) está comprometida con la ética pública, la legalidad y "
            "la custodia debida de la información institucional y académica. El tratamiento de expedientes de matrícula, "
            "legajos docentes y bases de datos institucionales debe salvaguardar la reserva y la privacidad de la persona humana."
        )
    },
    {
        "doc_id": "CODIGO_ETICA_UNSA",
        "fuente": "Código de Ética y Conducta de la UNSA",
        "contenido": (
            "Todo servidor universitario, docente o administrativo de la UNSA tiene el deber ineludible de guardar reserva "
            "y confidencialidad sobre los datos personales y sensibles a los que tenga acceso en razón de sus funciones. "
            "Queda estrictamente prohibido compartir listas de estudiantes con calificaciones o datos de contacto a terceros "
            "sin autorización institucional. La participación anual en los talleres y programas de capacitación y sensibilización en privacidad es obligatoria para todo el personal."
        )
    },
    {
        "doc_id": "GUIA_BRECHAS_UNSA",
        "fuente": "Directiva UNSA de Gestión de Brechas de Seguridad y Privacidad",
        "contenido": (
            "Ante cualquier sospecha o evidencia de fuga, extravío, acceso no autorizado o divulgación indebida de datos "
            "personales, todo miembro de la UNSA debe notificar inmediatamente al Oficial de Seguridad de la Información "
            "y Privacidad (PIMS). El plazo máximo para reporte preliminar es de 24 horas para cumplir con la notificación a la Autoridad Nacional (MINJUSDH)."
        )
    }
]

def procesar_archivos(directorio: Path, coleccion, nombre_coleccion: str):
    archivos = list(directorio.glob("*.pdf")) + list(directorio.glob("*.md"))
    if not archivos:
        print(f"[RAG] No se encontraron archivos adicionales en {directorio}.")
        return

    for archivo in archivos:
        print(f"[RAG] Procesando archivo: {archivo.name}")
        try:
            full_text = ""
            if archivo.suffix.lower() == ".pdf":
                if PdfReader is None:
                    print(f"[RAG] pypdf no esta instalado. Omitiendo lectura de {archivo.name}.")
                    continue
                reader = PdfReader(str(archivo))
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n"
            elif archivo.suffix.lower() == ".md":
                with open(archivo, "r", encoding="utf-8") as f:
                    full_text = f.read()

            chunks = chunk_text(full_text)
            insert_fn = getattr(coleccion, "upsert", coleccion.add)
            for idx, ch in enumerate(chunks):
                doc_id = f"{archivo.suffix.lstrip('.')}_{archivo.stem}_{idx}"
                insert_fn(
                    documents=[ch],
                    metadatas=[{
                        "fuente": archivo.name,
                        "doc_id": archivo.stem,
                        "chunk_index": idx,
                        "coleccion": nombre_coleccion
                    }],
                    ids=[doc_id]
                )
            print(f"   -> {len(chunks)} chunks indexados en {nombre_coleccion}.")
        except Exception as e:
            print(f"[RAG] Error leyendo {archivo.name}: {e}")

def ejecutar_ingesta():
    print("[RAG] Iniciando proceso de ingesta RAG...")

    # 1. Ingestar semillas en normas_iso
    print("[RAG] Indexando base normativa (ISO 27701, ISO 29100, Ley 29733, DS 003-2013-JUS)...")
    for doc in DOCUMENTOS_SEMILLA_NORMAS:
        chunks = chunk_text(doc["contenido"])
        for idx, ch in enumerate(chunks):
            cid = f"norma_{doc['doc_id']}_{idx}"
            col_normas_iso.upsert(
                documents=[ch],
                metadatas=[{
                    "fuente": doc["fuente"],
                    "doc_id": doc["doc_id"],
                    "chunk_index": idx,
                    "coleccion": "normas_iso"
                }],
                ids=[cid]
            )

    # 2. Ingestar semillas en politicas_negocio
    print("[RAG] Indexando politicas y reglamentos institucionales de la UNSA...")
    for doc in DOCUMENTOS_SEMILLA_POLITICAS:
        chunks = chunk_text(doc["contenido"])
        for idx, ch in enumerate(chunks):
            cid = f"politica_{doc['doc_id']}_{idx}"
            col_politicas_negocio.upsert(
                documents=[ch],
                metadatas=[{
                    "fuente": doc["fuente"],
                    "doc_id": doc["doc_id"],
                    "chunk_index": idx,
                    "coleccion": "politicas_negocio"
                }],
                ids=[cid]
            )

    # 3. Procesar PDFs y MDs existentes en knowledge_base/
    dir_iso = KNOWLEDGE_BASE_PATH / "normativas" / "iso"
    dir_peru = KNOWLEDGE_BASE_PATH / "normativas" / "peru"
    dir_unsa = KNOWLEDGE_BASE_PATH / "normativas" / "reglamentos_unsa"
    dir_politicas = KNOWLEDGE_BASE_PATH / "politicas" / "seguridad_informacion"

    procesar_archivos(dir_iso, col_normas_iso, "normas_iso")
    procesar_archivos(dir_peru, col_normas_iso, "normas_iso")
    procesar_archivos(dir_unsa, col_politicas_negocio, "politicas_negocio")
    procesar_archivos(dir_politicas, col_politicas_negocio, "politicas_negocio")

    print(f"[RAG] Ingesta finalizada exitosamente:")
    print(f"   - Coleccion 'normas_iso': {col_normas_iso.count()} chunks.")
    print(f"   - Coleccion 'politicas_negocio': {col_politicas_negocio.count()} chunks.")

if __name__ == "__main__":
    ejecutar_ingesta()
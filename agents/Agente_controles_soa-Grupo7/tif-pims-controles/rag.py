import glob
import os
import faiss
import numpy as np
import requests

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
EMBEDDING_MODEL = os.environ.get("OLLAMA_EMBED_MODEL", "all-minilm")


def obtener_embeddings(textos):
    """
    Genera embeddings vectoriales usando el servidor local de Ollama.
    Utiliza el modelo liviano 'all-minilm' (384 dimensiones) 100% local.
    """
    if not textos:
        return np.empty((0, 384), dtype="float32")

    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/embed",
            json={"model": EMBEDDING_MODEL, "input": textos},
            timeout=45,
        )
        if resp.status_code == 200:
            vecs = np.asarray(resp.json().get("embeddings", []), dtype="float32")
            if vecs.ndim == 2 and vecs.shape[0] == len(textos):
                # Normalizar para similitud coseno exacta (producto interno = coseno)
                normas = np.linalg.norm(vecs, axis=1, keepdims=True)
                normas[normas == 0] = 1.0
                return vecs / normas
    except Exception as e:
        print(f"[RAG] Error conectando con Ollama embeddings: {e}")

    # Fallback seguro con matriz vacía o ceros si no responde
    return np.zeros((len(textos), 384), dtype="float32")


class Indice:
    """Índice vectorial: textos + metadatos, búsqueda semántica por similitud con Ollama + FAISS."""

    def __init__(self, textos, metas):
        self.textos, self.metas = textos, metas
        self.index = None
        if not textos:
            return
        vecs = obtener_embeddings(textos)
        dim = vecs.shape[1] if vecs.ndim == 2 else 384
        self.index = faiss.IndexFlatIP(dim)  # producto interno con vectores normalizados = similitud coseno
        self.index.add(np.asarray(vecs, dtype="float32"))

    def buscar(self, consulta, k=3):
        if self.index is None or not self.textos:
            return []
        q = obtener_embeddings([consulta])
        scores, ids = self.index.search(q, min(k, len(self.textos)))
        return [
            {"texto": self.textos[i], "meta": self.metas[i], "score": float(s)}
            for s, i in zip(scores[0], ids[0])
            if i != -1
        ]


def desde_carpeta(carpeta):
    """Lee los .md de una carpeta, une encabezados con sus párrafos y extrae metadatos limpios."""
    textos, metas = [], []
    for ruta in sorted(glob.glob(os.path.join(carpeta, "*.md"))):
        with open(ruta, encoding="utf-8") as f:
            contenido = f.read()

        partes = [p.strip() for p in contenido.split("\n\n") if p.strip()]
        i = 0
        while i < len(partes):
            p = partes[i]
            # Si el bloque es muy corto (< 100 caracteres) y parece un encabezado
            if len(p) < 100 and (p.startswith("#") or ":" in p or p.startswith("ISO/IEC") or p.startswith("Normativa")):
                if i + 1 < len(partes):
                    titulo = p.replace("#", "").strip()
                    cuerpo = partes[i + 1]
                    texto_completo = f"{titulo}\n\n{cuerpo}"
                    meta_label = titulo.split("\n")[0].strip().rstrip(":")
                    textos.append(texto_completo)
                    metas.append(meta_label)
                    i += 2
                    continue

            # Bloque con contenido completo
            if len(p) >= 80:
                lineas = [l for l in p.split("\n") if l.strip()]
                primera = lineas[0].replace("#", "").strip()
                meta_label = primera.split(":")[0].strip() if ":" in primera else primera[:90]
                textos.append(p)
                metas.append(meta_label)
            i += 1

    return Indice(textos, metas)

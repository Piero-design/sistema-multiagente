"""Recuperación léxica sin dependencias: TF-IDF (línea base) y BM25 con raíces, sinónimos y títulos."""

from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter
from typing import Any

TFIDF_MODEL_NAME = "tfidf-word-ngram-1-2-v1"
LEXICAL_MODEL_NAME = "bm25-es-stem-syn-title-v1"
TOKEN_RE = re.compile(r"[a-z0-9]{2,}")
STOPWORDS = frozenset({
    "al", "ante", "como", "con", "de", "del", "el", "en", "es", "esta",
    "este", "la", "las", "lo", "los", "para", "por", "que", "se", "sin",
    "su", "sus", "un", "una", "y",
})
BM25_K1 = 1.5
BM25_B = 0.75
# (raíces, sinónimos, título) de cada variante: mejoras acumulativas para medir el aporte de cada una.
LEXICAL_VARIANTS = {
    "bm25": (False, False, False),
    "bm25-stem": (True, False, False),
    "bm25-stem-syn": (True, True, False),
    "bm25-stem-syn-title": (True, True, True),
}
LEXICAL_DEFAULT = "bm25-stem-syn-title"
LEXICAL_TOKEN_RE = re.compile(r"[a-z]\.\d+(?:\.\d+)+|[a-z0-9]{2,}")
LEXICAL_STOPWORDS = STOPWORDS | {
    "mi", "mis", "tu", "tus", "me", "te", "si", "puedo", "puede", "pueden", "debe", "deben",
    "hay", "tiene", "tienen", "tener", "ser", "son", "cual", "cuales", "cuanto", "cuanta",
    "como", "donde", "cuando", "quien", "quienes", "porque", "tambien", "mas", "muy", "otra",
    "otro", "ya", "han", "ha", "sobre", "entre", "desde", "hasta", "estan", "esto", "eso",
    "soy", "quiero", "tengo", "hacer", "algun", "cada", "debo", "hace",
}
CLITICS = ("nos", "les", "me", "te", "lo", "la", "le", "se")
DERIVATIONAL_SUFFIXES = tuple(sorted((
    "amiento", "imiento", "icion", "acion", "ucion", "cion", "sion", "idad", "mente", "adora",
    "ador", "able", "ible", "ando", "iendo", "aron", "ieron", "aban", "aria", "eria", "ivo",
    "iva", "ado", "ada", "ido", "ida", "ar", "er", "ir", "an", "en", "a", "o", "e",
), key=len, reverse=True))
# Formas que significan lo mismo en este dominio. Cada grupo añade un término común ("@concepto")
# a documentos y consultas; se evitan palabras ambiguas.
CONCEPT_GROUPS = {
    "supresion": "suprimir supresion eliminar eliminacion borrar borrado cancelar cancelacion destruir olvido",
    "rectificacion": "rectificar rectificacion corregir correccion corrige arreglar actualizar actualizacion "
                     "incorrecto inexacto erroneo equivocado",
    "oposicion": "oponer oponerse oposicion objetar objecion negar negarse rehusar",
    "portabilidad": "portabilidad portable portar llevar llevarse trasladar transferir transmitir migrar",
    "plazo": "plazo plazos tiempo vencer vencimiento demora tardar",
    "respuesta": "responder respuesta contestar atender atencion",
    "prorroga": "prorroga prorrogar alargar ampliar ampliacion extender extension",
    "reclamo": "reclamar reclamo reclamacion queja denunciar apelar impugnar tutela habeas",
    "gratuidad": "gratuito gratuidad gratis pagar pago costo cobrar cobro precio tarifa",
    "identidad": "identidad identificar verificar verificacion acreditar acreditacion demostrar validar",
    "aprobacion": "aprobar aprobacion aprobador autorizar autorizacion",
    "confidencial": "confidencial secreto reservado",
    "recepcion": "recibir recepcion presentar presentacion mandar",
    "norma": "iso norma estandar internacional 27701",
    "jurisdiccion": "jurisdiccion pais territorio",
    "flexible": "flexible permisivo permisiva laxo relajado",
    "tono": "tono estilo formal",
    "documentos": "documento documentos papeles requisito requisitos",
}


def normalize(value: str) -> str:
    """Minúsculas y sin tildes."""
    decomposed = unicodedata.normalize("NFKD", value.lower())
    return "".join(char for char in decomposed if not unicodedata.combining(char))


# Cubre el fragmento más largo del corpus (1456 caracteres); un recorte parte las tablas a mitad de fila.
EXCERPT_CHARS = 1500


def format_hit(rank: int, score: float, chunk: dict[str, Any]) -> dict[str, Any]:
    return {
        "rank": rank,
        "score": round(score, 6),
        "chunk_id": chunk["chunk_id"],
        "source": chunk["source"],
        "section": chunk["section"],
        "sha256": chunk["sha256"],
        "excerpt": re.sub(r"\s+", " ", chunk["text"]).strip()[:EXCERPT_CHARS],
    }


def _check_top_k(top_k: int) -> None:
    if top_k <= 0:
        raise ValueError("top_k debe ser positivo")


# --- TF-IDF (línea base) ---

def tokenize(value: str) -> list[str]:
    words = [token for token in TOKEN_RE.findall(normalize(value)) if token not in STOPWORDS]
    return words + [f"{left}::{right}" for left, right in zip(words, words[1:])]


def sparse_embedding(terms: list[str], vocabulary: dict[str, int], idf: list[float]) -> list[list[float]]:
    counts = Counter(term for term in terms if term in vocabulary)
    if not counts:
        return []
    weights = {vocabulary[term]: (1.0 + math.log(frequency)) * idf[vocabulary[term]]
               for term, frequency in counts.items()}
    norm = math.sqrt(sum(weight * weight for weight in weights.values()))
    return [[index, round(weight / norm, 10)] for index, weight in sorted(weights.items())]


_TFIDF_CACHE: dict[str, dict[str, Any]] = {}


def tfidf_model(index: dict[str, Any]) -> dict[str, Any]:
    """Vocabulario, IDF y vectores dispersos del corpus (en memoria, por firma del corpus)."""
    key = index["corpus_sha256"]
    if key not in _TFIDF_CACHE:
        tokenized = [tokenize(chunk["text"]) for chunk in index["chunks"]]
        frequency: Counter[str] = Counter()
        for terms in tokenized:
            frequency.update(set(terms))
        terms_sorted = sorted(frequency)
        vocabulary = {term: position for position, term in enumerate(terms_sorted)}
        count = len(tokenized)
        idf = [round(math.log((1 + count) / (1 + frequency[term])) + 1.0, 10) for term in terms_sorted]
        _TFIDF_CACHE[key] = {"vocabulary": vocabulary, "idf": idf,
                             "vectors": [sparse_embedding(terms, vocabulary, idf) for terms in tokenized]}
    return _TFIDF_CACHE[key]


def cosine_sparse(left: list[list[float]], right: list[list[float]]) -> float:
    left_map = {int(index): float(value) for index, value in left}
    right_map = {int(index): float(value) for index, value in right}
    if len(left_map) > len(right_map):
        left_map, right_map = right_map, left_map
    return sum(value * right_map.get(index, 0.0) for index, value in left_map.items())


def tfidf_search(query: str, index: dict[str, Any], top_k: int = 3) -> list[dict[str, Any]]:
    _check_top_k(top_k)
    model = tfidf_model(index)
    query_vector = sparse_embedding(tokenize(query), model["vocabulary"], model["idf"])
    if not query_vector:
        return []
    scored = [(cosine_sparse(query_vector, vector), chunk) for vector, chunk in zip(model["vectors"], index["chunks"])]
    scored = sorted((item for item in scored if item[0] > 0), key=lambda item: (-item[0], item[1]["chunk_id"]))
    return [format_hit(rank, score, chunk) for rank, (score, chunk) in enumerate(scored[:top_k], 1)]


# --- BM25 con raíces de palabras, sinónimos del dominio y títulos ---

def strip_clitic(word: str) -> str:
    for clitic in CLITICS:
        base = word[: -len(clitic)]
        if word.endswith(clitic) and len(base) >= 4 and base.endswith(("ar", "er", "ir")):
            return base
    return word


def stem_es(word: str) -> str:
    """Raíz ligera y determinista para español (sin tildes); no es un lematizador completo."""
    if word[:1].isdigit() or "." in word or len(word) <= 3:
        return word
    word = strip_clitic(word)
    if word.endswith("es") and len(word) - 2 >= 4:
        word = word[:-2]
    elif word.endswith("s") and len(word) - 1 >= 3:
        word = word[:-1]
    for suffix in DERIVATIONAL_SUFFIXES:
        if word.endswith(suffix) and len(word) - len(suffix) >= 4:
            return word[: -len(suffix)]
    return word


def _concept_lookup(use_stem: bool) -> dict[str, list[str]]:
    lookup: dict[str, list[str]] = {}
    for concept, forms in CONCEPT_GROUPS.items():
        for form in forms.split():
            lookup.setdefault(stem_es(form) if use_stem else form, []).append("@" + concept)
    return lookup


_LOOKUPS = {True: _concept_lookup(True), False: _concept_lookup(False)}


def lexical_tokens(value: str, use_stem: bool = True, use_synonyms: bool = True) -> list[str]:
    words = [token for token in LEXICAL_TOKEN_RE.findall(normalize(value)) if token not in LEXICAL_STOPWORDS]
    terms = [stem_es(word) if use_stem else word for word in words]
    if use_synonyms:
        lookup = _LOOKUPS[use_stem]
        terms = terms + [concept for term in terms for concept in lookup.get(term, [])]
    return terms


_LEXICAL_CACHE: dict[tuple, dict[str, Any]] = {}


def lexical_stats(index: dict[str, Any], use_stem: bool, use_synonyms: bool, use_title: bool = False) -> dict[str, Any]:
    key = (index["corpus_sha256"], use_stem, use_synonyms, use_title)
    if key not in _LEXICAL_CACHE:
        # El título de la sección nombra el tema del fragmento pero no está en su texto.
        counts = [Counter(lexical_tokens(f"{c['section']}\n{c['text']}" if use_title else c["text"],
                                         use_stem, use_synonyms)) for c in index["chunks"]]
        lengths = [sum(c.values()) for c in counts]
        frequency: Counter[str] = Counter()
        for chunk_counts in counts:
            frequency.update(chunk_counts.keys())
        total = len(counts)
        _LEXICAL_CACHE[key] = {
            "counts": counts,
            "lengths": lengths,
            "average": (sum(lengths) / total) if total else 0.0,
            "idf": {term: math.log(1 + (total - n + 0.5) / (n + 0.5)) for term, n in frequency.items()},
        }
    return _LEXICAL_CACHE[key]


def lexical_search(query: str, index: dict[str, Any], top_k: int = 3,
                   variant: str = LEXICAL_DEFAULT) -> list[dict[str, Any]]:
    _check_top_k(top_k)
    use_stem, use_synonyms, use_title = LEXICAL_VARIANTS[variant]
    query_terms = set(lexical_tokens(query, use_stem, use_synonyms))
    stats = lexical_stats(index, use_stem, use_synonyms, use_title)
    scored = []
    for chunk, counts, length in zip(index["chunks"], stats["counts"], stats["lengths"]):
        score = 0.0
        for term in query_terms:
            frequency = counts.get(term, 0)
            if frequency:
                norm = frequency + BM25_K1 * (1 - BM25_B + BM25_B * length / (stats["average"] or 1.0))
                score += stats["idf"][term] * frequency * (BM25_K1 + 1) / norm
        if score > 0:
            scored.append((score, chunk))
    scored.sort(key=lambda item: (-item[0], item[1]["chunk_id"]))
    return [format_hit(rank, score, chunk) for rank, (score, chunk) in enumerate(scored[:top_k], 1)]

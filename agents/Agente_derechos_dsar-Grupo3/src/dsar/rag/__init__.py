"""Recuperación de conocimiento: BM25, embeddings densos opcionales y fusión RRF.

Funciona sin numpy ni sentence-transformers: entonces recupera con BM25 y deja el motivo en
`fallback_reason`. Punto de entrada: `dsar.rag.retrieve.retrieve`.
"""

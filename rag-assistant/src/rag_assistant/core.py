"""Briques du RAG : découpage, embeddings, index vectoriel, LLM, outil fund-api et agent."""

from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass, field
from typing import Protocol

import httpx
from langchain_text_splitters import RecursiveCharacterTextSplitter


@dataclass(frozen=True)
class Chunk:
    doc_id: str
    title: str
    text: str


def split(doc_id: str, title: str, text: str, size: int = 600, overlap: int = 80) -> list[Chunk]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=size, chunk_overlap=overlap,
                                              separators=["\n\n", "\n", ". ", " "])
    return [Chunk(doc_id, title, part) for part in splitter.split_text(text)]


class Embedder(Protocol):
    def embed(self, text: str) -> list[float]: ...


class HashEmbedder:
    """Embeddings déterministes (sac de mots haché) : tests et démonstration sans modèle."""

    def __init__(self, dimensions: int = 256):
        self.dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for word in re.findall(r"\w+", text.lower()):
            if len(word) > 2:
                vector[int(hashlib.md5(word.encode()).hexdigest(), 16) % self.dimensions] += 1.0
        norm = math.sqrt(sum(x * x for x in vector)) or 1.0
        return [x / norm for x in vector]


class OllamaEmbedder:
    def __init__(self, client: httpx.Client, model: str = "nomic-embed-text"):
        self.client, self.model = client, model

    def embed(self, text: str) -> list[float]:
        response = self.client.post("/api/embeddings", json={"model": self.model, "prompt": text})
        response.raise_for_status()
        return response.json()["embedding"]


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    na, nb = math.sqrt(sum(x * x for x in a)), math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


@dataclass
class VectorIndex:
    embedder: Embedder
    entries: list[tuple[Chunk, list[float]]] = field(default_factory=list)

    def add(self, chunks: list[Chunk]) -> int:
        self.entries += [(c, self.embedder.embed(c.text)) for c in chunks]
        return len(chunks)

    def search(self, query: str, k: int = 3, min_score: float = 0.05) -> list[tuple[Chunk, float]]:
        q = self.embedder.embed(query)
        scored = sorted(((c, cosine(q, v)) for c, v in self.entries), key=lambda x: x[1], reverse=True)
        return [(c, round(s, 4)) for c, s in scored[:k] if s >= min_score]


class Llm(Protocol):
    def generate(self, prompt: str) -> str: ...


class OllamaLlm:
    def __init__(self, client: httpx.Client, model: str = "llama3.1:8b"):
        self.client, self.model = client, model

    def generate(self, prompt: str) -> str:
        response = self.client.post("/api/generate", json={"model": self.model, "prompt": prompt, "stream": False,
                                                            "options": {"temperature": 0.1}})
        response.raise_for_status()
        return response.json()["response"].strip()


class FundApiTool:
    """Outil de l'agent : performance d'un fonds via fund-api."""

    def __init__(self, client: httpx.Client):
        self.client = client

    def performance(self, fund_id: str, date_from: str, date_to: str) -> dict:
        response = self.client.get(f"/api/funds/{fund_id}/performance", params={"from": date_from, "to": date_to})
        response.raise_for_status()
        return response.json()


FUND_RE = re.compile(r"\bFL-\d{4}\b")
DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
PERF_WORDS = ("performance", "rendement", "évolution", "valeur liquidative", " vl ")


@dataclass
class Answer:
    answer: str
    sources: list[dict]
    tool: str | None = None


class Agent:
    """Choisit l'outil fund-api pour une question chiffrée (fonds + deux dates), sinon répond par RAG."""

    def __init__(self, index: VectorIndex, llm: Llm, fund_api: FundApiTool | None = None):
        self.index, self.llm, self.fund_api = index, llm, fund_api

    def ask(self, question: str) -> Answer:
        fund, dates = FUND_RE.search(question), DATE_RE.findall(question)
        wants_figures = any(w in f" {question.lower()} " for w in PERF_WORDS)
        if self.fund_api and fund and len(dates) >= 2 and wants_figures:
            perf = self.fund_api.performance(fund.group(), dates[0], dates[1])
            pct = round(perf["periodReturn"] * 100, 2)
            return Answer(f"La performance de {fund.group()} du {dates[0]} au {dates[1]} est de {pct} %.",
                          [{"type": "fund-api", "endpoint": "performance"}], tool="fund-api")

        hits = self.index.search(question)
        if not hits:
            return Answer("Je ne trouve pas cette information dans les documents des fonds.", [])
        context = "\n\n".join(f"[{i + 1}] ({c.title}) {c.text}" for i, (c, _) in enumerate(hits))
        prompt = ("Tu es l'assistant documentaire d'une société de gestion. Réponds en français, "
                  "uniquement à partir des extraits numérotés ci-dessous, et cite-les entre crochets. "
                  "Si la réponse n'y est pas, dis-le.\n\n"
                  f"Extraits :\n{context}\n\nQuestion : {question}\nRéponse :")
        return Answer(self.llm.generate(prompt),
                      [{"doc_id": c.doc_id, "title": c.title, "score": s} for c, s in hits])

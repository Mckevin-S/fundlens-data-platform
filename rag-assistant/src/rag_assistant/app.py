"""API : POST /documents (indexation) et POST /ask (question)."""

from __future__ import annotations

import os

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from rag_assistant.core import Agent, FundApiTool, OllamaEmbedder, OllamaLlm, VectorIndex, split


class DocumentIn(BaseModel):
    doc_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    text: str = Field(min_length=20)


class Question(BaseModel):
    question: str = Field(min_length=3, max_length=1000)


def create_app(agent: Agent | None = None) -> FastAPI:
    if agent is None:
        ollama = httpx.Client(base_url=os.environ.get("OLLAMA_URL", "http://localhost:11434"), timeout=120)
        fund_api = httpx.Client(base_url=os.environ.get("FUND_API_URL", "http://localhost:8080"), timeout=30)
        agent = Agent(VectorIndex(OllamaEmbedder(ollama)), OllamaLlm(ollama), FundApiTool(fund_api))
    app = FastAPI(title="FundLens – assistant RAG")

    @app.post("/documents", status_code=201)
    def add_document(doc: DocumentIn) -> dict:
        return {"chunks": agent.index.add(split(doc.doc_id, doc.title, doc.text))}

    @app.post("/ask")
    def ask(q: Question) -> dict:
        try:
            result = agent.ask(q.question)
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=502, detail=f"Service amont indisponible : {exc}") from exc
        return {"answer": result.answer, "sources": result.sources, "tool": result.tool}

    @app.get("/health")
    def health() -> dict:
        return {"status": "UP", "chunks": len(agent.index.entries)}

    return app

from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient
from rag_assistant.app import create_app
from rag_assistant.core import Agent, FundApiTool, HashEmbedder, OllamaEmbedder, OllamaLlm, VectorIndex, cosine, split

PROSPECTUS = (Path(__file__).resolve().parents[1] / "docs-sample/prospectus-FL-0001.md").read_text()


class EchoLlm:
    def __init__(self):
        self.prompts = []

    def generate(self, prompt):
        self.prompts.append(prompt)
        return "Les frais de gestion sont de 1,20 % [1]."


def mock_client(handler):
    return httpx.Client(base_url="http://svc", transport=httpx.MockTransport(handler))


@pytest.fixture
def agent():
    index = VectorIndex(HashEmbedder())
    index.add(split("FL-0001-prospectus", "Prospectus FL-0001", PROSPECTUS, size=300, overlap=30))

    def fund_api(request):
        assert request.url.path == "/api/funds/FL-0001/performance"
        assert request.url.params["from"] == "2026-11-20"
        return httpx.Response(200, json={"periodReturn": 0.004015})

    return Agent(index, EchoLlm(), FundApiTool(mock_client(fund_api)))


def test_decoupage_avec_chevauchement():
    chunks = split("d", "t", PROSPECTUS, size=300, overlap=30)
    assert len(chunks) >= 3 and all(len(c.text) <= 300 for c in chunks)


def test_la_recherche_trouve_le_passage_sur_les_frais(agent):
    best, score = agent.index.search("Quels sont les frais de gestion annuels ?")[0]
    assert "1,20 %" in best.text and score > 0.1


def test_reponse_rag_avec_sources_et_consigne_de_citation(agent):
    answer = agent.ask("Quels sont les frais de gestion du fonds ?")
    assert answer.tool is None and answer.sources[0]["doc_id"] == "FL-0001-prospectus"
    prompt = agent.llm.prompts[0]
    assert "uniquement à partir des extraits" in prompt and "[1]" in prompt


def test_question_chiffree_routee_vers_fund_api(agent):
    answer = agent.ask("Quelle est la performance de FL-0001 entre 2026-11-20 et 2026-11-23 ?")
    assert answer.tool == "fund-api" and "0.4 %" in answer.answer
    assert agent.llm.prompts == []


def test_aucune_source_pertinente(agent):
    assert "ne trouve pas" in agent.ask("zzz qqq www").answer


def test_clients_ollama():
    def handler(request):
        body = request.read().decode()
        if request.url.path == "/api/embeddings":
            return httpx.Response(200, json={"embedding": [0.1, 0.2]})
        assert '"stream":false' in body.replace(" ", "")
        return httpx.Response(200, json={"response": "  bonjour  "})

    client = mock_client(handler)
    assert OllamaEmbedder(client).embed("x") == [0.1, 0.2]
    assert OllamaLlm(client).generate("x") == "bonjour"
    assert cosine([0, 0], [1, 1]) == 0.0


def test_api_indexation_question_et_erreur_amont(agent):
    client = TestClient(create_app(agent))
    doc = {"doc_id": "dic", "title": "DIC", "text": "Le SRI du fonds est de 4 sur 7."}
    assert client.post("/documents", json=doc).json() == {"chunks": 1}
    assert client.get("/health").json()["chunks"] > 1
    assert client.post("/ask", json={"question": "Quels frais de gestion ?"}).json()["sources"]
    assert client.post("/ask", json={"question": "x"}).status_code == 422

    broken = Agent(agent.index, agent.llm, FundApiTool(mock_client(lambda r: httpx.Response(500))))
    response = TestClient(create_app(broken)).post(
        "/ask", json={"question": "performance de FL-0001 du 2026-11-20 au 2026-11-23"})
    assert response.status_code == 502


def test_application_par_defaut_sans_service(monkeypatch):
    monkeypatch.setenv("OLLAMA_URL", "http://ollama:11434")
    assert TestClient(create_app()).get("/health").json() == {"status": "UP", "chunks": 0}

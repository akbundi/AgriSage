from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, HTTPException
from .rag_store import MiniVectorStore, Doc
from .agent import AgriAgent
from .models import AskRequest, AskResponse, IngestDoc
from typing import Dict, Any
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse

# Seed docs for demo
SEED_DOCS = [
    Doc(id="icar_wheat_irrigation", text=("Wheat irrigation schedule depends on critical stages: crown root initiation, tillering, jointing, flowering, and grain filling. Avoid irrigation immediately before forecasted rain."), meta={"title":"ICAR Wheat Irrigation Guidance","source":"local"}),
    Doc(id="pest_aphid_control", text=("Aphid management: monitor undersides of leaves during cool periods; use yellow sticky traps; encourage predators; apply insecticides only if thresholds crossed."), meta={"title":"Aphid IPM Guide","source":"local"}),
    Doc(id="policy_kcc_summary", text=("Kisan Credit Card (KCC) provides short-term credit at concessional interest to farmers."), meta={"title":"KCC Overview","source":"local"}),
    Doc(id="post_harvest_onion", text=("For onions ensure cured bulbs and ventilated storage. Market timing reduces losses."), meta={"title":"Onion Post-Harvest Tips","source":"local"}),
]

app = FastAPI(title="AgriSage Agent", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STORE = MiniVectorStore()
for d in SEED_DOCS:
    STORE.upsert(d)
AGENT = AgriAgent(STORE)

@app.get("/health")
def health():
    return {"status": "ok", "docs": len(STORE.docs)}

@app.post("/ingest")
def ingest(doc: IngestDoc):
    try:
        STORE.upsert(Doc(id=doc.id, text=doc.text, meta=doc.meta))
        return {"ok": True, "doc_id": doc.id, "count": len(STORE.docs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    ctx: Dict[str, Any] = req.context.dict() if req.context else {}
    try:
        resp = AGENT.answer(req.query, ctx)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return AskResponse(answer=resp.answer, citations=resp.citations, explain={"intent": resp.intent, "language": resp.language, "steps": resp.steps, "confidence": resp.confidence, "raw": resp.raw}, warnings=resp.warnings, meta={"retrieved_docs": resp.metrics.get("retrieved_docs", 0)})
app.mount("/static", StaticFiles(directory="../frontend/build/static"), name="static")

@app.get("/")
def serve_root():
    return FileResponse("../frontend/build/index.html")

@app.get("/{full_path:path}")
def serve_react(full_path: str):
    """
    Catch-all route: serve index.html for React Router deep links
    (like /about, /dashboard, etc.)
    """
    return FileResponse("../frontend/build/index.html")

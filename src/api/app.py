from fastapi import FastAPI, HTTPException
from src.models.schemas import QueryRequest, QueryResponse
from src.pipeline import run_rag
from src.utils.logging import logger  # noqa: F401  (configures logging)

app = FastAPI(title="Policy-Aware RAG Assistant", version="1.0.0")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest) -> QueryResponse:
    try:
        return run_rag(req)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Unhandled error")
        raise HTTPException(status_code=500, detail="internal_error")
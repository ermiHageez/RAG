from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.agent.graph import build_agent

app = FastAPI(title="eTech Agent API", version="0.1.0")


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    success: bool
    result: dict | None = None
    error: str | None = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/agent/run", response_model=QueryResponse)
def run_agent(req: QueryRequest):
    try:
        agent = build_agent()
        result = agent.invoke({"query": req.query})
        return QueryResponse(success=True, result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

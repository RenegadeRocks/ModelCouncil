from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from council.config import load_config
from server.stream import council_stream

app = FastAPI(title="Model Council API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


class CouncilRequest(BaseModel):
    prompt: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/council")
async def council(req: CouncilRequest):
    config = load_config()

    async def event_generator():
        async for event_json in council_stream(req.prompt, config):
            yield f"data: {event_json}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

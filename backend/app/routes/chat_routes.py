from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List

from app.agents.supervisor.graph import create_graph
from langgraph.checkpoint.memory import MemorySaver
import json

graph = create_graph()

chat_router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    messages: List[tuple[str, str]]
    thread_id: str


@chat_router.post("/chat/stream", response_class=StreamingResponse)
async def chat(request: ChatRequest):

    messages = request.messages
    config = {"configurable": {"thread_id": request.thread_id}}

    async def event_stream():
        try:
            async for chunk in graph.astream(
                input={"messages": messages},
                config=config,
                stream_mode=["custom"],
            ):
                yield f"data: {json.dumps({'text': chunk[1]})}\n\n"
        except Exception as e:
            print(f"========== {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")

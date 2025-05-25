from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from app.agents.supervisor.graph import create_graph
from app.agents.place_researcher.chains import PlaceInfo
from langgraph.checkpoint.memory import MemorySaver
import json
from langchain_core.messages import HumanMessage
import os

# PostgreSQL 연결 정보 (환경변수에서 가져오기)
# DB_URI = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/planner")

# 영구 저장소 기반 체크포인터와 스토어 초기화
# try:
#     checkpointer = PostgresSaver.from_conn_string(DB_URI)
#     # store = PostgresStore.from_conn_string(DB_URI)

# 테이블 초기화 (한 번만 실행)
# checkpointer.setup()
# store.setup()

#     graph = create_graph()
#     graph = graph.compile(checkpointer=checkpointer, store=store)
# except Exception as e:
# print(f"PostgreSQL 연결 실패, 메모리 저장소 사용: {e}")
checkpointer = MemorySaver()
# store = InMemoryStore()
graph = create_graph(verbose=True)
graph = graph.compile(checkpointer=checkpointer)


chat_router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    query: str = Field(...)
    thread_id: str


class StateRequest(BaseModel):
    thread_id: str


class UpdateStateRequest(BaseModel):
    thread_id: str
    messages: Dict[str, Any]


class UpdateSelectedPlacesRequest(BaseModel):
    """선택된 장소 업데이트 요청"""

    thread_id: str
    selected_places: List[Dict[str, Any]]


class ResumeRequest(BaseModel):
    thread_id: str


class HistoryRequest(BaseModel):
    thread_id: str
    limit: Optional[int] = 10


@chat_router.post(
    "/chat/stream",
    response_class=StreamingResponse,
    responses={
        200: {
            "description": "Server-sent events stream",
            "content": {
                "text/event-stream": {"schema": {"type": "string", "format": "binary"}}
            },
        }
    },
    description="여행 계획 생성 서비스 스트리밍 호출",
)
async def chat_stream(request: ChatRequest):

    query = request.query
    config = {"configurable": {"thread_id": request.thread_id}, "recursion_limit": 25}

    async def event_stream():
        try:
            async for chunk in graph.astream(
                input={"messages": query},
                config=config,
                stream_mode="custom",
                subgraphs=True,
            ):
                yield f"data: {json.dumps({'text': chunk[1]})}\n\n"
        except Exception as e:
            print(f"========== {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@chat_router.post("/chat/state")
async def get_state(request: StateRequest):
    """그래프 상태 조회"""
    try:
        config = {"configurable": {"thread_id": request.thread_id}}
        snapshot = graph.get_state(config, subgraphs=True)

        state_data = {
            "has_tasks": bool(snapshot.tasks),
            "tasks": [],
        }

        if snapshot.tasks:
            for task in snapshot.tasks:
                messages = task.state.values.get("messages", [])
                last_message = messages[-1] if messages else None

                # 서브 그래프 상태에서 추천 장소 정보 추출
                places = task.state.values.get("places", [])
                if places:
                    # PlaceInfo 객체들을 딕셔너리로 변환
                    recommended_places = []
                    for place in places:
                        recommended_places.append(place.model_dump())
                    state_data["recommended_places"] = recommended_places

                task_data = {
                    "config": task.state.config,
                    "last_message": (
                        {
                            "type": getattr(last_message, "type", None),
                            "name": getattr(last_message, "name", None),
                            "content": getattr(last_message, "content", None),
                        }
                        if last_message
                        else None
                    ),
                }
                state_data["tasks"].append(task_data)

        return state_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@chat_router.post("/chat/update_state")
async def update_state(request: UpdateStateRequest):
    """그래프 상태 업데이트"""
    try:
        config = {"configurable": {"thread_id": request.thread_id}}
        snapshot = graph.get_state(config, subgraphs=True)

        if not snapshot.tasks:
            raise HTTPException(status_code=400, detail="No active tasks to update")

        # 기존 마지막 검색 결과
        last_message = snapshot.tasks[0].state.values["messages"][-1]
        # 유저가 선택한 검색 결과
        new_content = request.messages.get("content", "")

        # 기존 검색 결과 업데이트
        user_places_message = last_message.model_copy()
        user_places_message.content = new_content

        task_config = snapshot.tasks[0].state.config
        graph.update_state(task_config, {"messages": user_places_message})

        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@chat_router.post("/chat/update_selected_places")
async def update_selected_places(request: UpdateSelectedPlacesRequest):
    """선택된 장소 정보 업데이트"""
    try:
        config = {"configurable": {"thread_id": request.thread_id}}
        snapshot = graph.get_state(config, subgraphs=True)

        if not snapshot.tasks:
            raise HTTPException(status_code=400, detail="No active tasks to update")

        # 기존 선택된 장소들 가져오기
        existing_selected_places = snapshot.tasks[0].state.values.get(
            "selected_places", []
        )
        # 선택된 장소를 PlaceInfo 객체로 변환
        new_selected_places = []
        for place_dict in request.selected_places:
            try:
                # place_id 매핑 확인 (다양한 키 시도)
                place_id = (
                    place_dict.get("place_id")
                    or place_dict.get("id")
                    or place_dict.get("name", "")
                    + "_"
                    + str(hash(place_dict.get("address", "")))
                )

                place_info = PlaceInfo(
                    name=place_dict.get("name", ""),
                    address=place_dict.get("address", ""),
                    latitude=float(place_dict.get("latitude", 0.0)),
                    longitude=float(place_dict.get("longitude", 0.0)),
                    rating=float(place_dict.get("rating", 0.0)),
                    reviews=place_dict.get("reviews", []) or [],
                    place_id=place_id,
                    reason=place_dict.get("reason", ""),
                )
                new_selected_places.append(place_info)
            except Exception as e:
                continue

        # 기존 장소와 새 장소를 합치기 (name + address 조합으로 중복 제거)
        combined_places = list(existing_selected_places)  # 기존 장소 복사

        # 기존 장소들의 (name, address) 조합 추출
        existing_place_keys = set()
        for place in existing_selected_places:
            if hasattr(place, "name") and hasattr(place, "address"):
                key = (place.name.strip().lower(), place.address.strip().lower())
                existing_place_keys.add(key)

        # 새로운 장소들을 추가 (중복 방지)
        for new_place in new_selected_places:
            new_key = (
                new_place.name.strip().lower(),
                new_place.address.strip().lower(),
            )
            if new_key not in existing_place_keys:
                combined_places.append(new_place)
                existing_place_keys.add(new_key)  # 중복 방지를 위해 추가

        # 서브 그래프 상태의 selected_places 업데이트
        task_config = snapshot.tasks[0].state.config
        update_data = {
            "selected_places": combined_places,
            "messages": HumanMessage(
                content=f"선택: {','.join([p.name for p in combined_places])}"
            ),
        }
        print("*" * 100)
        print(update_data["messages"])
        print("*" * 100)
        graph.update_state(task_config, update_data)

        return {"success": True, "selected_count": len(combined_places)}
    except Exception as e:
        print(f"selected_places 업데이트 오류: {e}")
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@chat_router.post("/chat/resume")
async def resume_graph(request: ResumeRequest):
    """인터럽트된 그래프 재개"""
    try:
        config = {
            "configurable": {"thread_id": request.thread_id},
            "recursion_limit": 25,
        }
        snapshot = graph.get_state(config, subgraphs=True)
        print(snapshot.tasks[0].state.values["messages"])

        if not snapshot.tasks:
            raise HTTPException(status_code=400, detail="No active tasks to resume")

        async def event_stream():
            try:
                async for chunk in graph.astream(
                    None,
                    snapshot.tasks[0].state.config,
                    stream_mode="custom",
                    subgraphs=True,
                ):
                    yield f"data: {json.dumps({'text': chunk[1]})}\n\n"
            except Exception as e:
                print(f"========== Resume error: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@chat_router.post("/chat/history")
async def get_chat_history(request: HistoryRequest):
    """대화 이력 조회"""
    try:
        config = {"configurable": {"thread_id": request.thread_id}}
        # state_history = list(graph.get_state_history(config, limit=request.limit))
        snapshot = graph.get_state(config)

        # 대화 메시지만 추출
        chat_messages = []
        for msg in snapshot.values["messages"]:
            if hasattr(msg, "type") and msg.type in ["human", "ai"]:
                if msg.name == "message_agent" or msg.name == "supervisor":
                    chat_messages.append(
                        {
                            "role": ("human" if msg.type == "human" else "assistant"),
                            "content": msg.content,
                            # "timestamp": state.created_at,
                        }
                    )

        # chat_messages.sort(key=lambda x: x["timestamp"])

        return {"messages": chat_messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

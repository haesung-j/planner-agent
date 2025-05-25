import httpx
import json
import asyncio
from typing import Dict, List, Any, Optional, AsyncGenerator
from dataclasses import dataclass


@dataclass
class ChatMessage:
    role: str
    content: str
    timestamp: Optional[str] = None


class PlannerAPIClient:
    """Planner FastAPI 서버와 통신하는 클라이언트"""

    def __init__(self, base_url: str = "http://localhost:8000", timeout: float = 300.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """응답 처리 및 에러 핸들링"""
        if response.status_code == 200:
            return response.json()
        else:
            error_msg = (
                f"API 요청 실패 (status: {response.status_code}): {response.text}"
            )
            raise Exception(error_msg)

    def get_chat_history(self, thread_id: str, limit: int = 50) -> List[ChatMessage]:
        """대화 이력 조회"""
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.base_url}/chat/history",
                    json={"thread_id": thread_id, "limit": limit},
                )
                data = self._handle_response(response)

                return [
                    ChatMessage(
                        role=msg["role"],
                        content=msg["content"],
                        timestamp=msg.get("timestamp"),
                    )
                    for msg in data["messages"]
                ]
        except Exception as e:
            return []

    def get_graph_state(self, thread_id: str) -> Dict[str, Any]:
        """그래프 상태 조회"""
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                f"{self.base_url}/chat/state", json={"thread_id": thread_id}
            )
            return self._handle_response(response)

    def update_graph_state(self, thread_id: str, content: str) -> bool:
        """그래프 상태 업데이트"""
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.base_url}/chat/update_state",
                    json={"thread_id": thread_id, "messages": {"content": content}},
                )
                data = self._handle_response(response)
                return data.get("success", False)
        except Exception as e:
            return False

    def update_selected_places(
        self, thread_id: str, selected_places: List[Dict[str, Any]]
    ) -> bool:
        """선택된 장소 정보 업데이트"""
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.base_url}/chat/update_selected_places",
                    json={"thread_id": thread_id, "selected_places": selected_places},
                )
                data = self._handle_response(response)
                return data.get("success", False)
        except Exception as e:
            print(f"선택된 장소 업데이트 실패: {e}")
            return False

    async def chat_stream(
        self, query: str, thread_id: str
    ) -> AsyncGenerator[str, None]:
        """채팅 스트리밍"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/stream",
                json={"query": query, "thread_id": thread_id},
            ) as response:
                async for chunk in response.aiter_text():
                    if chunk.strip():
                        lines = chunk.strip().split("\n")
                        for line in lines:
                            if line.startswith("data: "):
                                try:
                                    data = json.loads(line[6:])
                                    if "text" in data:
                                        yield data["text"]
                                except json.JSONDecodeError:
                                    continue

    async def resume_graph(self, thread_id: str) -> AsyncGenerator[str, None]:
        """그래프 재개"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/resume",
                json={"thread_id": thread_id},
            ) as response:
                async for chunk in response.aiter_text():
                    if chunk.strip():
                        lines = chunk.strip().split("\n")
                        for line in lines:
                            if line.startswith("data: "):
                                try:
                                    data = json.loads(line[6:])
                                    if "text" in data:
                                        yield data["text"]
                                except json.JSONDecodeError:
                                    continue

    def health_check(self) -> bool:
        """서버 상태 확인"""
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except:
            return False

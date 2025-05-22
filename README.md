# planner


## Features
1. Agent 관리
    1. **에이전트 등록**:
    `backend/app/agents/registry.py` 파일에 새로운 에이전트 추가

    ```python
    AGENTS_REGISTRY: Dict[str, AgentInfo] = {
        "new_agent": {
            "description": "새로운 에이전트 설명",
            "enabled": True
        },
        # 기존 에이전트...
    }
    ```

    2. **에이전트 비활성화**:
    레지스트리에서 `enabled` 값을 `False`로 설정
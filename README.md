# 여행 계획 AI 서비스

멀티 에이전트 AI 시스템을 활용하여 자연스러운 대화를 통해 개인화된 여행 일정을 생성하는 지능형 여행 계획 서비스입니다.

## 시스템 아키텍처

<div align="center">
  <img src="assets/rough_architecture.png" alt="시스템 아키텍처" width="800">
  <br>
  <em>현재 시스템 구조: 3계층 컨테이너 기반 애플리케이션</em>
</div>

### 시스템 구성 요소

| 구성 요소 | 기술 스택 | 포트 | 설명 |
|-----------|-----------|------|------|
| **웹 프록시** | Nginx | 80 | 단일 진입점, Streamlit으로 요청 전달 |
| **프론트엔드** | Streamlit | 8501 | 대화형 웹 인터페이스 |
| **백엔드** | FastAPI | 8000 | 멀티 에이전트 시스템 기반 REST API |

### 주요 기능

- **멀티 에이전트 AI 시스템** - 각 계획 작업에 특화된 전문 에이전트
- **구글 맵스 연동** - 실시간 장소 검색 및 상세 정보 제공
- **캘린더 연동** - 구글 캘린더 동기화
- **대화형 인터페이스** - 자연어 기반 여행 계획 수립
- **실시간 스트리밍** - 실시간 응답 생성

## 빠른 시작

```bash
# 저장소 복제 및 애플리케이션 실행
git clone <repository-url>
cd planner
docker-compose up -d
```

`http://localhost`으로 접속할 수 있습니다.

## 기술 스택

- **백엔드**: FastAPI, LangGraph, LangChain
- **프론트엔드**: Streamlit
- **AI 모델**: OpenAI GPT
- **외부 API**: Google Maps, Google Calendar, Gmail
- **인프라**: Docker, Nginx
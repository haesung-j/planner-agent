import streamlit as st
import pandas as pd
import json
import asyncio
import httpx
import os
import uuid

from client import PlannerAPIClient, ChatMessage

# FastAPI 서버 URL
API_BASE_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")
api_client = PlannerAPIClient(base_url=API_BASE_URL)


def display_search_place_results(thread_id):
    """tool_call 결과를 streamlit에 표출하는 함수"""

    # 현재 그래프 상태 가져오기
    state_data = api_client.get_graph_state(thread_id)

    if not state_data["has_tasks"]:
        return None

    selected_data = None
    last_message = state_data["tasks"][0]["last_message"]  # last tool message

    if last_message:
        st.subheader("🔧 Tool 실행 결과")

        try:
            # JSON으로 파싱 시도
            if isinstance(last_message["content"], str):
                result_data = json.loads(last_message["content"])
            else:
                result_data = last_message["content"]

            # 결과를 DataFrame으로 표시
            if isinstance(result_data, list) and len(result_data) > 0:
                if isinstance(result_data[0], dict):
                    df = pd.DataFrame(result_data)

                    # 고유한 키 생성 (현재 툴 결과의 해시값 사용)
                    df_key = f"dataframe_{hash(str(result_data))}"

                    st.write("📋 **아래 테이블에서 원하는 장소를 선택하세요:**")

                    # 선택된 데이터를 세션 상태에서 확인
                    selected_key = f"selected_{df_key}"

                    selection_event = st.dataframe(
                        df,
                        on_select="rerun",
                        selection_mode="multi-row",
                        key=df_key,
                        use_container_width=True,
                    )

                    # 선택된 행이 있는지 확인
                    if selection_event.selection.rows:
                        selected_rows = selection_event.selection.rows
                        selected_df = df.iloc[selected_rows]

                        # 선택된 데이터를 세션 상태에 저장
                        st.session_state[selected_key] = selected_df

                        # 선택 여부 확인
                        if st.button(
                            f"선택한 {len(selected_rows)}개 장소로 계속 진행",
                            key=f"continue_{df_key}",
                        ):
                            selected_data = selected_df.to_dict("records")

                            # 선택 결과 업데이트
                            success = api_client.update_graph_state(
                                thread_id, str(selected_data)
                            )

                            if success:
                                return selected_data
                            else:
                                return None

                    # # 이전에 선택된 데이터가 있다면 표시
                    # elif selected_key in st.session_state:
                    #     previous_selection = st.session_state[selected_key]

                    #     col1, col2 = st.columns(2)
                    #     with col1:
                    #         if st.button(
                    #             f"이전 선택({len(previous_selection)}개 장소)으로 계속 진행",
                    #             key=f"continue_prev_{df_key}",
                    #         ):
                    #             st.session_state.show_tool_results = False
                    #             # dict 형태로 변환하여 반환
                    #             selected_data = previous_selection.to_dict("records")
                    #             return selected_data
                    #     with col2:
                    #         if st.button("다시 선택하기", key=f"reselect_{df_key}"):
                    #             del st.session_state[selected_key]
                    #             st.rerun()

        except json.JSONDecodeError:
            st.text(last_message["content"])

    # 항상 None이나 dict list만 반환하도록 수정
    return selected_data


# Streamlit 앱에서 사용 예시
def main():
    st.set_page_config(
        page_title="Place Researcher - Human in the Loop", page_icon="🤖", layout="wide"
    )

    if not api_client.health_check():
        st.error("API 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
        st.stop()

    # 세션 상태 초기화
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())

    # 메세지 초기화
    if "messages" not in st.session_state:
        try:
            chat_messages = api_client.get_chat_history(st.session_state.thread_id)
            st.session_state.messages = [
                {"role": msg.role, "content": msg.content} for msg in chat_messages
            ]
        except Exception as e:
            # 새로운 thread_id이거나 서버에 기록이 없는 경우 빈 배열로 초기화
            # print(f"대화 이력 로드 실패: {e}")
            st.session_state.messages = []

    if "human_in_the_loop" not in st.session_state:
        st.session_state.human_in_the_loop = False

    # 사이드바에 설정 정보 표시
    with st.sidebar:
        st.write("**세션 정보**")
        st.write(f"Thread ID: {st.session_state.thread_id[:8]}...")

        if st.button("새 대화 시작"):
            st.session_state.thread_id = str(uuid.uuid4())
            st.session_state.messages = []
            st.rerun()

    # 이전 메시지들 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if st.session_state.human_in_the_loop:
        state_data = api_client.get_graph_state(st.session_state.thread_id)

        print("^" * 100)
        print(state_data)
        print(st.session_state.thread_id)
        last_message = state_data["tasks"][0]["last_message"]
        if last_message and last_message["type"] == "tool":
            tool_name = last_message["name"]
            st.info(f"tool_name: {tool_name}")

            #! search_place 인 경우
            if tool_name == "search_place":
                with st.container():
                    selected_data = display_search_place_results(
                        st.session_state.thread_id
                    )
                    if selected_data:
                        st.success("선택이 완료되었습니다! 응답을 생성중입니다...")
                        # 재개 시점
                        subgraph_config = state_data["tasks"][0]["config"]
                        with st.chat_message("assistant"):
                            message_placeholder = st.empty()

                            async def resume_execution():
                                response = ""
                                async for chunk in api_client.resume_graph(
                                    st.session_state.thread_id
                                ):
                                    response += chunk
                                    message_placeholder.markdown(response)

                                st.session_state.messages.append(
                                    {"role": "assistant", "content": response}
                                )
                                st.session_state.human_in_the_loop = False

                            asyncio.run(resume_execution())

            else:
                # 다른 tool의 경우 그래프 재개
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    print("*" * 100)
                    print("다른 툴이자나")

                    async def resume_execution():
                        response = ""
                        async for chunk in api_client.resume_graph(
                            st.session_state.thread_id
                        ):
                            response += chunk
                            message_placeholder.markdown(response)

                        st.session_state.messages.append(
                            {"role": "assistant", "content": response}
                        )
                        st.session_state.human_in_the_loop = False
                        st.rerun()

                    asyncio.run(resume_execution())

    # 사용자 입력
    if query := st.chat_input("메시지를 입력하세요"):
        # 사용자 메시지 표시
        with st.chat_message("human"):
            st.markdown(query)

        st.session_state.messages.append({"role": "human", "content": query})

        with st.chat_message("assistant"):
            message_placeholder = st.empty()

            async def stream_events():
                full_response = ""
                async for chunk in api_client.chat_stream(
                    query, st.session_state.thread_id
                ):
                    full_response += chunk
                    message_placeholder.markdown(full_response)

                # 인터럽트가 발생했는지 확인하고 tool 결과 표시
                state_data = api_client.get_graph_state(st.session_state.thread_id)
                print("*" * 100)
                print(state_data)
                if state_data["has_tasks"]:
                    last_message = state_data["tasks"][0]["last_message"]
                    if last_message:
                        print("*" * 100)
                        print("HUMAN IN THE LOOP")
                        st.session_state.human_in_the_loop = True
                    st.rerun()
                else:
                    st.session_state.messages.append(
                        {"role": "assistant", "content": full_response}
                    )
                # if snapshot.tasks:  # interrupt 발생 시
                #     # search_place tool 호출로 인한 interrupt인 경우,
                #     if (
                #         snapshot.tasks[0].state.values["messages"][-1].name
                #         == "search_place"
                #     ):
                #         st.session_state.human_in_the_loop = True
                #     st.rerun()
                # else:
                #     # 정상 완료된 경우 메시지 저장
                #     st.session_state.messages.append(
                #         {"role": "assistant", "content": full_response}
                #     )

            asyncio.run(stream_events())


if __name__ == "__main__":
    main()

import streamlit as st
from utils import print_messages, StreamHandler
from langchain_core.messages import ChatMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

st.set_page_config(page_title="ChatGPT", page_icon=":)")
st.title("Chatgpt")

# 세션 스테이트는 캐싱을 해줘서 새로 고침이 일어나도 데이터를 보관을 해준다.
if "messages" not in st.session_state:  # 세션 스테이트에 messages라는 키값이 없으면
    st.session_state["messages"] = []  # 새로운 리스트 생성, 우리가 입력한 메세지 추가


# 체팅 대화 기록을 저장하는 store 세션 상태 변수 
if "store" not in st.session_state:
    st.session_state["store"] = dict()

with st.sidebar:
    session_id = st.text_input("Session ID", value="abc123")


# 이전 대화 기록 출력
print_messages()

# 세션 ID를 기반으로 세션 기록을 가져오는 함수
def get_session_history(session_ids: str) -> BaseChatMessageHistory:
    if session_ids not in st.session_state["store"]:  # 세션 ID가 store에 없는 경우
        st.session_state["store"][session_ids] = ChatMessageHistory()  # 새로운 ChatMessagesHistory 객체를 생성하여 store에 저장

    return st.session_state["store"][session_ids]  # 헤당 세션 아이디에 대한 세션 기록 반환



if user_input := st.chat_input("Say something"):
    # 사용자가 입력한 내용
    st.chat_message("user").write(f"{user_input}")
    st.session_state["messages"].append(ChatMessage(role="user", content=user_input))

    # AI의 답변
    with st.chat_message("assistant"):
        stream_handler = StreamHandler(st.empty())

        # LLM을 사용하여 AI의 답변을 생성

        # 1. 모델 생성
        llm = ChatOpenAI(streaming=True, callbacks=[stream_handler])
        
        # 2. 프롬프트 생성
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "질문에 짧고 간결하게 답변해."),
                # 대화 기록을 변수로 사용, history가 MessageHistory의 key가 됨 
                MessagesPlaceholder(variable_name="history"),
                ("human", "{question}"),  # 사용자 질문을 변수로 사용
            ]
        )

        chain = prompt | llm

        chain_with_memory = (
            RunnableWithMessageHistory(  # RunnableWithMessageHistory 객체 생성
                chain,  # 실행할 Runnable 객체
                get_session_history,  # 세션 기록을 가져오는 함수
                input_messages_key="question",  # 사용자 질문의 키
                history_messages_key="history",  # 기록 메세지의 키 
            )
        )

        # response = chian.invoke({"question": user_input})
        response = chain_with_memory.invoke(
            {"question": user_input},
            # 세션ID 설정 
            config={"configurable": {"session_id": session_id}},
        )

        msg = response.content
        st.session_state["messages"].append(ChatMessage(role="assistant", content=msg))  # messages 안에 튜플 형식으로 추가



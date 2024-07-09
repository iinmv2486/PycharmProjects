from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

store = {} # 세션 기록을 저장할 딕셔너리

# 세션 ID를 기반으로 세션 기록을 가져오는 함수
def get_session_history(session_ids: str) -> BaseChatMessageHistory:
    print(session_ids)
    if session_ids not in store:  # 세션 ID가 store에 없는 경우
        store[session_ids] = ChatMessageHistory()  # 새로운 ChatMessagesHistory 객체를 생성하여 store에 저장

    return store[session_ids]  # 헤당 세션 아이디에 대한 세션 기록 반환


with_message_history = (
    RunnableWithMessageHistory(  # RunnableWithMessageHistory 객체 생성
        runnable,  # 실행할 Runnable 객체
        get_session_history,  # 세션 기록을 가져오는 함수
        input_messages_key="input",  # 입력 메세지의 키
        history_messages_key="history",  # 기록 메세지의 키 
    )
)

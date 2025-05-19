import streamlit as st
from datetime import datetime
from modules.kpi_dashboard import get_kpi_records, parse_kpi_text_to_dict
from modules.strategy_chatbot_logic import (
    run_strategy_analysis, create_new_chatroom,
    save_chat_message, get_chat_history, display_typing_effect
)
from modules.chatdb import ChatRoom, chat_session, init_chat_db
from modules.gemini_api import call_gemini

# 초기 설정
st.set_page_config(page_title="🧠 전략 챗봇", layout="wide")
init_chat_db()
st.title("🤖 Gemini 기반 전략 챗봇")

# 상태 초기화
if "chat_triggered" not in st.session_state:
    st.session_state["chat_triggered"] = False
if "selected_chatroom_id" not in st.session_state:
    st.session_state["selected_chatroom_id"] = None

# 사이드바 - 채팅방 목록
with st.sidebar:
    # ✅ 새 채팅 시작하기 버튼
    if st.button("🆕 새 채팅 시작하기"):
        st.session_state["selected_chatroom_id"] = None
        st.session_state["chat_triggered"] = False
        st.rerun()
    st.markdown("## 💬 채팅방 목록")
    chatrooms = chat_session.query(ChatRoom).order_by(ChatRoom.created_at.asc()).all()
    label_counts = {}

    for chat in chatrooms:
        base_kpi = chat.kpi_name.split("-")[0]
        base_label = f"{chat.company}-{base_kpi}"
        label_counts[base_label] = label_counts.get(base_label, 0) + 1
        label = base_label if label_counts[base_label] == 1 else f"{base_label}-{label_counts[base_label]}"

        if st.button(label, key=f"load_{chat.id}"):
            st.session_state["selected_chatroom_id"] = chat.id
            st.session_state["chat_triggered"] = True

        timestamp_str = chat.created_at.strftime("%m/%d %H:%M")
        st.markdown(
            f"<div style='margin-top:-10px; margin-bottom:5px; color:gray; font-size:12px;'>{timestamp_str}</div>",
            unsafe_allow_html=True
        )

        if st.button("🗑️ 삭제", key=f"delete_{chat.id}"):
            chat_session.delete(chat)
            chat_session.commit()
            st.rerun()

# KPI 선택
records = get_kpi_records()
companies = sorted({r.company for r in records})
selected_company = st.selectbox("📌 회사 선택", companies)

if selected_company:
    record = next((r for r in records if r.company == selected_company), None)
    kpis = parse_kpi_text_to_dict(record.kpi_text)
    kpi_names = [k["KPI 명"] for k in kpis]
    selected_kpi = st.selectbox("🎯 KPI 선택", kpi_names)

    if st.button("🔍 전략 분석 요청"):
        with st.spinner("Gemini 분석 중..."):
            result = run_strategy_analysis(selected_company, selected_kpi)
            chatroom = create_new_chatroom(selected_company, selected_kpi)

            st.session_state["selected_chatroom_id"] = chatroom.id
            st.session_state["chat_triggered"] = True

            save_chat_message(chatroom.id, "user", f"[분석 요청] KPI: {selected_kpi}")
            save_chat_message(chatroom.id, "gemini", result)
            st.rerun()
            st.success("분석 완료! 채팅창에서 확인하세요.")

# 채팅창 표시 조건
if st.session_state.get("chat_triggered") and st.session_state.get("selected_chatroom_id"):
    chatroom_id = st.session_state["selected_chatroom_id"]
    chatroom = chat_session.query(ChatRoom).filter_by(id=chatroom_id).first()

    if chatroom:
        st.subheader(f"💬 {chatroom.company} - {chatroom.kpi_name} 전략 대화")
        chat_history = get_chat_history(chatroom_id)

        for msg in chat_history:
            role = "user" if msg.sender == "user" else "assistant"
            with st.chat_message(role):
                st.markdown(msg.content)

        user_input = st.chat_input("메시지를 입력하세요...")

        if user_input:
            save_chat_message(chatroom_id, "user", user_input)
            with st.chat_message("user"):
                st.markdown(user_input)

            gemini_reply = call_gemini(user_input)
            save_chat_message(chatroom_id, "gemini", gemini_reply)
            with st.chat_message("assistant"):
                display_typing_effect(gemini_reply)

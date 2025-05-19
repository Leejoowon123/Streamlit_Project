from datetime import date, datetime
from modules.chatdb import ChatRoom, ChatMessage, chat_session
from modules.db import KPIDeadline, KPIDailyProgress, session as kpi_session
from modules.prompts_loader import load_prompt
from modules.gemini_api import call_gemini
import streamlit as st
import time

def get_kpi_summary_context(company_name: str, kpi_name: str):
    meta = kpi_session.query(KPIDeadline).filter_by(company=company_name, kpi_name=kpi_name).first()
    progress = kpi_session.query(KPIDailyProgress).filter_by(
        company=company_name, kpi_name=kpi_name
    ).order_by(KPIDailyProgress.date.asc()).all()

    actuals = [p.actual for p in progress]
    recent_trend = "하락세" if len(actuals) >= 5 and actuals[-1] < actuals[-2] else "상승세"
    cumulative = sum(actuals)
    avg = sum(actuals[-5:]) / min(5, len(actuals)) if actuals else 0
    current_rate = cumulative / meta.target * 100 if meta and meta.target else 0

    return {
        "KPI 명": kpi_name,
        "측정 기준": meta.measure if meta else "",
        "목표값": meta.target if meta else 0,
        "마감기한": str(meta.deadline if meta else date.today()),
        "누적 실적": cumulative,
        "현재 달성률": round(current_rate, 2),
        "최근 평균 실적": round(avg, 2),
        "최근 추세": recent_trend
    }

def build_strategy_prompt(company_name, kpi_info, prompt_stage="strategy_kpi"):
    template = load_prompt(prompt_stage, company_name)
    for key, val in kpi_info.items():
        template = template.replace(f"{{{key}}}", str(val))
    return template

def run_strategy_analysis(company_name, kpi_name):
    kpi_info = get_kpi_summary_context(company_name, kpi_name)
    prompt = build_strategy_prompt(company_name, kpi_info)
    response = call_gemini(prompt)
    return response

def create_new_chatroom(company_name, kpi_name):
    base_kpi_like = f"{kpi_name}%"
    existing_rooms = chat_session.query(ChatRoom).filter(
        ChatRoom.company == company_name,
        ChatRoom.kpi_name.like(base_kpi_like)
    ).all()

    suffixes = []
    for room in existing_rooms:
        rest = room.kpi_name.replace(kpi_name, "").replace("-", "")
        if rest.isdigit():
            suffixes.append(int(rest))
        elif rest == "":
            suffixes.append(1)

    next_suffix = max(suffixes + [1]) + 1 if suffixes else 1
    new_kpi_name = kpi_name if next_suffix == 2 else f"{kpi_name}-{next_suffix - 1}"

    new_chatroom = ChatRoom(
        company=company_name,
        kpi_name=new_kpi_name,
        created_at=datetime.now()
    )
    chat_session.add(new_chatroom)
    chat_session.commit()
    return new_chatroom

def save_chat_message(chatroom_id, sender, content):
    msg = ChatMessage(chatroom_id=chatroom_id, sender=sender, content=content, timestamp=datetime.now())
    chat_session.add(msg)
    chat_session.commit()

def get_chat_history(chatroom_id):
    return chat_session.query(ChatMessage).filter_by(chatroom_id=chatroom_id).order_by(ChatMessage.timestamp.asc()).all()

def display_typing_effect(text, delay=0.01):
    output = st.empty()
    typed_text = ""
    for char in text:
        typed_text += char
        output.markdown(typed_text)
        time.sleep(delay)

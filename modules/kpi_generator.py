import os
from modules.db import get_analysis_by_company
from modules.analyzer import run_full_analysis, STAGES
from modules.prompts_loader import load_prompt
from modules.gemini_api import call_gemini
from modules.history import save_analysis_result
import streamlit as st

def generate_kpis(company_name):
    # 1. DB에서 회사 분석 결과 가져오기
    record = get_analysis_by_company(company_name)

    if record:
        combined_text = "\n\n".join(record["분석결과"].values())
    else:
        # 2. 분석 이력이 없으면 전체 분석 실행
        result = run_full_analysis(company_name, STAGES)
        combined_text = "\n\n".join([v for k, v in result.items() if not k.startswith("__")])
        st.session_state["result"] = result
        save_analysis_result(company_name, result)
    # 3. KPI 프롬프트 구성
    prompt = load_prompt("kpi", company_name).replace("{{분석내용}}", combined_text)

    try:
        return call_gemini(prompt).strip()
    except Exception as e:
        return f"❌ KPI 생성 실패: {e}"

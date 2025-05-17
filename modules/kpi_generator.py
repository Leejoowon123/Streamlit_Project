import json
import os
from modules.db import get_analysis_by_company, save_result_to_db
from modules.analyzer import run_full_analysis, STAGES, generate_pdf_report
from modules.prompts_loader import load_prompt
from modules.gemini_api import call_gemini
from modules.history import save_analysis_result
import streamlit as st
from datetime import datetime
from typing import List, Dict
import re

def generate_kpis(company_name):
    record = get_analysis_by_company(company_name)

    if record:
        combined_text = record["분석결과"]
    else:
        # 분석 이력이 없으면 전체 분석
        result = run_full_analysis(company_name, STAGES)
        combined_text = "\n\n".join([v for k, v in result.items() if not k.startswith("__")])
        st.session_state["result"] = result
        save_analysis_result(company_name, result)

        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)

        today = datetime.now().strftime("%Y.%m.%d")
        filename = f"{today}_{company_name}_전략분석.pdf"
        file_path = os.path.join(output_dir, filename)
        pdf_path = generate_pdf_report(company_name, result, file_path=file_path)
        save_result_to_db(company_name, result, pdf_path)

    prompt = load_prompt("kpi", company_name).replace("{{분석내용}}", combined_text)

    try:
        return call_gemini(prompt).strip()
    except Exception as e:
        return f"KPI 생성 실패: {e}"
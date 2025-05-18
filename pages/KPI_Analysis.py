import streamlit as st
from modules.kpi_generator import generate_kpis
from modules.analyzer import generate_pdf_report_with_structured_kpi
from modules.db import save_kpi_analysis_result
import os
from datetime import datetime

st.set_page_config(page_title="KPI 자동 생성", layout="wide")
st.title("전략 KPI 자동 생성")

company_name = st.text_input("회사명을 입력하세요", "")

if st.button("KPI 생성하기") and company_name.strip():
    
    with st.spinner("KPI를 생성 중입니다..."):
        kpi_text = generate_kpis(company_name)
        today = datetime.now().strftime("%Y.%m.%d")
        pdf_filename = f"{today}_{company_name}_KPI분석.pdf"
        pdf_path = os.path.join("output", pdf_filename)

        generate_pdf_report_with_structured_kpi(
            company_name,
            {"KPI 분석 결과": kpi_text},
            file_path=pdf_path
        )
        save_kpi_analysis_result(company_name, kpi_text, pdf_path)

        st.session_state["kpi_text"] = kpi_text
        st.session_state["kpi_pdf_path"] = pdf_path
        st.session_state["kpi_filename"] = pdf_filename
        st.session_state["kpi_company"] = company_name

if (
    st.session_state.get("kpi_text")
    and st.session_state.get("kpi_pdf_path")
    and st.session_state.get("kpi_filename")
    and os.path.exists(st.session_state["kpi_pdf_path"])
):
    st.markdown("### 🔍 KPI 분석 결과")
    with open(st.session_state["kpi_pdf_path"], "rb") as f:
        st.download_button(
            label="📥 PDF 다운로드",
            data=f,
            file_name=st.session_state["kpi_filename"],
            mime="application/pdf",
        )
    st.success("KPI 분석 완료!")
    kpi_text = st.session_state["kpi_text"] 
    st.markdown(f"{kpi_text}")
else:
    st.info("👆 회사명을 입력하고 KPI 생성 버튼을 눌러주세요.")
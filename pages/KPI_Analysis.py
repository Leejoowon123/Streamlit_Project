import streamlit as st
from modules.kpi_generator import generate_kpis
from modules.analyzer import generate_pdf_report
from modules.db import save_kpi_analysis_result
import os
from datetime import datetime

st.set_page_config(page_title="📊 KPI 자동 생성", layout="wide")
st.title("📊 전략 KPI 자동 생성")

company_name = st.text_input("회사명을 입력하세요", "")

if st.button("KPI 생성하기") and company_name.strip():
    with st.spinner("KPI를 생성 중입니다..."):
        kpi_text = generate_kpis(company_name)
        today = datetime.now().strftime("%Y.%m.%d")
        pdf_filename = f"{today}_{company_name}_KPI분석.pdf"
        pdf_path = os.path.join("output", pdf_filename)

        # ✅ KPI 내용만 PDF로 저장
        generate_pdf_report(company_name, {"KPI 분석 결과": kpi_text}, file_path=pdf_path)

        save_kpi_analysis_result(company_name, kpi_text, pdf_path)

    st.success("✅ KPI 분석 완료!")
    st.download_button(
        label="📥 PDF 다운로드",
        data=open(pdf_path, "rb"),
        file_name=pdf_filename,
        mime="application/pdf",
    )

    st.subheader("🔍 KPI 분석 결과")
    st.markdown(kpi_text)

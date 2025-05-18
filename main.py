import os
import streamlit as st
from datetime import datetime
from modules.analyzer import run_full_analysis, generate_pdf_report, STAGES
from modules.history import save_analysis_result
from modules.db import init_db, save_result_to_db

init_db()
st.set_page_config(page_title="전략 분석 프로그램", layout="wide")
st.title("📊 기업 전략 분석 자동화")

# ✅ 사용자 입력: 회사명 + 분석 항목 선택
available_sections = [stage[0] for stage in STAGES]
selected_sections = st.multiselect("📌 실행할 분석 항목을 선택하세요", options=available_sections, default=available_sections)
company_name = st.text_input("분석할 기업명을 입력하세요:")

if st.button("분석 실행") and company_name:
    selected_stages = [stage for stage in STAGES if stage[0] in selected_sections]
    with st.spinner("🔄 분석 중입니다. 잠시만 기다려주세요..."):
        result = run_full_analysis(company_name, selected_stages)
        st.session_state["result"] = result
        save_analysis_result(company_name, result)

        today = datetime.now().strftime("%Y.%m.%d")
        filename = f"{today}_{company_name}_전략분석.pdf"
        file_path = os.path.join("output", filename)
        pdf_path = generate_pdf_report(company_name, result, file_path=file_path)
        save_result_to_db(company_name, result, pdf_path)

        st.session_state["pdf_path"] = pdf_path
        st.session_state["filename"] = filename
        st.session_state["company"] = company_name 

if "result" in st.session_state:
    result = st.session_state["result"]
    summary_text = result.get("__요약__")
    keywords_text = result.get("__키워드__")

    st.markdown("### 🔍 분석 결과")

    pdf_path = st.session_state.get("pdf_path")
    filename = st.session_state.get("filename")
    if pdf_path and filename and os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="📥 PDF 다운로드",
                data=f,
                file_name=filename,
                mime="application/pdf",
            )

    st.success("✅ 분석 완료! PDF 저장 가능")
    if summary_text:
        st.markdown("### 📝 요약")
        st.markdown(summary_text)

    if keywords_text:
        st.markdown("### 🔑 핵심 키워드")
        st.markdown(f"**{keywords_text}**")

    for section, content in result.items():
        if section.startswith("__"):
            continue
        st.markdown(f"#### 📌 {section}")
        st.markdown(content.replace("\n", "  \n"))

else:
    st.info("👆 기업명을 입력하고 버튼을 눌러 분석을 시작하세요.")
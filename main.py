import os
import streamlit as st
from datetime import datetime
from modules.analyzer import run_full_analysis, generate_pdf_report, STAGES
from modules.history import save_analysis_result, get_saved_analysis_titles, get_analysis_by_index

st.set_page_config(page_title="전략 분석 프로그램", layout="wide")
st.title("📊 기업 전략 분석 자동화")

# ✅ 사이드바: 이전 분석 이력
with st.sidebar:
    st.header("📌 이전 분석 이력")
    titles = get_saved_analysis_titles()
    selected = st.selectbox("이전 분석 결과 보기", options=[""] + titles)

    if selected and selected != "":
        index = titles.index(selected)
        past_result = get_analysis_by_index(index)
        st.markdown("#### 🔁 불러온 분석 결과")
        for section, content in past_result.items():
            st.markdown(f"**{section}**")
            st.markdown(content.replace("\n", "  \n"))  # ✅ 줄바꿈 유지

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

    st.markdown("### 🔍 분석 결과")
    for section, content in result.items():
        st.markdown(f"#### {section}")
        st.markdown(content.replace("\n", "  \n"))

    st.success("✅ 분석 완료! PDF 저장 가능")
    
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    today = datetime.now().strftime("%Y.%m.%d")
    filename = f"{today}_{company_name}_전략분석.pdf"
    file_path = os.path.join(output_dir, filename)
    pdf_path = generate_pdf_report(company_name, result, file_path=file_path)

    with open(pdf_path, "rb") as f:
        st.download_button(
            label="📥 PDF 다운로드",
            data=f,
            file_name=filename,
            mime="application/pdf"
        )
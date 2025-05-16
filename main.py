import os
import streamlit as st
from datetime import datetime
from modules.analyzer import run_full_analysis, generate_pdf_report, STAGES
from modules.history import save_analysis_result, get_saved_analysis_titles, get_analysis_by_index
from modules.db import init_db, save_result_to_db, get_grouped_results

init_db()
st.set_page_config(page_title="전략 분석 프로그램", layout="wide")
st.title("📊 기업 전략 분석 자동화")

# ✅ 사이드바: 이전 분석 이력
with st.sidebar.expander("📚 이전 분석 이력 보기"):
    history_records = get_grouped_results()

    if not history_records:
        st.markdown("ℹ️ 저장된 분석 이력이 없습니다.")
    else:
        for record in history_records:
            st.markdown(f"**🕒 {record['조회일']}**")
            st.markdown(f"📌 **회사명**: {record['회사명']}")
            st.markdown(f"📄 **분석 항목**: {record['분석 항목']}")

            # ✅ 요약 3문단 이하만 표시
            summary = record['요약']
            summary_paragraphs = summary.strip().split("\n")

            if len(summary_paragraphs) > 3:
                short_summary = "\n".join(summary_paragraphs[:3]) + "\n..."
                st.markdown("📌 요약:")
                st.markdown(short_summary)
                with st.expander("📖 더보기 (전체 요약 보기)"):
                    st.markdown(summary)
            else:
                st.markdown("📌 요약:")
                st.markdown(summary)

            st.markdown(f"🔑 **키워드**: {record['키워드']}")

            # PDF 다운로드
            try:
                with open(record["PDF 경로"], "rb") as pdf_file:
                    st.download_button(
                        label="📥 PDF 다운로드",
                        data=pdf_file,
                        file_name=record["PDF 파일명"],
                        mime="application/pdf",
                        key=record["PDF 파일명"]
                    )
            except Exception as e:
                st.error(f"PDF 파일을 불러올 수 없습니다: {e}")

            st.markdown("---")

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
    
    summary_text = result.get("__요약__")
    keywords_text = result.get("__키워드__")
    
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    today = datetime.now().strftime("%Y.%m.%d")
    filename = f"{today}_{company_name}_전략분석.pdf"
    file_path = os.path.join(output_dir, filename)
    pdf_path = generate_pdf_report(company_name, result, file_path=file_path)
    save_result_to_db(company_name, result, pdf_path)
    with open(pdf_path, "rb") as f:
        st.download_button(
            label="📥 PDF 다운로드",
            data=f,
            file_name=filename,
            mime="application/pdf"
        )


    st.markdown("### 🔍 분석 결과")
        
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

    st.success("✅ 분석 완료! PDF 저장 가능")
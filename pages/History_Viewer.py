import streamlit as st
import pandas as pd
from modules.db import get_grouped_results, get_all_kpi_results
import os

st.set_page_config(page_title="📊 분석 이력", layout="wide")
st.title("📄 전체 분석 결과 이력")

results = get_grouped_results()

if results:
    st.markdown("### 🔍 분석 이력 조회 결과")

    for r in results:
        with st.expander(f"{r['조회일']} | {r['회사명']}"):
            st.write(f"**분석 항목:** {r['분석 항목']}")
            st.write(f"📌 요약: {r['요약']}")
            st.write(f"🔑 키워드: {r['키워드']}")
            pdf_path = r["PDF 경로"]
            file_name = r["PDF 파일명"]
            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="📥 PDF 다운로드",
                        data=f,
                        file_name=file_name,
                        mime="application/pdf",
                        key=f"analysis_{r['회사명']}_{r['조회일']}"
                    )
            else:
                st.warning("PDF 파일을 찾을 수 없습니다.")
else:
    st.info("저장된 분석 이력이 없습니다.")

st.divider()

st.title("🏁 KPI 분석 결과 이력")
kpi_results = get_all_kpi_results()

if kpi_results:
    for r in kpi_results:
        with st.expander(f"{r.timestamp.strftime('%Y-%m-%d %H:%M')} | {r.company}"):
            st.markdown("이 분석은 KPI 자동 생성 결과입니다.")
            if os.path.exists(r.pdf_path):
                with open(r.pdf_path, "rb") as f:
                    st.download_button(
                        label="📥 KPI PDF 다운로드",
                        data=f,
                        file_name=os.path.basename(r.pdf_path),
                        mime="application/pdf",
                        key=f"kpi_{r.id}"
                    )
            else:
                st.warning("PDF 파일을 찾을 수 없습니다.")
else:
    st.info("저장된 KPI 분석 이력이 없습니다.")

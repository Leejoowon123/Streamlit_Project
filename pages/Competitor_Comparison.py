import streamlit as st
from modules.industry import get_competitor_comparison_table
import pandas as pd
from io import StringIO
import re

st.set_page_config(page_title="경쟁사 비교", page_icon="📊")

st.title("📊 경쟁사 비교 대시보드")

company_name = st.text_input("비교할 기업명을 입력하세요:", value="삼성전자")
st.text("브랜드 인지도는 주관적인 평가이며, R&D 투자 비중 및 글로벌 진출도는 공개된 정보를 바탕으로 추정")

if st.button("경쟁사 비교 실행"):
    with st.spinner("🔍 Gemini를 통해 경쟁사 분석 중입니다..."):
        raw_text = get_competitor_comparison_table(company_name)

        match = re.search(r"\|.*\|\n(\|.*\|\n)+", raw_text)
        if match:
            markdown_table = match.group()
        else:
            st.error("마크다운 표를 추출하지 못했습니다.")
            st.text_area("🔍 원본 응답:", raw_text, height=300)
            st.stop()

        try:
            df = pd.read_csv(StringIO(markdown_table), sep="|", engine="python").dropna(axis=1, how="all")
            df.columns = [col.strip() for col in df.columns]
            df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

            st.markdown("### 📊 비교 표")
            st.dataframe(df)
        except Exception as e:
            st.error(f"표 변환 실패: {e}")
            st.text_area("추출된 표 텍스트:", markdown_table, height=300)
import streamlit as st
from modules.industry import analyze_industry

st.set_page_config(page_title="산업 분석", layout="wide")
st.title("🏭 산업 분석")

company = st.text_input("🔎 분석할 기업명을 입력하세요")

if st.button("산업 분석 실행") and company:
    with st.spinner("산업 분석 중입니다..."):
        result = analyze_industry(company)
        st.markdown("### ✅ 분석 결과")
        st.markdown(result)
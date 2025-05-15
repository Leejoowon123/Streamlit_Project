import streamlit as st
from modules.strategy import suggest_strategy

st.set_page_config(page_title="전략 제안 및 경쟁사 분석", layout="wide")
st.title("📈 전략 제안 및 경쟁사 분석")

company = st.text_input("🏢 기업명을 입력하세요")

if company:
    with st.spinner("전략 제안 생성 중입니다..."):
        strategy = suggest_strategy(company)
        st.markdown("### 💡 전략 제안 결과")
        st.markdown(strategy)

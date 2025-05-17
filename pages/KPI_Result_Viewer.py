import streamlit as st
import plotly.graph_objects as go
from modules.kpi_dashboard import parse_kpi_text_to_dict, get_kpi_records

st.set_page_config(page_title="KPI 시각화", layout="wide")

# ✅ KPI 히스토리 가져오기
kpi_history = get_kpi_records()
if not kpi_history:
    st.warning("저장된 KPI 분석 결과가 없습니다.")
    st.stop()

# ✅ 회사 선택
company_list = list({record.company for record in kpi_history})
selected_company = st.sidebar.selectbox("📌 회사 선택", company_list)

# ✅ 해당 회사 데이터 필터링
selected_record = next((item for item in kpi_history if item.company == selected_company), None)

if selected_record:
    st.title(f"{selected_company} KPI")
    st.caption(f"분석일: {selected_record.timestamp}")

    kpi_items = parse_kpi_text_to_dict(selected_record.kpi_text)
    if not kpi_items:
        st.warning("KPI 파싱 실패. 포맷을 확인하세요.")
        st.code(selected_record.kpi_text)
        st.stop()

    # ✅ KPI 개수만큼 반복
    for idx, kpi in enumerate(kpi_items):
        st.markdown("---")
        col1, col2 = st.columns([2, 3])

        with col1:
            st.markdown(f"### {idx+1}. {kpi['KPI 명']}")
            st.markdown(f"**설명:** {kpi['설명']}")
            st.markdown(f"**측정 기준:** {kpi['측정 기준']}")
            st.markdown(f"**기대 효과:** {kpi['기대 효과']}")

        with col2:
            sub_col1, sub_col2 = st.columns([1, 1])

            with sub_col1:
                goal = st.number_input("🎯 목표값", key=f"{selected_company}_goal_{idx}", value=100)

            with sub_col2:
                actual = st.number_input("📈 실적값", key=f"{selected_company}_actual_{idx}", value=50)

            rate = actual / goal * 100
            status = f"✅ 달성률: {rate:.2f}%"

            st.markdown(f"**{status}**")
            
            # 📊 게이지 그래프
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=rate,
                title={'text': "달성률 (%)", 'font': {'size': 14}},
                gauge={
                    'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                    'bar': {'color': "blue"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightcoral"},
                        {'range': [50, 80], 'color': "lightgray"},
                        {'range': [80, 100], 'color': "lightgreen"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 3},
                        'thickness': 0.75,
                        'value': 100
                    }
                },
                domain={'x': [0, 1], 'y': [0, 1]}
            ))

            fig.update_layout(
                margin=dict(t=20, b=20, l=20, r=20),
                height=180
            )

            st.plotly_chart(fig, use_container_width=True, key=f"plot_{idx}")

else:
    st.warning("해당 회사의 KPI 분석 기록이 없습니다.")

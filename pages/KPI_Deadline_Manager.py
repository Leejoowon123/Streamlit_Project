import streamlit as st
from modules.kpi_dashboard import get_kpi_records, parse_kpi_text_to_dict
from modules.db import KPIDeadline, session, init_db
import datetime
import uuid

init_db()
st.set_page_config(page_title="KPI 기한 설정", layout="wide")
st.title("📅 KPI 달성 목표 설정")

records = get_kpi_records()
companies = list({r.company for r in records})
selected_company = st.selectbox("📌 회사 선택", companies)

if selected_company:
    record = next(r for r in records if r.company == selected_company)
    parsed_kpis = parse_kpi_text_to_dict(record.kpi_text)

    for idx, kpi in enumerate(parsed_kpis):
        existing = session.query(KPIDeadline).filter_by(company=selected_company, kpi_name=kpi['KPI 명']).first()

        if existing:
            measure_default = existing.measure
            target_default = existing.target
            deadline_default = existing.deadline
        else:
            measure_default = ""
            target_default = 0.0
            deadline_default = datetime.date.today()

        st.markdown(f"### {idx+1}. {kpi['KPI 명']}")
        measure = st.text_area("📏 측정 기준", value=measure_default, key=f"measure_{idx}")
        target = st.number_input("🎯 목표값", value=target_default, key=f"target_{idx}")
        deadline = st.date_input("📅 달성 기한", value=deadline_default, key=f"deadline_{idx}")

        if st.button(f"💾 저장 - {kpi['KPI 명']}", key=f"save_{idx}"):
            if existing:
                existing.deadline = deadline
                existing.target = target
                existing.measure = measure
            else:
                new_deadline = KPIDeadline(
                    company=selected_company,
                    kpi_name=kpi['KPI 명'],
                    deadline=deadline,
                    target=target,
                    measure=measure
                )
                session.add(new_deadline)
            session.commit()
            st.success("✅ 저장 완료")

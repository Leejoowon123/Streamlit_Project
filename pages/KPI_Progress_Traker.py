import streamlit as st
import datetime
import pandas as pd
import uuid
import plotly.graph_objects as go
from modules.kpi_dashboard import get_kpi_records, parse_kpi_text_to_dict
from modules.db import session, KPIDeadline, KPIDailyProgress, init_db

init_db()
st.set_page_config(page_title="KPI 실적 추적", layout="wide")
st.title("📈 KPI 실적 입력 및 추이 시각화")

records = get_kpi_records()
companies = list({r.company for r in records})
selected_company = st.selectbox("📌 회사 선택", companies)


def format_num(x):
    return f"{x:.2f}".rstrip("0").rstrip(".") if isinstance(x, float) else x

if selected_company:
    record = next(r for r in records if r.company == selected_company)
    parsed_kpis = parse_kpi_text_to_dict(record.kpi_text)
    kpi_names = [k["KPI 명"] for k in parsed_kpis]

    selected_kpi = st.selectbox("KPI 선택", kpi_names)

    meta = session.query(KPIDeadline).filter_by(company=selected_company, kpi_name=selected_kpi).first()
    if meta:
        measure = meta.measure
        target_value = meta.target
        deadline_date = meta.deadline
        progress = session.query(KPIDailyProgress)\
            .filter_by(company=selected_company, kpi_name=selected_kpi)\
            .order_by(KPIDailyProgress.date.asc()).all()

        cumulative = sum(p.actual for p in progress)
        today = datetime.date.today()
        achieved = cumulative >= meta.target and today <= meta.deadline

        st.markdown("### 🧭 KPI 정보")
        st.markdown(
            f"""
            <div style='font-size:18px;'>
                <b>측정 기준:</b> {meta.measure}<br>
                <b>전체 목표값:</b> {format_num(meta.target)}<br>
                <b>기한:</b> {meta.deadline.strftime("%Y-%m-%d")}<br>
                <b>달성 여부:</b> {"✅ 목표 달성" if achieved else "⏳ 진행 중"}
            </div>
            """, unsafe_allow_html=True
        )

        st.markdown("### 📆 일자별 실적 입력")
        date_input = st.date_input("날짜", datetime.date.today())
        daily_target = st.number_input("일일 목표값", value=0.0, step=0.1)
        actual = st.number_input("실적값", value=0.0, step=0.1, format="%.2f")

        if st.button("💾 입력 저장"):
            existing = session.query(KPIDailyProgress).filter_by(
                company=selected_company,
                kpi_name=selected_kpi,
                date=date_input
            ).first()

            if existing:
                existing.target = daily_target
                existing.actual = actual
                st.info("📌 기존 데이터를 수정했습니다.")
            else:
                new_record = KPIDailyProgress(
                    id=str(uuid.uuid4()),
                    company=selected_company,
                    kpi_name=selected_kpi,
                    date=date_input,
                    target=daily_target,
                    actual=actual
                )
                session.add(new_record)
                st.success("✅ 새 데이터를 저장했습니다.")
            session.commit()

        st.markdown("### 📊 KPI 실적 추이 시각화")
        progress = session.query(KPIDailyProgress)\
            .filter_by(company=selected_company, kpi_name=selected_kpi)\
            .order_by(KPIDailyProgress.date.asc()).all()

        if progress:
            df = pd.DataFrame([{
                "날짜": p.date,
                "일일 목표": p.target,
                "일일 실적": p.actual
            } for p in progress])

            df["날짜"] = pd.to_datetime(df["날짜"]).dt.date
            df["누적 실적"] = df["일일 실적"].cumsum()
            df["일일 달성률(%)"] = (df["일일 실적"] / df["일일 목표"]) * 100
            df["누적 달성률(%)"] = (df["누적 실적"] / meta.target) * 100 if meta and meta.target > 0 else 0
            df["전체 목표 잔여량"] = meta.target - df["누적 실적"]

            last_date = df["날짜"].max()
            plot_end_date = max(last_date, meta.deadline)
            plot_start_date = df["날짜"].min()

            goal_dates = pd.to_datetime(df["날짜"]).tolist()
            if pd.Timestamp(meta.deadline) > pd.Timestamp(goal_dates[-1]):
                goal_dates.append(pd.Timestamp(meta.deadline))
            goal_y = [meta.target] * len(goal_dates)

            fig = go.Figure()

            # 누적 실적
            fig.add_trace(go.Scatter(
                x=pd.to_datetime(df["날짜"]), y=df["누적 실적"],
                mode="lines+markers+text",
                name="누적 실적값",
                text=[f"일일 {d:.1f}%, 누적 {c:.1f}%" for d, c in zip(df["일일 달성률(%)"], df["누적 달성률(%)"])],
                textposition="top center"
            ))

            # 전체 목표값
            fig.add_trace(go.Scatter(
                x=goal_dates, y=goal_y,
                mode="lines",
                name="전체 목표값",
                line=dict(dash="dot", color="gray")
            ))

            # ✅ 목표 기한 표시를 범례에 포함
            fig.add_trace(go.Scatter(
                x=[meta.deadline, meta.deadline],
                y=[0, df["누적 실적"].max()],
                mode="lines",
                name="목표 기한",
                line=dict(color="red", dash="dash")
            ))

            fig.update_layout(
                title=f"{selected_kpi} 누적 실적 vs 전체 목표",
                xaxis_title="날짜",
                yaxis_title="누적 실적",
                xaxis=dict(range=[
                    pd.Timestamp(plot_start_date),
                    pd.Timestamp(plot_end_date)
                ]),
                legend=dict(
                    x=1.02,
                    y=0.5,
                    xanchor="left",
                    yanchor="middle",
                    orientation="v"
                )
            )
            st.plotly_chart(fig, use_container_width=True)

            ordered_columns = [
                "날짜", "일일 목표", "일일 실적", "전체 목표 잔여량", "누적 실적",
                "일일 달성률(%)", "누적 달성률(%)"
            ]

            def fmt(x):
                if isinstance(x, float):
                    return f"{x:.2f}".rstrip("0").rstrip(".") if x % 1 else f"{int(x)}"
                return x

            formatted_df = df[ordered_columns].copy()
            formatted_df = formatted_df.applymap(fmt)

            # 색상 비교
            numeric_df = df.drop(columns=["날짜", "전체 목표 잔여량"])
            color_map = pd.DataFrame("black", index=numeric_df.index, columns=numeric_df.columns)
            color_map[numeric_df > numeric_df.shift(1)] = "red"
            color_map[numeric_df < numeric_df.shift(1)] = "blue"
            color_map.insert(0, "날짜", "black")
            color_map.insert(0, "전체 목표 잔여량", "black")

            # 스타일 함수
            def color_cells(val, row_idx, col_name):
                return f"color: {color_map.loc[row_idx, col_name]}"

            def apply_row_style(row):
                return [color_cells(val, row.name, col) for col, val in row.items()]

            styled_df = df[ordered_columns].style.format(fmt).apply(apply_row_style, axis=1)

            st.markdown("### 📋 KPI 진행표")
            st.dataframe(styled_df)

    else:
        st.warning("⚠️ 해당 KPI에 대한 '측정 기준', '목표값', '달성 기한'이 설정되지 않았습니다. 직접 입력해주세요.")
        measure = st.text_input("측정 기준 입력")
        target_value = st.number_input("전체 목표값 입력", value=0.0)
        deadline_date = st.date_input("목표 기한 입력", value=datetime.date.today())

        if st.button("✅ KPI 정보 저장"):
            new_meta = KPIDeadline(
                company=selected_company,
                kpi_name=selected_kpi,
                measure=measure,
                target=target_value,
                deadline=deadline_date
            )
            session.add(new_meta)
            session.commit()
            st.success("KPI 메타 정보를 저장했습니다.")
            st.rerun()
from datetime import date
from sqlalchemy import select
from modules.db import session, KPIDeadline, KPIDailyProgress

def save_deadline_for_kpi(company, kpi_name, deadline, target, measure):
    record = session.query(KPIDeadline).filter_by(company=company, kpi_name=kpi_name).first()
    if record:
        record.deadline = deadline
        record.target = target
        record.measure = measure
    else:
        record = KPIDeadline(
            company=company,
            kpi_name=kpi_name,
            deadline=deadline,
            target=target,
            measure=measure
        )
        session.add(record)
    session.commit()

def check_deadline_alerts():
    today = date.today()
    alerts = []

    deadlines = session.query(KPIDeadline).all()
    for d in deadlines:
        if today > d.deadline:
            alerts.append(f"[{d.company}] '{d.kpi_name}' KPI는 기한({d.deadline})을 넘겼습니다.")

        # 실적 미달 여부 확인
        latest = (
            session.query(KPIDailyProgress)
            .filter_by(company=d.company, kpi_name=d.kpi_name)
            .order_by(KPIDailyProgress.date.desc())
            .first()
        )
        if latest and latest.actual < latest.target and today >= d.deadline:
            alerts.append(f"[{d.company}] '{d.kpi_name}' KPI는 목표 미달성 상태입니다.")

    return alerts
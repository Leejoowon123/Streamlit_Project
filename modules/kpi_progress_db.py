from modules.db import session, KPIDailyProgress
import uuid

def save_kpi_daily_progress(company, kpi_name, date, target, actual):
    record = KPIDailyProgress(
        id=str(uuid.uuid4()),
        company=company,
        kpi_name=kpi_name,
        date=date,
        target=target,
        actual=actual
    )
    session.add(record)
    session.commit()

def get_kpi_progress(company, kpi_name):
    result = (
        session.query(KPIDailyProgress)
        .filter_by(company=company, kpi_name=kpi_name)
        .order_by(KPIDailyProgress.date.asc())
        .all()
    )
    return [
        {"date": r.date, "target": r.target, "actual": r.actual}
        for r in result
    ]

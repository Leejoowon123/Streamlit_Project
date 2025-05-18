import sys
import os
import re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from modules.db import KPIRecord, SessionLocal

def get_kpi_records():
    db = SessionLocal()
    records = db.query(KPIRecord).order_by(KPIRecord.timestamp.desc()).all()
    db.close()
    return records

def parse_kpi_text_to_dict(kpi_text):
    pattern = r"\d+\.\s+\*\*(.*?)\*\*\s*-\s+\*\*설명:\*\*\s*(.*?)\s*-\s+\*\*측정 기준:\*\*\s*(.*?)\s*-\s+\*\*기대 효과:\*\*\s*(.*?)(?=\n\d+\.|\Z)"
    matches = re.findall(pattern, kpi_text, flags=re.DOTALL)

    kpi_list = []
    for title, description, measure, impact in matches:
        kpi_list.append({
            "KPI 명": title.strip(),
            "설명": description.strip(),
            "측정 기준": measure.strip(),
            "기대 효과": impact.strip()
        })

    return kpi_list
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Date, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.abspath(os.path.join(BASE_DIR, "../output"))
DB_PATH = os.path.join(PDF_DIR, "analysis_history.db")

# SQLAlchemy 설정
engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, index=True)
    section = Column(String)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    pdf_path = Column(String)
    summary = Column(Text, default="")
    keywords = Column(String, default="")

class KPIRecord(Base):
    __tablename__ = "kpi_records"
    id = Column(Integer, primary_key=True)
    company = Column(String)
    timestamp = Column(DateTime, default=datetime.now)
    pdf_path = Column(String)
    kpi_text = Column(Text)

# ✅ KPI 기한 테이블
class KPIDeadline(Base):
    __tablename__ = "kpi_deadlines"
    company = Column(String, primary_key=True)
    kpi_name = Column(String, primary_key=True)
    deadline = Column(Date)
    target = Column(Float)
    measure = Column(String) 

# ✅ KPI 실적 추이 테이블
class KPIDailyProgress(Base):
    __tablename__ = "kpi_daily_progress"
    id = Column(String, primary_key=True)
    company = Column(String)
    kpi_name = Column(String)
    date = Column(Date)
    target = Column(Float)
    actual = Column(Float)

Base.metadata.create_all(bind=engine)

# 테이블 생성
def init_db():
    Base.metadata.create_all(bind=engine)

# 저장
def save_result_to_db(company_name, result_dict, pdf_path):
    session = SessionLocal()
    file_name = os.path.basename(pdf_path)
    summary = result_dict.pop("__요약__", "")
    keywords = result_dict.pop("__키워드__", "")

    for section, content in result_dict.items():
        entry = AnalysisResult(
            company_name=company_name,
            section=section,
            content=content,
            pdf_path=file_name,
            summary=summary,
            keywords=keywords
        )
        session.add(entry)
    session.commit()
    session.close()

def get_grouped_results():
    session = SessionLocal()
    rows = session.query(
        AnalysisResult.company_name,
        AnalysisResult.created_at,
        AnalysisResult.pdf_path,
        AnalysisResult.summary,
        AnalysisResult.keywords
    ).distinct().order_by(AnalysisResult.created_at.desc()).all()

    grouped = []
    for row in rows:
        sections = session.query(AnalysisResult.section)\
            .filter_by(company_name=row.company_name, created_at=row.created_at)\
            .all()
        section_list = ", ".join(sorted(set([s.section for s in sections])))

        abs_pdf_path = os.path.join(PDF_DIR, row.pdf_path)

        grouped.append({
            "조회일": row.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "회사명": row.company_name,
            "분석 항목": section_list,
            "PDF 파일명": row.pdf_path,
            "PDF 경로": abs_pdf_path,
            "요약": row.summary or "",
            "키워드": row.keywords or ""
        })
    session.close()
    return grouped

def get_analysis_by_company(company_name):
    session = SessionLocal()
    all_records = session.query(KPIRecord).order_by(KPIRecord.timestamp.desc()).all()
    for record in all_records:
        if record.company == company_name:
            return {
                "회사명": record.company,
                "조회일": record.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "PDF 경로": record.pdf_path,
                "분석결과": record.kpi_text,
            }
    return None

# KPI 저장 함수
def save_kpi_analysis_result(company_name, kpi_text, pdf_path):
    session = SessionLocal()
    entry = KPIRecord(
        company=company_name,
        pdf_path=pdf_path,
        kpi_text=kpi_text
    )
    session.add(entry)
    session.commit()
    session.close()

# KPI 결과 조회 함수
def get_all_kpi_results():
    session = SessionLocal()
    results = session.query(KPIRecord).order_by(KPIRecord.timestamp.desc()).all()
    session.close()
    return results
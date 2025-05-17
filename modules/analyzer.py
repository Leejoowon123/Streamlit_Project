from fpdf import FPDF
import os
import re
import warnings
from .prompts_loader import load_prompt
from .gemini_api import call_gemini
from markdown2 import markdown
from datetime import datetime
from bs4 import BeautifulSoup

warnings.filterwarnings("ignore", message="cmap value too big/small")

STAGES = [
    ("Five Forces 분석", "five_forces"),
    ("가치사슬 분석", "value_chain"),
    ("3C 분석", "three_c"),
    ("PEST 분석", "pest"),
    ("SWOT 분석", "swot"),
    ("STP 분석", "stp"),
    ("4P 마케팅 전략", "four_p")
]

def build_prompt_with_context(template_name, company_name, context=[]):
    prompt = load_prompt(template_name, company_name)
    context_text = "\n\n".join([f"[이전 분석결과]\n{c}" for c in context])
    return context_text + "\n\n" + prompt

def extract_section(text, section_name):
    pattern = rf"{section_name}\s*[:\-\n](.*?)\n\s*[A-Z가-힣]"
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).strip() if match else ""

def run_full_analysis(company_name, selected_stages):
    result = {}
    for display_name, file_key in selected_stages:
        if display_name == "3C 분석":
            prompt = build_prompt_with_context(file_key, company_name, [
                result.get("Five Forces 분석", ""), result.get("가치사슬 분석", "")
            ])
        elif display_name == "SWOT 분석":
            prompt = build_prompt_with_context(file_key, company_name, [
                result.get("3C 분석", ""), result.get("PEST 분석", "")
            ])
        elif display_name == "STP 분석":
            customer_info = extract_section(result.get("3C 분석", ""), "고객")
            competitor_info = extract_section(result.get("3C 분석", ""), "경쟁사")
            prompt = build_prompt_with_context(file_key, company_name, [
                result.get("SWOT 분석", ""), f"고객 정보: {customer_info}", f"경쟁사 정보: {competitor_info}"
            ])
        elif display_name == "4P 마케팅 전략":
            prompt = build_prompt_with_context(file_key, company_name, [
                result.get("STP 분석", "")
            ])
        else:
            prompt = load_prompt(file_key, company_name)

        try:
            answer = call_gemini(prompt)
            if not answer.strip():
                answer = f"{display_name}에 대한 Gemini 응답이 비어 있습니다."
        except Exception as e:
            answer = f"{display_name} 호출 중 오류 발생: {e}"

        result[display_name] = answer
        
    try:
        full_analysis_text = "\n\n".join(
            [v for k, v in result.items() if not k.startswith("__")]
        )

        summarizer_prompt = load_prompt("summarizer", company_name)
        final_prompt = summarizer_prompt.replace("{{분석내용}}", full_analysis_text)

        summary_response = call_gemini(final_prompt)

        summary_lines = summary_response.strip().splitlines()
        summary_text = next((line for line in summary_lines if line.strip()), "")
        keyword_line = next((line for line in summary_lines if "키워드" in line), "")
        keywords = keyword_line.replace("키워드:", "").strip() if "키워드:" in keyword_line else ""

        result["__요약__"] = summary_text
        result["__키워드__"] = keywords
    except Exception as e:
        result["__요약__"] = f"요약 실패: {e}"
        result["__키워드__"] = "키워드 없음"

    return result

def break_long_words(text, max_len=50):
    return re.sub(r'(\S{' + str(max_len) + r',})', lambda m: '\n'.join([m.group(0)[i:i+max_len] for i in range(0, len(m.group(0)), max_len)]), text)

def generate_pdf_report(company_name, analysis_result, file_path="report.pdf"):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # 폰트 등록
    pdf.add_font("NanumGothic", "", os.path.join("fonts", "NanumGothic.ttf"), uni=True)
    pdf.add_font("NanumGothic", "B", os.path.join("fonts", "NanumGothicBold.ttf"), uni=True)

    # 제목
    pdf.set_font("NanumGothic", "B", 16)
    pdf.cell(0, 10, f"{company_name} 전략 분석 리포트", ln=True, align='C')

    # 날짜
    pdf.set_font("NanumGothic", "", 11)
    date_str = datetime.now().strftime("분석일: %Y년 %m월 %d일")
    pdf.cell(0, 10, date_str, ln=True, align='R')
    pdf.ln(5)

    # 요약 및 키워드 먼저 출력
    summary = analysis_result.get("__요약__")
    keywords = analysis_result.get("__키워드__")

    if summary:
        pdf.set_font("NanumGothic", "B", 13)
        pdf.cell(0, 10, "요약", ln=True)
        pdf.set_font("NanumGothic", "", 11)
        pdf.multi_cell(0, 8, summary)
        pdf.ln(3)

    if keywords:
        pdf.set_font("NanumGothic", "B", 13)
        pdf.cell(0, 10, "핵심 키워드", ln=True)
        pdf.set_font("NanumGothic", "", 11)
        pdf.multi_cell(0, 8, keywords)
        pdf.ln(5)

    # 목차
    pdf.set_font("NanumGothic", "B", 12)
    pdf.cell(0, 10, "목차", ln=True)
    pdf.set_font("NanumGothic", "", 11)
    for section in analysis_result:
        pdf.cell(0, 8, f"- {section}", ln=True)
    pdf.ln(10)

    # 본문
    for section, content in analysis_result.items():
        pdf.set_font("NanumGothic", "B", 12)
        pdf.multi_cell(0, 10, section)
        pdf.ln(2)

        # markdown → html → text
        html = markdown(content)
        soup = BeautifulSoup(html, "html.parser")

        pdf.set_font("NanumGothic", "", 11)

        for element in soup.find_all(["p", "li"]):
            try:
                raw_text = element.get_text(strip=True)
                safe_text = break_long_words(raw_text)
                pdf.multi_cell(0, 8, safe_text)
                pdf.ln(1)
            except Exception as e:
                pdf.set_text_color(255, 0, 0)
                pdf.multi_cell(0, 8, f"[렌더링 실패: {e}]")
                pdf.set_text_color(0, 0, 0)

        pdf.ln(5)

    pdf.output(file_path)
    return file_path

def generate_pdf_report_with_structured_kpi(company_name, analysis_result, file_path="report.pdf"):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # 폰트 등록
    pdf.add_font("NanumGothic", "", os.path.join("fonts", "NanumGothic.ttf"), uni=True)
    pdf.add_font("NanumGothic", "B", os.path.join("fonts", "NanumGothicBold.ttf"), uni=True)

    # 제목
    pdf.set_font("NanumGothic", "B", 16)
    pdf.cell(0, 10, f"{company_name} 전략 KPI 분석 리포트", ln=True, align='C')

    # 날짜
    pdf.set_font("NanumGothic", "", 11)
    date_str = datetime.now().strftime("분석일: %Y년 %m월 %d일")
    pdf.cell(0, 10, date_str, ln=True, align='R')
    pdf.ln(5)

    # 목차
    pdf.set_font("NanumGothic", "B", 12)
    pdf.cell(0, 10, "목차", ln=True)
    pdf.set_font("NanumGothic", "", 11)
    for section in analysis_result:
        pdf.cell(0, 8, f"- {section}", ln=True)
    pdf.ln(10)

    # 본문
    for section, content in analysis_result.items():
        pdf.set_font("NanumGothic", "B", 12)
        pdf.multi_cell(0, 10, break_long_words(section))
        pdf.ln(2)

        html = markdown(str(content))
        soup = BeautifulSoup(html, "html.parser")
        pdf.set_font("NanumGothic", "", 11)

        for element in soup.find_all(["p", "li"]):
            try:
                raw_text = element.get_text(strip=True)
                safe_text = break_long_words(raw_text)
                pdf.multi_cell(0, 8, safe_text)
                pdf.ln(1)
            except Exception as e:
                pdf.set_text_color(255, 0, 0)
                pdf.multi_cell(0, 8, f"[렌더링 실패: {e}]")
                pdf.set_text_color(0, 0, 0)

        pdf.ln(5)

    pdf.output(file_path)
    return file_path
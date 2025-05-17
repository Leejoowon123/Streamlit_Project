import os
import requests
import streamlit as st
from dotenv import load_dotenv
from modules.prompts_loader import load_prompt

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = os.getenv("GEMINI_URL")

def get_competitor_comparison_table(company_name):
    prompt = load_prompt("industry", company_name)

    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    try:
        response = requests.post(f"{GEMINI_URL}?key={GEMINI_API_KEY}", headers=headers, json=data)
        result = response.json()

        if "candidates" in result:
            return result["candidates"][0]["content"]["parts"][0]["text"]
        else:
            st.error("Gemini 응답 오류 발생 (산업 분석)")
            print("[Gemini 응답 - 산업 분석]", result)
            return "산업 분석에 실패했습니다."
    except Exception as e:
        st.error("산업 분석 요청 중 오류 발생")
        return f"[산업 분석 실패: {company_name}]\n{str(e)}"
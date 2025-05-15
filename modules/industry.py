import os
import requests
import traceback
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = os.getenv("GEMINI_URL")

@st.cache_data
def analyze_industry(company_name):
    try:
        with open("prompts/industry.txt", "r", encoding="utf-8") as f:
            template = f.read()

        prompt = template.replace("{{회사명}}", company_name)

        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{"parts": [{"text": prompt}]}]
        }

        response = requests.post(
            f"{GEMINI_URL}?key={GEMINI_API_KEY}", headers=headers, json=data)
        result = response.json()

        if "error" in result:
            error = result["error"]
            if error.get("code") == 429:
                return "❌ [Gemini 쿼터 초과] 무료 플랜의 사용 한도를 초과했습니다.\n잠시 후 다시 시도하거나 유료 플랜으로 전환해주세요."
            return f"❌ 오류: {error.get('message')}"

        text = result["candidates"][0]["content"]["parts"][0]["text"]
        return text

    except Exception as e:
        print(f"❌ [분석 실패] {e}")
        return f"❌ 분석 실패: {e}"
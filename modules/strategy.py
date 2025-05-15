import os
import requests
import traceback
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = os.getenv("GEMINI_URL")

def load_strategy_prompt():
    try:
        with open("prompts/strategy.txt", "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print("❌ [프롬프트 로딩 오류 - strategy.txt]")
        traceback.print_exc()
        return f"[❌ 프롬프트 파일 로딩 실패: {str(e)}]"

@st.cache_data
def suggest_strategy(company_name: str):
    prompt_template = load_strategy_prompt()
    if prompt_template.startswith("[❌"):
        return prompt_template

    prompt = prompt_template.replace("{{회사명}}", company_name)

    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        response = requests.post(f"{GEMINI_URL}?key={GEMINI_API_KEY}", headers=headers, json=data)
        result = response.json()

        if "candidates" in result and result["candidates"]:
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            return text
        else:
            return f"[⚠️ Gemini 응답 오류 - 전략 제안 실패]\n{prompt}"
    except Exception as e:
        print("❌ [전략 제안 예외 발생]")
        traceback.print_exc()
        return f"[❌ 전략 제안 예외 발생: {str(e)}]\n{prompt}"

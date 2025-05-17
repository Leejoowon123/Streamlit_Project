import os
import requests
from dotenv import load_dotenv

def call_gemini(prompt: str) -> str:
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    url = os.getenv("GEMINI_URL")
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    try:
        response = requests.post(f"{url}?key={api_key}", headers=headers, json=payload)
        data = response.json()

        if response.status_code != 200:
            return f"Gemini 오류: {data.get('error', {}).get('message', '알 수 없는 오류')}"

        return data['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"요청 실패: {str(e)}"
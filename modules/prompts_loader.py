import os

def load_prompt(stage_name, company_name):
    base_path = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(base_path, "..", "prompts", f"{stage_name}.txt")

    if not os.path.exists(prompt_path):
        return f"{stage_name}.txt 프롬프트 파일이 존재하지 않습니다."

    with open(prompt_path, "r", encoding="utf-8") as f:
        template = f.read()

    return template.replace("{company}", company_name)

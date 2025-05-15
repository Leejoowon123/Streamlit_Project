import os

def load_prompt(stage_name, company_name):
    """
    prompts/ 폴더 내에서 {stage_name}.txt 파일을 읽고, 
    {company} 변수에 사용자 입력 회사명을 삽입하여 반환
    """
    prompt_path = os.path.join("prompts", f"{stage_name}.txt")

    if not os.path.exists(prompt_path):
        return f"⚠️ {stage_name}.txt 프롬프트 파일이 존재하지 않습니다."

    with open(prompt_path, "r", encoding="utf-8") as f:
        template = f.read()

    return template.replace("{company}", company_name)

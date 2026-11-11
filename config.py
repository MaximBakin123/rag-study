import os 
from dotenv import load_dotenv

load_dotenv()
create_key = os.getenv("key")

def ai_chat_rules(file_path: str) -> str: 
    if os.path.exists(file_path): 
        with open(file_path, "r", encoding="utf-8") as f: 
            return f.strip()

    else: 
        print("--ошибка, файла 'rules.md' не существует--")

saving_file = ai_chat_rules("rules.md")



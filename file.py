import asyncio
import json
import os
from typing import Literal

from dotenv import load_dotenv
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole
from pydantic import BaseModel, Field, ValidationError
import aiosqlite 

load_dotenv()
create_key = os.getenv("key")

def load_file(file_path: str = "rules.txt") -> str: 
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    else: 
        print("⚠️ Возникла ошибка при обработке файла (файл не найден).")
        return "База знаний пуста."

FILE_CONTENT = load_file("rules.txt")

PROMT = f"""Твоя задача — анализировать сообщения пользователя, используя базу знаний:
{FILE_CONTENT}

ПРАВИЛА ВЫБОРА ФУНКЦИЙ:
1) Если пользователь написал бутсы, которые хочет купить, но ИХ НЕТ в наличии (смотри базу данных выше) -> вызывай функцию predzakaz_function.
2) Если бутсы ЕСТЬ в наличии -> вызывай функцию nalichie_function.
3) Если человек спамит, присылает рекламу или пишет бессмысленный текст не по теме -> вызывай функцию spam_function.
4) Если пользователь просит помочь выбрать бутсы под его критерии -> вызывай функцию suppote_function.
"""

class Predzakaz(BaseModel): 
    text: str = Field(description="Название бутс, которых нет в наличии, для оформления предзаказа")

class Nalichie(BaseModel): 
    text: str = Field(description="Название бутс, которые есть в наличии, для оформления покупки")

class Spam(BaseModel): 
    text: str = Field(description="Текст спама или рекламы")

class Suppote(BaseModel): 
    text: str = Field(description="Критерии пользователя для подбора бутс")

# Изменили обычные функции на асинхронные, чтобы их можно было единообразно вызывать с await
async def predzakaz_function(text: str) -> dict: 
    print(f"\n[ОТЛИЧНО] Оформляем предзаказ на: {text}")
    return {"status": "predzakaz", "message": f"Бутсы {text} успешно добавлены в предзаказ."}

async def nalichie_function(text: str) -> dict: 
    print(f"\n[ОТЛИЧНО] Бутсы {text} есть в наличии! Перенаправляем на оплату.")
    return {"status": "nalichie", "message": f"Бутсы {text} забронированы для покупки."}

async def spam_function(text: str) -> dict: 
    print(f"\n[СПАМ] Обнаружено нежелательное сообщение: {text}")
    return {"status": "spam", "message": "Ваше сообщение заблокировано системой модерации."}

async def suppote_function(text: str) -> dict: 
    print(f"\n[ПОДДЕРЖКА] ИИ подбирает бутсы по запросу: {text}")
    async with GigaChat(credentials=create_key, scope="GIGACHAT_API_PERS", verify_ssl_certs=False) as giga: 
        response = await giga.achat(Chat(
            model="GigaChat", 
            messages=[Messages(role=MessagesRole.USER, content=f"Помоги выбрать бутсы на основе запроса: {text}")], 
            temperature=0.6
        ))
        vuvod = response.choices[0].message.content
    return {"status": "suppote", "otvet": vuvod}

# Исправили имя ключа со 'spam' на 'spam_function' для соответствия
TOOLS = {
    "predzakaz_function": predzakaz_function, 
    "nalichie_function": nalichie_function, 
    "spam_function": spam_function, 
    "suppote_function": suppote_function
}

FUNCTION = [
    {"name": "predzakaz_function", "description": "Если человек хочет заказать, но бутс нет в наличии", "parameters": Predzakaz.model_json_schema()},
    {"name": "nalichie_function", "description": "Если человек хочет заказать, и бутсы есть в наличии", "parameters": Nalichie.model_json_schema()},
    {"name": "spam_function", "description": "Если человек пишет спам, рекламу или флуд", "parameters": Spam.model_json_schema()},
    {"name": "suppote_function", "description": "Если человеку надо помочь выбрать бутсы по параметрам", "parameters": Suppote.model_json_schema()}
]

async def ai(ad: str):
    messages = [
        Messages(role=MessagesRole.SYSTEM, content=PROMT),
        Messages(role=MessagesRole.USER, content=ad)  # Исправлено: роль USER вместо SYSTEM
    ]
    
    async with GigaChat(credentials=create_key, scope="GIGACHAT_API_PERS", verify_ssl_certs=False) as giga: 
        # Исправлено: добавлен await, метод achat, и параметр functions
        remore = await giga.achat(Chat(
            model="GigaChat-2", 
            messages=messages,
            function_call="auto", 
            functions=FUNCTION, 
            temperature=0.2
        )) 

        msg = remore.choices[0].message

        # Исправлено: убрали вызов скобками () у свойства function_call
        if not msg.function_call: 
            print(f"\n🤖 Ответ ИИ: {msg.content}")
            return msg.content

        name = msg.function_call.name
        arguments = msg.function_call.arguments

        if isinstance(arguments, str): 
            arg = json.loads(arguments)
        else:
            arg = arguments

        print(f"\n🤖 ИИ решил вызвать функцию [{name}] с аргументами: {arg}")

        if name in TOOLS:
            # Исправлено: корректный вызов функции из словаря с распаковкой аргументов через await
            result = await TOOLS[name](**arg)
        else: 
            result = {"status": "none", "content": "Такой функции нет, перепроверь и выбери правильную"}

        messages.append(msg)
        messages.append(
            Messages(
                role=MessagesRole.FUNCTION,
                name=name,  
                content=json.dumps(result, ensure_ascii=False)
            )
        )
        
        # Делаем финальный шаг: отдаем результат работы функции обратно ИИ, чтобы он ответил пользователю
        final_response = await giga.achat(Chat(
            model="GigaChat-2",
            messages=messages,
            temperature=0.2
        ))
        print(f"\n🤖 Итоговый ответ для клиента: {final_response.choices[0].message.content}")


async def main() -> str: 
    # Исправлено: функция теперь возвращает строку, чтобы передать её в ai()
    text = input("Введите, какие бутсы хотите купить (или попросите ИИ помочь с выбором): ")
    return text

if __name__ == "__main__":
    # Запускаем main() через await внутри asyncio.run()
    user_input = asyncio.run(main())
    asyncio.run(ai(user_input))

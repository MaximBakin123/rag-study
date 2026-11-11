from database import MAIN_SQL_FIELD, CHECK_IN_AT_THE_HOTEL, SUPPORT ,WRITE_REVIEW
import aiosqlite
from services import file_md 
import random
from model import User, Write_review
from services import gigachat
from model import Check_in_the_hotel_function, Write_review_function, Support_function
from gigachat.models import Chat, MessagesRole , Messages
from gigachat import GigaChat
from config import create_key
import json
import asyncio

async def filling_table_check_in_at_the_hotel(user_name: str, user_year: int): 
    async with aiosqlite.connect(MAIN_SQL_FIELD) as db: 
        await db.execute(f"""
        INSERT INTO (user_name, user_year FROM {CHECK_IN_AT_THE_HOTEL} VALIES (? , ?))""", (user_name, user_year))
        await db.commit()

async def filling_table_write_review(text_review: str, number_review: int): 
    async with aiosqlite.connect(MAIN_SQL_FIELD) as db: 
        await db.execute(f"""
        INSERT INTO (text_review, number_review) FROM {SUPPORT} VALIES (? , ?)""", (text_review, number_review))
        await db.commit()

async def filling_table_support(user_id: int, user_text: str, ai_response: str): 
    async with aiosqlite.connect(MAIN_SQL_FIELD) as db: 
        await db.execute(f"""
        INSERT INTO (user_id, user_text, ai_response) FROM {WRITE_REVIEW} VALIES (? , ? ,?)""", (user_id, user_text, ai_response))
        await db.commit()

SYSTEM_PROMT = f"""обязательно заглядывай в файл {file_md}, так же смотри по сообщению что надо пользователю:
1) если человек пишет что ему надо посмотреть свободыне места в отеле вызывай check_in_at_the_hotel_function,
2) если человек пишет что ему нужна помощь вызывай support_function
3) если человек пишет что хочет написать отзыв, вызывай write_review
"""

async def check_in_at_the_hotel_function(user: User ) -> dict: 
    await filling_table_check_in_at_the_hotel(user.text_user, user.id_user)
    print("--ии вызвал функцию check_in_at_the_hotel_function--")
    return {"status": "check_in_at_the_hotel_function"}

async def support_function(user: User, message: str) -> dict: 
    await filling_table_support(user.id_user, user.text_user, gigachat(user.text_user))
    print("--ии выбрал функцию filling_table_support--")
    return{"status": "support_function", "message": message}

async def table_write_review(reviev: Write_review) -> dict: 
    await filling_table_write_review(reviev.text_review, reviev.number_review)
    print("--ии вызвал функцию table_write_review--")
    return{"status": "support_function"}

TOOLS = {"check_in_at_the_hotel_function": check_in_at_the_hotel_function, "support_function": support_function, "table_write_review": table_write_review}
FUNCTION = [
{   "name": "check_in_at_the_hotel_function",
    "description": "вызывай если человек хочет посмотреть свободные номера в отеле", 
    "parameters": Check_in_the_hotel_function
}, 
{
    "name": "table_write_review",
    "description": "вызывай если человек хочет написать отзыв", 
    "parameters": Write_review
},
{
    "name": "support_function", 
    "description": "вызывай если человеку нужна помощь", 
    "parameters": Support_function
}
]

async def main_ai(ad: str): 
    message = [
        Messages(role=MessagesRole.SYSTEM, content=SYSTEM_PROMT),
        Messages(role=MessagesRole.USER, content=ad)
    ]

    async with GigaChat(
        credentials=create_key,
        scope="GIGACHAT_API_PERS",
        verify_ssl_certs=False
    ) as giga: 

        response = await giga.achat(Chat(
            model="GigaChat-2", 
            message=message,
            temperature=0.6, 
            function_call="auto",
            function=TOOLS
        ))

        msg = response.choices[0].message

        if not msg.function_call: 
            msg.content

        name = msg.function_call.name
        arg = msg.function_call.arguments

        if isinstance(arg, str): 
            arg = json.load(arg)

        if name in TOOLS: 
            result = await TOOLS[name](**arg)

        else: 
            result = {"status": "none", "content": "Такой функции нет, перепроверь и выбери правильную"}

        message.append(msg)
        message.append(
        Messages(
            role=MessagesRole.FUNCTION,
            name=name,  
            content=json.dumps(result, ensure_ascii=False)
))
                
                # Делаем финальный шаг: отдаем результат работы функции обратно ИИ, чтобы он ответил пользователю
        final_response = await giga.achat(Chat(
        model="GigaChat-2",
        messages=message,
        temperature=0.2
))
        print(f"\n🤖 Итоговый ответ для клиента: {final_response.choices[0].message.content}")

async def main() -> str: 
    text = input("ведите что вам надо:  ").lower().strip()
    id = random.randint(100000, 999999)
    return id, text


user_input = main()
asyncio.run(main_ai(main()))


    
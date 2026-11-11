import aiosqlite

MAIN_SQL_FIELD= "MAIN_SQL_FIELD"
CHECK_IN_AT_THE_HOTEL = "CHECK-IN_AT_THE_HOTEL"
WRITE_REVIEW = "WRITE_REVIEW"
SUPPORT = "SUPPORT"

async def create_table():
    async with aiosqlite.connect(MAIN_SQL_FIELD) as db: 
        await db.execute(F"""
        CREATE TABLE IF NOT EXISTS {CHECK_IN_AT_THE_HOTEL}(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name_user TEXT, 
        year_user INTEGER
        )
""")
        await db.execute(f"""
        CREATE TABLE IF NOT EXISTS {WRITE_REVIEW}(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text_review TEXT, 
        number_review INTEGER
        )
""")
        await db.execute(f"""
        CREATE TABLE IF NOT EXISTS {SUPPORT}(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        text_user TEXT,
        ai_response TEXT
        )
""")
        await db.commit()


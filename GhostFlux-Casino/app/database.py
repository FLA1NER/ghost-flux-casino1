import aiosqlite
import json
import os

DB_PATH = os.getenv('DATABASE_URL', 'database.db')

async def init_db():
    """Инициализация базы данных"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                balance INTEGER DEFAULT 0,
                inventory TEXT DEFAULT '[]',
                last_bonus_claim INTEGER DEFAULT 0
            )
        ''')
        await db.commit()

async def get_user(user_id: int):
    """Получить пользователя по ID"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return {
                    'user_id': row[0],
                    'username': row[1],
                    'balance': row[2],
                    'inventory': json.loads(row[3]),
                    'last_bonus_claim': row[4]
                }
            return None

async def create_user(user_id: int, username: str = None):
    """Создать нового пользователя"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)',
            (user_id, username)
        )
        await db.commit()

async def update_balance(user_id: int, amount: int):
    """Обновить баланс пользователя"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'UPDATE users SET balance = balance + ? WHERE user_id = ?',
            (amount, user_id)
        )
        await db.commit()

async def update_inventory(user_id: int, inventory: list):
    """Обновить инвентарь пользователя"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'UPDATE users SET inventory = ? WHERE user_id = ?',
            (json.dumps(inventory), user_id)
        )
        await db.commit()

async def update_bonus_claim(user_id: int, timestamp: int):
    """Обновить время последнего бонуса"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'UPDATE users SET last_bonus_claim = ? WHERE user_id = ?',
            (timestamp, user_id)
        )
        await db.commit()
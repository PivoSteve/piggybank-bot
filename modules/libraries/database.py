import sqlite3

def get_connection() -> callable:
    return sqlite3.connect('database/piggy_bank.db')

def init_db() -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS savings (
        user_id INTEGER PRIMARY KEY,
        currency TEXT NULL,
        amount REAL DEFAULT 0,
        goal REAL NULL,
        achived BOOLEAN DEFAULT FALSE
    )
    ''')
    conn.commit()
    conn.close()

def get_user(user_id) -> tuple:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM savings WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result if result else (user_id, None, 0, None)
    
def update_currency(user_id, currency) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE savings SET currency = ? WHERE user_id = ?', (currency, user_id))
    if cursor.rowcount == 0:
        cursor.execute('INSERT INTO savings (user_id, currency) VALUES (?, ?)', (user_id, currency))
    conn.commit()
    conn.close()

def update_goal(user_id, goal) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE savings SET goal = ? WHERE user_id = ?', (goal, user_id))
    if cursor.rowcount == 0:
        cursor.execute('INSERT INTO savings (user_id, goal) VALUES (?, ?)', (user_id, goal))
    conn.commit()
    conn.close()

def get_balance(user_id) -> float:
    user = get_user(user_id)
    return user[2]

def update_balance(user_id, amount, decrease=False) -> str:
    current_balance = get_balance(user_id)
    if decrease and current_balance < amount:
        return f'❌ Недостаточно средств. Текущий баланс: {current_balance:.2f} {user[1]}'
    new_balance = current_balance - amount if decrease else current_balance + amount
    conn = get_connection()
    cursor = conn.cursor()
    if new_balance >= get_user(user_id)[3]:
        cursor.execute('UPDATE savings SET amount = ? WHERE user_id = ?', (new_balance, user_id))
        cursor.execute('UPDATE savings SET achived = ? WHERE user_id = ?', (True, user_id))
        conn.commit()
        conn.close()
        return '🥳 Твоя цель накопления достигнута! Поздравляю!\nЧтобы начать новую копилку напишите /reset'
    else: 
        cursor.execute('UPDATE savings SET amount = ? WHERE user_id = ?', (new_balance, user_id))
        if cursor.rowcount == 0:
            cursor.execute('INSERT INTO savings (user_id, currency, amount) VALUES (?, ?, ?)', (user_id, 'USD', new_balance))
        conn.commit()
        conn.close()
    updated_user = get_user(user_id)
    if decrease:
        return f'✔ Отлично!\n{amount:.2f} {updated_user[1]} было вычтено из ваших сбережений!'
    else:
        return f'✔ Отлично!\n{amount:.2f} {updated_user[1]} добавлено к вашим сбережениям!'

def reset(user_id) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE savings SET currency = NULL, amount = 0, goal = NULL, achived = FALSE WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()
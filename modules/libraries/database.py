import sqlite3

def get_connection():
    return sqlite3.connect('piggy_bank.db')

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS savings (
        user_id INTEGER PRIMARY KEY,
        currency TEXT NULL,
        amount REAL DEFAULT 0,
        goal REAL NULL
    )
    ''')
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM savings WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result if result else (user_id, None, 0, None)
    
def update_currency(user_id, currency):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE savings SET currency = ? WHERE user_id = ?', (currency, user_id))
    if cursor.rowcount == 0:
        cursor.execute('INSERT INTO savings (user_id, currency) VALUES (?, ?)', (user_id, currency))
    conn.commit()
    conn.close()

def update_goal(user_id, goal):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE savings SET goal = ? WHERE user_id = ?', (goal, user_id))
    if cursor.rowcount == 0:
        cursor.execute('INSERT INTO savings (user_id, goal) VALUES (?, ?)', (user_id, goal))
    conn.commit()
    conn.close()


def get_balance(user_id):
    user = get_user(user_id)
    return user[2]

def update_balance(user_id, amount):
    conn = get_connection()
    cursor = conn.cursor()
    user = get_user(user_id)
    new_balance = user[2] + amount
    cursor.execute('UPDATE savings SET amount = ? WHERE user_id = ?',
                   (new_balance, user_id))
    if cursor.rowcount == 0:
        cursor.execute('INSERT INTO savings (user_id, currency, amount) VALUES (?, ?, ?)',
                       (user_id, 'USD', amount))
    conn.commit()
    conn.close()
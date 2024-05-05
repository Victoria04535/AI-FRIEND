import logging
import sqlite3


def create_database():
    try:
        con = sqlite3.connect("DB_FILE.db", check_same_thread=False)
        cur = con.cursor()
        query='''CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        text_message TEXT,
        role TEXT,
        used_tokens INTEGER,
        tts_symbols INTEGER,
        stt_blocks INTEGER); '''
        cur.execute(query)
        con.close()
        logging.info("База данных создана")
    except Exception as e:
        logging.error(e)

def add_message(our_user_id, text, role, used_tokens, symbols, blocks):
    try:
        con = sqlite3.connect("DB_FILE.db", check_same_thread=False)
        cur = con.cursor()
        query='''INSERT INTO messages (
            user_id, 
            text_message, 
            role,
            used_tokens, 
            tts_symbols, 
            stt_blocks) 
            VALUES(?, ?, ?, ?, ?, ?);'''
        values = (our_user_id, text, role, used_tokens, symbols, blocks)
        cur.execute(query, values)
        con.commit()
        con.close()
        logging.info(f"Сообщение пользователя {our_user_id} добавлено в базу данных")
    except Exception as e:
        logging.error(e)

def count_users(our_user_id):
    try:
        with sqlite3.connect("DB_FILE.db") as conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT COUNT(DISTINCT user_id) FROM messages WHERE user_id <> ?''', (our_user_id,))
            count = cursor.fetchone()[0]
            return count
    except Exception as e:
        logging.error(e)


def select_n_last_messages(our_user_id, n_last_messages=4):
    try:
        messages = []
        used_tokens = 0
        with sqlite3.connect("DB_FILE.db") as conn:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT text_message, role, used_tokens FROM messages WHERE user_id=? AND text_message <> ? ORDER BY id DESC LIMIT ?''',
                           (our_user_id, "NULL", n_last_messages))
            data = cursor.fetchall()
            if data and data[0]:
                for message in reversed(data):
                    messages.append({'text': message[0], 'role': message[1]})
                    used_tokens = max(used_tokens, message[2])
            return messages, used_tokens
    except Exception as e:
        logging.error(e)


def count_all_limits(our_user_id, limit_type):
    try:
        with sqlite3.connect("DB_FILE.db") as conn:
            cursor = conn.cursor()
            cursor.execute(f'''SELECT SUM({limit_type}) FROM messages WHERE user_id=?''', (our_user_id,))
            data = cursor.fetchone()
            if data and data[0]:
                return data[0]
            else:
                return 0
    except Exception as e:
        logging.error(e)

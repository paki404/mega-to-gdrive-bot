# plugins/login.py
from pyrogram import Client, filters
from pyrogram.types import Message
import sqlite3
import os

DB_NAME = "users.db"

def init_db():
    """Pehli baar bot chale to table bana dega"""
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (user_id INTEGER PRIMARY KEY,
                      mega_email TEXT,
                      mega_pass TEXT)''')
        conn.commit()
        conn.close()

def save_mega(user_id: int, email: str, password: str):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("REPLACE INTO users (user_id, mega_email, mega_pass) VALUES (?,?,?)",
              (user_id, email, password))
    conn.commit()
    conn.close()

def get_mega(user_id: int):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT mega_email, mega_pass FROM users WHERE user_id =?", (user_id,))
    res = c.fetchone()
    conn.close()
    return res # (email, pass) ya None

init_db()

def mega_login(client: Client, message: Message):
    """/login email password"""
    try:
        parts = message.text.split(" ", 2)
        if len(parts)!= 3:
            return message.reply_text("**Usage:** `/login your_email your_password`\n\nExample: `/login abc@gmail.com mypass123`")

        email, password = parts[1], parts[2]
        user_id = message.from_user.id

        msg = message.reply_text("`Checking your Mega login...`")

        # Check kar lo ke login sahi hai ya nahi
        from mega import Mega
        try:
            mega = Mega()
            m = mega.login(email, password)
            m.get_user() # agar ye chal gaya to login sahi hai
        except Exception as e:
            msg.edit_text(f"❌ Login Failed: `Invalid Email or Password`\nError: `{e}`")
            return

        save_mega(user_id, email, password)
        msg.edit_text(f"✅ Mega login saved successfully\n**Email:** `{email}`\n\nAb mujhe file bhejo upload karne ke liye.")

    except Exception as e:
        message.reply_text(f"**Error:** `{e}`")
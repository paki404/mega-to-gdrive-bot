# plugins/rm.py
from pyrogram import Client, filters
from pyrogram.types import Message
from mega import Mega
import sqlite3

DB_NAME = "users.db"

def get_mega(user_id: int):
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT mega_email, mega_pass FROM users WHERE user_id =?", (user_id,))
        res = c.fetchone()
        conn.close()
        return res
    except:
        return None

def mega_rm(client: Client, message: Message): # <-- NAAM TEAK KAR DIYA
    """/rm filename.ext -> User ke apne Mega se file delete"""
    user_creds = get_mega(message.from_user.id)
    if not user_creds:
        return message.reply_text("❌ Pehle `/login email password` se Mega account add karo.")

    MEGA_EMAIL, MEGA_PASS = user_creds

    if len(message.command) < 2:
        return message.reply_text("**Usage:** `/rm filename.ext`")

    file_name = " ".join(message.command[1:])
    msg = message.reply_text(f"`Searching {file_name} in your Mega...`")

    try:
        mega = Mega()
        m = mega.login(MEGA_EMAIL, MEGA_PASS)

        files = m.find(file_name)
        if not files:
            return msg.edit_text(f"❌ `{file_name}` not found in your Mega.")

        file_id = list(files.keys())[0]
        m.delete(file_id)
        msg.edit_text(f"✅ `File removed from your Mega:` `{file_name}`")

    except Exception as e:
        msg.edit_text(f"**Mega Error:** `{e}`")
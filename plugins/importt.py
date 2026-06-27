# plugins/importt.py
from pyrogram import Client, filters
from pyrogram.types import Message
from mega import Mega
import sqlite3
import re

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

def mega_import(client: Client, message: Message): # <-- NAAM TEAK
    """/import mega.nz/folder... -> Link ko user ke Mega me copy karega"""
    user_creds = get_mega(message.from_user.id)
    if not user_creds:
        return message.reply_text("❌ Pehle `/login email password` se Mega account add karo.")

    MEGA_EMAIL, MEGA_PASS = user_creds

    if len(message.command) < 2:
        return message.reply_text("**Usage:** `/import https://mega.nz/folder/...#key`")

    link = " ".join(message.command[1:])
    
    # Check karo link Mega ka hai ya nahi
    if "mega.nz" not in link:
        return message.reply_text("❌ Sirf `mega.nz` link do.")

    msg = message.reply_text("`Importing to your Mega...`")

    try:
        mega = Mega()
        m = mega.login(MEGA_EMAIL, MEGA_PASS)
        
        # mega.py me import_url hota hai
        m.import_url(link) 
        msg.edit_text(f"✅ `Link imported to your Mega successfully.`\n`Link:` {link}")

    except Exception as e:
        msg.edit_text(f"**Mega Error:** `{e}`\nLink public hai ya key sahi hai?")
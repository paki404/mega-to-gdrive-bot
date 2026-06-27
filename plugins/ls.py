# plugins/ls.py
from pyrogram import Client, filters
from pyrogram.types import Message
from mega import Mega
import sqlite3
import humanize

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

def mega_ls(client: Client, message: Message):
    """/ls folder_name -> User ke apne Mega ki files list"""
    user_creds = get_mega(message.from_user.id)
    if not user_creds:
        return message.reply_text("❌ Pehle `/login email password` se Mega account add karo.")

    MEGA_EMAIL, MEGA_PASS = user_creds
    folder_name = " ".join(message.command[1:]) if len(message.command) > 1 else ""
    msg = message.reply_text("`Loading your Mega files...`")

    try:
        mega = Mega()
        m = mega.login(MEGA_EMAIL, MEGA_PASS)

        if folder_name:
            files = m.find(folder_name)
            if not files:
                return msg.edit_text(f"❌ Folder/File `{folder_name}` not found.")
            folder_id = list(files.keys())[0]
            data = m.get_files_in_node(folder_id)
        else:
            data = m.get_files()

        if not data:
            return msg.edit_text("📂 Your Mega is empty.")

        text = f"**📂 Your Mega.nz Files:**\n\n"
        for i, (file_id, f) in enumerate(data.items()):
            if i >= 20:
                text += f"\n...and more"
                break
            name = f['a']['n']
            size = humanize.naturalsize(f.get('s', 0))
            text += f"`{name}` - `{size}`\n"

        msg.edit_text(text)

    except Exception as e:
        msg.edit_text(f"**Mega Error:** `{e}`")
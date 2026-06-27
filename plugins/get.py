# plugins/get.py
from pyrogram import Client, filters
from pyrogram.types import Message
from mega import Mega
import os
import sqlite3
import time
import humanize
import asyncio
from threading import Thread

DB_NAME = "users.db"

def get_mega(user_id: int):
    """Database se user ka mega login nikalta hai"""
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT mega_email, mega_pass FROM users WHERE user_id =?", (user_id,))
        res = c.fetchone()
        conn.close()
        return res # (email, pass) ya None
    except:
        return None

def mega_get(client: Client, message: Message):
    """/get filename.ext -> User ke apne Mega se Telegram me"""
    user_creds = get_mega(message.from_user.id)
    if not user_creds:
        return message.reply_text("❌ Pehle `/login email password` se Mega account add karo.")

    MEGA_EMAIL, MEGA_PASS = user_creds

    if len(message.command) < 2:
        return message.reply_text("**Usage:** `/get filename.ext`\nExample: `/get movie.mkv`")

    file_name = " ".join(message.command[1:])
    msg = message.reply_text(f"`Searching in your Mega...`")

    try:
        mega = Mega()
        m = mega.login(MEGA_EMAIL, MEGA_PASS)

        files = m.find(file_name)
        if not files:
            return msg.edit_text(f"❌ `{file_name}` not found in your Mega.nz")

        file_id = list(files.keys())[0]
        actual_name = files[file_id]['a']['n']

        msg.edit_text(f"✅ Found: `{actual_name}`\n`Downloading from Mega...`")

        c_time = time.time()
        def download_task():
            path = m.download(file_id, dest_path='downloads/')
            msg.edit_text("`Uploading to Telegram...`")
            client.send_document(
                message.chat.id,
                path,
                caption=f"✅ From your Mega.nz: `{actual_name}`",
                progress=progress_for_pyrogram,
                progress_args=("📤 Uploading", msg, c_time)
            )
            os.remove(path)
            msg.delete()

        Thread(target=download_task, daemon=True).start()

    except Exception as e:
        msg.edit_text(f"**Mega Error:** `{e}`\nPassword galat ho sakta hai?")

async def progress_for_pyrogram(current, total, ud_type, message, start):
    now = time.time()
    diff = now - start
    if round(diff % 5.00) == 0 or current == total:
        try:
            percentage = current * 100 / total
            speed = current / diff if diff > 0 else 0
            time_to_completion = round((total - current) / speed) if speed > 0 else 0
            eta = time.strftime("%H:%M:%S", time.gmtime(time_to_completion))
            progress = "[{0}{1}] {2}%\n".format(
                ''.join(["█" for i in range(int(percentage / 5))]),
                ''.join(["░" for i in range(20 - int(percentage / 5))]),
                round(percentage, 2))
            tmp = progress + f"`{humanize.naturalsize(current)}` of `{humanize.naturalsize(total)}`\n**Speed:** `{humanize.naturalsize(speed)}/s`\n**ETA:** `{eta}`"
            await message.edit_text(f"{ud_type}\n\n{tmp}")
        except:
            pass
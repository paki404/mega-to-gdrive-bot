from pyrogram import Client, filters, enums
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from mega import Mega
import os
import humanize
import time
import asyncio
import sqlite3
from threading import Thread

DB_NAME = "users.db"

def get_mega(user_id):
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

def gdrive_mega1(app, message): # <-- bot.py isko call karta hai
    """Telegram file -> User ka apna Mega upload"""
    user_creds = get_mega(message.from_user.id)
    if not user_creds:
        return message.reply_text("❌ Pehle `/login email password` se Mega account add karo.")

    MEGA_EMAIL, MEGA_PASS = user_creds

    if not (message.document or message.video or message.audio or message.photo):
        return message.reply_text("📁 File bhejo.")

    try:
        msg = message.reply_text("`Downloading... 0%`")
        c_time = time.time()

        file_path = app.download_media(
            message,
            progress=progress_for_pyrogram,
            progress_args=("📥 Downloading", msg, c_time)
        )

        file_size = os.path.getsize(file_path)
        file_name = os.path.basename(file_path)
        msg.edit_text(f"✅ Downloaded\n**Size:** {humanize.naturalsize(file_size)}\n\n`Logging into your Mega...`")

        mega = Mega()
        m = mega.login(MEGA_EMAIL, MEGA_PASS)

        msg.edit_text("`Uploading to Mega.nz... 0%`")

        def upload_task():
            m.upload(file_path, None, callback=lambda x, y: progress_mega(x, y, msg))
            os.remove(file_path)
            msg.edit_text(f"✅ Uploaded to your Mega.nz\n**File:** `{file_name}`")

        Thread(target=upload_task, daemon=True).start()

    except Exception as e:
        message.reply_text(f"**Mega Error:** `{e}`\nPassword galat ho sakta hai.")

def gdrive_answer(app, message):
    """Telegram file -> Google Drive upload"""
    if not (message.document or message.video or message.audio or message.photo):
        return message.reply_text("📁 File bhejo.")

    try:
        msg = message.reply_text("`Authenticating Google Drive...`")
        gauth = GoogleAuth()
        gauth.LoadCredentialsFile("token.txt")
        if gauth.credentials is None:
            gauth.LocalWebserverAuth()
        elif gauth.access_token_expired:
            gauth.Refresh()
        else:
            gauth.Authorize()
        gauth.SaveCredentialsFile("token.txt")
        drive = GoogleDrive(gauth)

        msg.edit_text("`Downloading...`")
        c_time = time.time()
        file_path = app.download_media(
            message,
            progress=progress_for_pyrogram,
            progress_args=("📥 Downloading", msg, c_time)
        )

        file_name = os.path.basename(file_path)
        msg.edit_text("`Uploading to Google Drive...`")
        gfile = drive.CreateFile({'title': file_name})
        gfile.SetContentFile(file_path)
        gfile.Upload()
        os.remove(file_path)

        msg.edit_text(f"✅ Uploaded\n**Link:** https://drive.google.com/file/d/{gfile['id']}/view")

    except Exception as e:
        message.reply_text(f"**GDrive Error:** `{e}`")

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

def progress_mega(uploaded, total, msg):
    try:
        if total > 0:
            percent = (uploaded / total) * 100
            text = f"`Uploading to Mega.nz... {round(percent, 2)}%`"
            asyncio.run_coroutine_threadsafe(msg.edit_text(text), msg._client.loop)
    except Exception:
        pass
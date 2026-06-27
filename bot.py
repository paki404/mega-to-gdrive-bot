from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from plugins.login import mega_login
from plugins.get import mega_get
from plugins.ls import mega_ls
from plugins.rm import mega_rm
from plugins.importt import mega_import
from plugins.gdrive import gdrive_mega1, gdrive_answer
from userbot import app
from os import environ

my_user_id = environ["TELEGRAM_USER_ID"]

@app.on_message(filters.command(["start"]))
def start(client: Client, message: Message):
    message.reply_text("**Welcome to Multi-User Mega Bot**\n\n"
                       "1. `/login email password`\n"
                       "2. `/ls`, `/get`, `/rm`, `/import`")

@app.on_message(filters.regex(r'#login'))
def megalogin(client: Client, message: Message):
    mega_login(client, message)

@app.on_message(filters.regex(r'#rm'))
def mega_rm_cmd(client: Client, message: Message):
    mega_rm(client, message)

@app.on_message(filters.regex(r'#import'))
def mega_import_cmd(client: Client, message: Message):
    mega_import(client, message)

@app.on_message(filters.regex(r'#get|mega.co.nz|mega.nz'))
def mega_get_cmd(client: Client, message: Message):
    mega_get(client, message)

@app.on_message(filters.regex(r'#ls'))
def megals(client: Client, message: Message):
    mega_ls(client, message)

@app.on_message(filters.audio | filters.document | filters.photo | filters.video)
def gdrive_mega(client: Client, message: Message):
    gdrive_mega1(client, message)

# Ye function bahar nikala hai
@app.on_callback_query()
def gdrive_mega_callback(client: Client, callback_query: CallbackQuery):
    gdrive_answer(client, callback_query)

app.run()
import asyncio
import os
import re
import subprocess
import sys
import traceback
from inspect import getfullargspec
from io import StringIO
from time import time

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

API_ID = 123456  
API_HASH = "your_api_hash"
BOT_TOKEN = "your_bot_token"
OWNER_ID = 7208410467
LOG_CHAT_ID = -1002519094633

app = Client("JapaneseXEvalBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

async def edit_or_reply(msg: Message, **kwargs):
    func = msg.edit_text if msg.from_user.is_self else msg.reply
    spec = getfullargspec(func.__wrapped__).args
    await func(**{k: v for k, v in kwargs.items() if k in spec})

async def aexec(code: str, client: Client, message: Message):
    local_vars = {}
    exec(
        f"async def __aexec(client, message):\n" +
        "\n".join(f"    {line}" for line in code.split("\n")),
        globals(),
        local_vars
    )
    return await local_vars["__aexec"](client, message)

@app.on_message(filters.command("e") & filters.user(OWNER_ID))
async def eval_command(client: Client, message: Message):
    if len(message.command) < 2:
        return await edit_or_reply(message, text="ᴘʟᴇᴀꜱᴇ ᴘʀᴏᴠɪᴅᴇ ᴍᴇ ᴄᴏᴅᴇ ᴛᴏ ᴇᴠᴀʟᴜᴀᴛᴇ ᴍʏ ᴍᴀꜱᴛᴇʀ")
    code = message.text.split(" ", maxsplit=1)[1]
    t1 = time()
    stdout = sys.stdout
    stderr = sys.stderr
    sys.stdout = StringIO()
    sys.stderr = StringIO()
    try:
        await aexec(code, client, message)
    except Exception:
        output = traceback.format_exc()
    else:
        output = sys.stdout.getvalue() or sys.stderr.getvalue() or "ꜱᴜᴄᴄᴇꜱꜱ"
    sys.stdout = stdout
    sys.stderr = stderr
    if len(output) > 4000:
        output = output[:4000] + "\n\n⚠️ ᴏᴜᴛᴘᴜᴛ ᴛʀᴜɴᴄᴀᴛᴇᴅ."
    t2 = time()
    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text="⏳", callback_data=f"runtime {round(t2-t1, 2)}s")]]
    )
    await message.reply_text(
        f"<b>📤 ʀᴇꜱᴜʟᴛ:</b>\n<pre language='python'>{output}</pre>",
        quote=True,
        reply_markup=reply_markup
    )
    
    try:
        await client.send_message(
            LOG_CHAT_ID,
            f"#ᴇᴠᴀʟ ʙʏ [{message.from_user.first_name}](tg://user?id={message.from_user.id}):\n\n"
            f"<b>📥 ᴄᴏᴅᴇ:</b>\n<pre language='python'>{code}</pre>\n\n"
            f"<b>📤 ᴏᴜᴛᴘᴜᴛ:</b>\n<pre language='python'>{output}</pre>",
        )
    except Exception as e:
        print("Logging failed:", e)

@app.on_message(filters.command("sh") & filters.user(OWNER_ID))
async def shellrunner(client: Client, message: Message):
    if len(message.command) < 2:
        return await edit_or_reply(message, text="<b>Example:</b>\n/sh ɢɪᴛ ᴘᴜʟʟ")
    text = message.text.split(None, 1)[1]
    output = ""
    if "\n" in text:
        lines = text.split("\n")
    else:
        lines = [text]

    for cmd in lines:
        shell = re.split(r""" (?=(?:[^'"]|'[^']*'|"[^"]*")*$)""", cmd)
        try:
            process = subprocess.Popen(shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = process.communicate()
            if out:
                output += out.decode("utf-8")
            if err:
                output += err.decode("utf-8")
        except Exception as e:
            error_trace = traceback.format_exc()
            return await edit_or_reply(message, text=f"<b>ᴇʀʀᴏʀ:</b>\n<pre>{error_trace}</pre>")

    if not output.strip():
        output = "No Output"

    if len(output) > 4096:
        with open("output.txt", "w+", encoding="utf-8") as f:
            f.write(output)
        await client.send_document(
            message.chat.id,
            "output.txt",
            caption="<code>Output is too long, sent as file</code>",
            reply_to_message_id=message.id
        )
        os.remove("output.txt")
    else:
        await edit_or_reply(message, text=f"<b>ᴏᴜᴛᴘᴜᴛ:</b>\n<pre>{output}</pre>")


app.run()

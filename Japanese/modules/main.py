import asyncio
import sys
import traceback
from io import StringIO
from pyrogram import Client, filters
from pyrogram.types import Message
from config import API_ID, API_HASH, BOT_TOKEN

OWNER_ID = 7208410467
LOG_CHAT_ID = -1002519094633

app = Client("EvalBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

async def edit_or_reply(message: Message, text: str):
    if message.from_user and message.chat.type in ["group", "supergroup"]:
        return await message.reply(text)
    return await message.reply(text)

async def aexec(code: str, client: Client, message: Message):
    exec(
        f"async def __aexec(client, message):\n"
        + "\n".join(f"    {line}" for line in code.split("\n"))
    )
    return await locals()["__aexec"](client, message)

@app.on_message(filters.command("eval") & filters.user(OWNER_ID))
async def eval_command(client: Client, message: Message):
    if len(message.command) < 2:
        return await edit_or_reply(message, "__❗ Please provide code to evaluate.__")

    code = message.text.split(" ", maxsplit=1)[1]

    stdout = sys.stdout
    stderr = sys.stderr
    sys.stdout = StringIO()
    sys.stderr = StringIO()

    try:
        await aexec(code, client, message)
    except Exception:
        output = traceback.format_exc()
    else:
        output = sys.stdout.getvalue() or sys.stderr.getvalue() or "✅ Success"

    sys.stdout = stdout
    sys.stderr = stderr

    if len(output) > 4000:
        output = output[:4000] + "\n\n⚠️ Output truncated."

    await message.reply_text(f"<b>📤 Result:</b>\n<pre language='python'>{output}</pre>", quote=True)

    try:
        await client.send_message(
            LOG_CHAT_ID,
            f"#Eval used by [{message.from_user.first_name}](tg://user?id={message.from_user.id}):\n\n"
            f"<b>📥 Code:</b>\n<pre language='python'>{code}</pre>\n\n"
            f"<b>📤 Output:</b>\n<pre language='python'>{output}</pre>",
        )
    except Exception as log_err:
        print("Failed to log eval:", log_err)

app.run()

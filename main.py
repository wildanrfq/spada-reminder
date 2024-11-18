import asqlite, sys, os, datetime

from telegram import Update
from telegram.ext import (
    ContextTypes,
    CommandHandler as Command,
    Application,
)
from telegram.constants import ReactionEmoji as Emoji
from dotenv import load_dotenv

from classes import SpadaCtx, SpadaDatabase
from reminders import schedule_jobs
from commands import *

load_dotenv()


async def post_init(application: Application):
    application.bot_data["uptime"] = datetime.datetime.now(datetime.UTC)
    schedule_jobs(application.job_queue)
    pool = await asqlite.create_pool("spada.db")
    application.bot_data["db"] = SpadaDatabase(pool)
    restart = await application.bot_data["db"].fetchone("SELECT * FROM restart;")
    if restart.status:
        await application.bot.set_message_reaction(
            restart.chat_id, restart.message_id, Emoji.THUMBS_UP
        )
        await application.bot_data["db"].execute("UPDATE restart SET status = ?;", 0)
    print("Logged in.")


def main():
    context = ContextTypes(context=SpadaCtx)

    commands = [
        Command("r", restart),
        Command("p", ping),
        Command("ping", ping),
        Command("u", uptime),
        Command("eval", e),
        Command("mock", mock),
        Command("send", send),
    ]

    application = (
        Application.builder()
        .token(os.getenv("TOKEN"))
        .context_types(context)
        .post_init(post_init)
        .build()
    )
    for command in commands:
        application.add_handler(command)

    application.run_polling(allowed_updates=Update.ALL_TYPES)

    if application.bot_data.get("restart"):
        os.execl(sys.executable, sys.executable, *sys.argv)


if __name__ == "__main__":
    main()

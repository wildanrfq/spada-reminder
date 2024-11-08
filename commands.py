import asyncio
from telegram import Update
from telegram.constants import ReactionEmoji as Emoji

from classes import SpadaCtx


async def ping(update: Update, ctx: SpadaCtx):
    await ctx.reply("Ping!")


async def restart(update: Update, ctx: SpadaCtx):
    if not ctx.is_owner():
        return

    print("Restarting...")
    ctx.bot_data["restart"] = True
    print(ctx.message.id)
    await ctx.db.execute(
        "UPDATE restart SET chat_id = ?, message_id = ?, status = ?;",
        ctx.message.chat_id,
        ctx.message.id,
        1,
    )
    ctx.application.stop_running()


async def reg(update: Update, ctx: SpadaCtx):
    """Mendaftarkan."""
    if await ctx.is_registered():
        registered = await ctx.reply("You already registered!")
        await asyncio.sleep(3)
        return await registered.delete()

    await ctx.db.execute("INSERT INTO users VALUES(?);", (ctx.chat_id))
    await ctx.react(Emoji.THUMBS_UP)


async def unreg(update: Update, ctx: SpadaCtx):
    if not await ctx.is_registered():
        registered = await ctx.reply("You haven't registered!")
        await asyncio.sleep(3)
        await registered.delete()

    await ctx.db.execute("DELETE FROM users WHERE id = ?;", (ctx.sender_id))
    await ctx.react(Emoji.THUMBS_UP)

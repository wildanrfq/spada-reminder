import datetime, time, io, textwrap, traceback

from telegram import Update
from telegram.constants import ReactionEmoji as Emoji

from contextlib import redirect_stdout
from classes import SpadaCtx, MD
from reminders import absen, Absen, markup


async def e(update: Update, ctx: SpadaCtx):
    if not ctx.is_owner():
        return

    env = {"ctx": ctx, "update": update}

    env.update(globals())
    body = " ".join(ctx.args)
    stdout = io.StringIO()

    to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

    try:
        exec(to_compile, env)
    except Exception as e:
        return await ctx.reply(f"```py\n{e.__class__.__name__}: {e}\n```")

    func = env["func"]
    try:
        with redirect_stdout(stdout):
            ret = await func()
    except Exception as e:
        value = stdout.getvalue()
        await ctx.reply(f"```py\n{value}{traceback.format_exc()}\n```")
    else:
        value = stdout.getvalue()
        try:
            await ctx.react(Emoji.THUMBS_UP)
        except:
            pass

        if ret is None:
            if value:
                await ctx.reply(f"```py\n{value}\n```")
        else:
            await ctx.reply(f"```py\n{value}{ret}\n```")


async def ping(update: Update, ctx: SpadaCtx):
    start = time.monotonic()
    await ctx.bot.send_chat_action(update.effective_chat.id, "typing")
    end = time.monotonic()
    res = (end - start) * 1000
    await ctx.reply(f"Ping: {int(res)} ms")


async def uptime(update: Update, ctx: SpadaCtx):
    delta_uptime = datetime.datetime.now(datetime.UTC) - ctx.bot_data["uptime"]
    hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    await ctx.reply(f"Uptime:\n{days}d, {hours}h, {minutes}m, {seconds}s")


async def restart(update: Update, ctx: SpadaCtx):
    if not ctx.is_owner():
        return

    print("Restarting...")
    ctx.bot_data["restart"] = True
    await ctx.db.execute(
        "UPDATE restart SET chat_id = ?, message_id = ?, status = ?;",
        ctx.message.chat_id,
        ctx.message.id,
        1,
    )
    ctx.application.stop_running()


async def mock(update: Update, ctx: SpadaCtx):
    if not ctx.is_owner():
        return

    link_key = ctx.args[0]
    reply_markup = (
        markup([Absen.links[f"{link_key}_b"], Absen.links[f"{link_key}_c"]], link_key)
        if link_key == "prak_basdat"
        else (
            markup(
                [Absen.links[f"{link_key}_c"], Absen.links[f"{link_key}_d"]], link_key
            )
            if link_key == "prak_alpro"
            else markup(Absen.links[link_key])
        )
    )
    hari = ""
    for i, item in enumerate(Absen.schedule):
        if item[2] == link_key:
            hari = item[0]

    await ctx.reply(absen(hari, link_key), reply_markup)


async def send(update: Update, ctx: SpadaCtx):
    if not ctx.is_owner():
        return

    link_key = ctx.args[0]
    reply_markup = (
        markup([Absen.links[f"{link_key}_b"], Absen.links[f"{link_key}_c"]], link_key)
        if link_key == "prak_basdat"
        else (
            markup(
                [Absen.links[f"{link_key}_c"], Absen.links[f"{link_key}_d"]], link_key
            )
            if link_key == "prak_alpro" or link_key == "prak_basdat"
            else markup(Absen.links[link_key])
        )
    )
    hari = ""
    for i, item in enumerate(Absen.schedule):
        if item[2] == link_key:
            hari = item[0]

    await ctx.bot.send_message(
        -1002309269021,
        absen(hari, link_key),
        parse_mode=MD,
        reply_markup=reply_markup,
    )

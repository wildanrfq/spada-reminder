from telegram import Update
from telegram.ext import CallbackContext, Application
from telegram.constants import ReactionEmoji


class SpadaDatabase:
    def __init__(self, pool):
        self.pool = pool

    async def fetch(self, query, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetchall(query, args)

    async def fetchone(self, query, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetchone(query, args)

    async def execute(self, query, *args):
        async with self.pool.acquire() as conn:
            execute = await conn.execute(query, args)
            return await execute.fetchall()


class SpadaCtx(CallbackContext):
    def __init__(self, application: Application, chat_id=None, user_id=None):
        super().__init__(application=application, chat_id=chat_id, user_id=user_id)
        self._db = None
        self._message = None
        self._sender_id = None
        self.chat_id = chat_id
        self.is_registered = self.is_registered
        self.is_owner = self.is_owner

    @property
    def message(self):
        return self._message

    @property
    def db(self):
        return self._db

    @property
    def sender_id(self):
        return self._sender_id

    def is_owner(self):
        return self._sender_id == 1231482727

    async def is_registered(self):
        users = await self._db.fetch("SELECT * FROM users;")
        return self._sender_id in [u.id for u in users]

    async def react(self, reaction: ReactionEmoji):
        return await self._message.set_reaction(reaction)

    async def reply(self, message):
        return await self.application.bot.send_message(
            chat_id=self._chat_id, text=message, disable_notification=True, parse_mode="MarkdownV2"
        )

    @classmethod
    def from_update(cls, update: Update, application: Application):
        context = super().from_update(update, application)
        context._db = application.bot_data["db"]
        context._sender_id = update.effective_user.id
        context._message = update.effective_message
        return context

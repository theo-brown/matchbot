import aiosqlite

database_file = 'database.db'

class Database:
    from . import channels
    from . import pickems
    from . import users

    def __init__(self, bot):
        self.bot = bot
        bot.loop.run_until_complete(self.async_init())

    async def async_init(self):
        self.db = await aiosqlite.connect(database_file, isolation_level=None)

        for table in (self.channels, self.pickems, self.users):
            table.db = self.db
            await table.create()

def setup(bot):
    bot.db = Database(bot)

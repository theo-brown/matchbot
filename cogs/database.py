import sql.users, sql.channels, sql.pickems
from . import Cog

class DatabaseCog(Cog, name='Database commands'):
    def __init__(self, bot):
        bot.loop.run_until_complete(self.database_init(bot))
        
    async def database_init(self, bot):
        # Create the sql tables if they don't exist
        await sql.channels.create()
        await sql.pickems.create()
        await sql.users.create()

def setup(bot):
    bot.add_cog(DatabaseCog(bot))

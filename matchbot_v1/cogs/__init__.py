from discord.ext import commands as cmds

class Cog(cmds.Cog):
    def __init__(self, bot):
        self.bot = bot

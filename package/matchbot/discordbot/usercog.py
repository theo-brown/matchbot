import discord.ext.commands as commands

class UserCog(commands.Cog, name='User commands'):
   def __init__(self, bot):
      self.bot = bot
      super().__init__()

   @commands.command()
   async def signup(self, ctx, display_name):
      # Get steam id
      pass
      # Add entry
      #(steam_id, display_name, ctx.author.id)




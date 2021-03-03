import discord
from discord.ext import commands
from steam import steamid
import logging
from dotenv import load_dotenv
from os import getenv

load_dotenv()

logging.basicConfig(level=logging.INFO)  # show all logs above INFO level

# Enable the bot to see members roles etc
bot_intents = discord.Intents.default()
bot_intents.members = True

# Create a bot instance
bot = commands.Bot(command_prefix='!', intents=bot_intents)

bot.load_extension('sql')
bot.load_extension('cogs.channels')
bot.load_extension('cogs.pickems')
bot.load_extension('cogs.lobby')
bot.load_extension('cogs.match')

@bot.command()
async def steam(ctx, profile_url: str, user=None):
    """Link your Steam and Discord accounts for server configuration."""
    if user is None:
        user = ctx.author
    steam64_id = steamid.steam64_from_url(profile_url)
    await ctx.bot.db.users.add_steam64_id(user.id, steam64_id)
    await ctx.send(f"Linked {user.mention} to <{profile_url}>")

if __name__ == '__main__':
    bot.run(getenv('BOT_TOKEN'))

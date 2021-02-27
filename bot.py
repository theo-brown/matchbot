import discord
from discord.ext import commands
import sql.channels, sql.leaderboards, sql.users
from steam import steamid

import logging
logging.basicConfig(level=logging.INFO)  # show all logs above INFO level

# Enable the bot to see members roles etc
bot_intents = discord.Intents.default()
bot_intents.members = True

# Create a bot instance
bot = commands.Bot(command_prefix='!', intents=bot_intents)

bot.load_extension('cogs.channels')
bot.load_extension('cogs.leaderboard')
bot.load_extension('cogs.lobby')
bot.load_extension('cogs.match')

@bot.command()
async def steam(ctx, profile_url: str, user=None):
    """Link your steam and discord accounts for server configuration."""
    if user is None:
        user = ctx.author
    steam64_id = steamid.steam64_from_url(profile_url)
    sql.users.add_steam64_id(steam64_id, user.id)
    await ctx.send(f"Linked {user.mention} to <{profile_url}>")

with open('bot_token.txt') as f:
    bot_token = f.read().strip()

if __name__ == '__main__':
    bot.run(bot_token)

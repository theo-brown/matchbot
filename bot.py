import discord
from discord.ext import commands
from steam import steamid
import logging
from dotenv import load_dotenv
from os import getenv
import parsing

load_dotenv()

# Set up logging
# Log in console
logging.basicConfig(level=logging.INFO)
# Log to file
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='matchbot.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Enable the bot to see members roles etc
bot_intents = discord.Intents.default()
bot_intents.members = True

# Create a bot instance
bot = commands.Bot(command_prefix='!', intents=bot_intents)

bot.load_extension('database')
bot.load_extension('cogs.channels')
bot.load_extension('cogs.pickems')
bot.load_extension('cogs.lobby')
bot.load_extension('cogs.match')

@bot.command()
async def steam(ctx, *args):
    """Link your Steam and Discord accounts for server configuration."""
    args = list(args)
    mentions = ctx.message.mentions
    if len(mentions):
        user = mentions[0]
        args.remove(user.mention)
    else:
        user = ctx.author
    if len(args) == 1:
        profile_url = args[0]
        steam64_id = steamid.steam64_from_url(profile_url)
        await ctx.bot.db.users.add_steam64_id(user.id, steam64_id)
        await ctx.send(f"Linked {user.mention} to <{profile_url}>")
    else:
        steam64_id = await ctx.bot.db.users.get_steam64_id(user.id)
        await ctx.send(f"{user.mention}'s steam64_id is {steam64_id}")

if __name__ == '__main__':
    bot.run(getenv('BOT_TOKEN'))

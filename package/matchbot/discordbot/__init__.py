import discord
import logging
from dotenv import load_dotenv
from os import getenv
import sys
from usercog import UserCog
load_dotenv()

# Set up logging
# Log in console
logging.basicConfig(level=logging.INFO)
# Log to file
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)

# Enable the bot to see members roles etc
bot_intents = discord.Intents.default()
bot_intents.members = True

# Create a bot instance
bot = discord.ext.commands.Bot(command_prefix='!', intents=bot_intents)
bot.add_cog(UserCog(bot))

@bot.event
async def on_command_error(ctx, error):
    error_string = ('Error raised\n'
                    f'In server: {ctx.guild.name}\n'
                    f'In channel: {ctx.channel.name}\n'
                    f'From user: {ctx.author}\n'
                    f'In message: {ctx.message.content}\n'
                    f'Error: {error}\n'
                    f'Traceback: {sys.exc_info()[2]}')

    logging_channel = bot.get_channel(int(getenv('LOG_CHANNEL_ID')))
    await logging_channel.send(f'```{error_string}```')

    logging.error(error_string, exc_info=error)

if __name__ == '__main__':
    bot.run(getenv('BOT_TOKEN'))

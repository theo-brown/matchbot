"""
EVL Discord Bot template by Theo Brown
Licensed under GNU GPLv3
https://github.com/theo-brown/EVL-bot-template
"""

import discord
import bot_util, bot_commands

client = discord.Client()

@client.event
async def on_ready():
    print("Logged in as {}".format(client.user))

@client.event
async def on_message(message):
    if message.author == client.user:
        # Ignore messages from this bot
        return
    elif message.content.startswith(bot_util.COMMAND_PREFIX):
        trigger, args, kwargs = bot_util.parse_args(message)
        if trigger in bot_commands.commands.keys():
            await bot_commands.commands[trigger](message, args, kwargs) 
            if bot_util.ECHO_COMMAND_ARGS:
                await message.channel.send("Trigger: `{}`\nargs: `{}`\nkwargs: `{}`".format(trigger, args, kwargs))
        elif bot_util.ERROR_ON_UNRECOGNISED_COMMAND:
            await message.channel.send("Error: command `{}` has not been recognised.".format(trigger))

#if message.author.has_permissions(manage_guild=True)

with open('bot_token.txt') as f:
    bot_token = f.read().strip()

client.run(bot_token)

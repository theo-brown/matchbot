"""
EVL Discord Bot template by Theo Brown
Licensed under GNU GPLv3
https://github.com/theo-brown/EVL-bot-template
"""

import discord
import sys
import bot_util
from commands import hello, match, result

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
        
        if trigger == "help":
            available_commands = ""
            for m in sys.modules.keys():
                if m.startswith('commands.'):
                    available_commands += bot_util.COMMAND_PREFIX + m[9:] + '\n'
            await message.channel.send("Available commands:\n```{}```".format(available_commands))
        
        module_str = 'commands.' + trigger
        
        if module_str in sys.modules:
            
            module = sys.modules[module_str]
            
            if any(help_trigger in kwargs for help_trigger in ['h', 'help']):
                
                await module.help(message, args, kwargs)
                
            else:
                
                await module.run(message, args, kwargs) 
                
            if bot_util.ECHO_COMMAND_ARGS:
                
                await message.channel.send("Trigger: `{}`\nargs: `{}`\nkwargs: `{}`".format(trigger, args, kwargs))
                
        elif bot_util.ERROR_ON_UNRECOGNISED_COMMAND:
            
            await message.channel.send("Error: command `{}` has not been recognised.".format(trigger))
            

with open('bot_token.txt') as f:
    bot_token = f.read().strip()

client.run(bot_token)

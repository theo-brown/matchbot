"""
EVL Discord Bot template by Theo Brown
Licensed under GNU GPLv3
https://github.com/theo-brown/EVL-bot-template
"""

help_message = \
"""
`!help`: Sends a 'Hello World' message to the current channel.
"""

async def run(message, args, kwargs):
    await message.channel.send("Hello World!")
    
async def help(message, args, kwargs):
    await message.channel.send(help_message)
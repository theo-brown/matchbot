"""
EVL Discord Bot template by Theo Brown
Licensed under GNU GPLv3
https://github.com/theo-brown/EVL-bot-template
"""

help_message = \
"""
`!result`: used in the reply to a message created with `!match` to reflect the score of the match
Syntax: `!result <T1 score> <T2 score>`
"""

async def run(message, args, kwargs):
    if len(args) == 2:
        score = args[0] + "-" + args[1]
    elif len(args) == 1:
        score = args[0]
    else:
        await message.channel.send("Error: incorrect arguments. Correct usage: `!result <score1> <score2>` or `!result <score1>-<score2>")
        return
    if message.reference is None:
        await message.channel.send("Error: `!result` must be sent as a reply to a message.")
        return
    else:
        match_message = await message.channel.fetch_message(message.reference.message_id)
        if not match_message.content.startswith("**Match scheduled:**"):
            await message.channel.send("Error: `!result` must be sent as a reply to a message generated using `!match`.")
            return
        old_content = match_message.content.split("        ")
        new_content = "**Match result:**        " + old_content[1] + "        **" + score + "**"
        await match_message.edit(content=new_content)
    
async def help(message, args, kwargs):
    await message.channel.send(help_message)
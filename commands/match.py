"""
EVL Discord Bot template by Theo Brown
Licensed under GNU GPLv3
https://github.com/theo-brown/EVL-bot-template
"""
from discord import Embed

help_message = \
"""
```
!match @Team1 @Team2 [-d DATE -t TIME]
DATE: The day or date that the match will be played, provided as a string with no spaces
TIME: The times that the match will be played, provided as a string with no spaces
"""

async def run(message, args, kwargs):

    date = "Today "
    time = ""

    if len(args) != 2 or len(message.role_mentions) != 2:
        await message.channel.send("Error: Please @ exactly two teams.")
        return

    team1, team2 = message.role_mentions
    team1_players, team2_players = "", ""
    for user in message.guild.members:
        if team1 in user.roles:
            team1_players += user.mention + '\n'
        if team2 in user.roles:
            team2_players += user.mention + '\n'    

    if 'd' in kwargs.keys():
        date = kwargs['d'] + " "

    if 't' in kwargs.keys():
        time = "at " + kwargs['t']

    timestamp = date + time

    match_embed = Embed(title="**Match scheduled**", color=0xf1c40f)
    match_embed.add_field(name=":one: " + team1.name, value=team1_players, inline=True)
    match_embed.add_field(name=":two: " + team2.name, value=team2_players, inline=True)
    match_embed.set_footer(text=timestamp)

    match_message = await message.channel.send(embed=match_embed)
    await match_message.add_reaction("1\u20e3")
    await match_message.add_reaction("2\u20e3")



async def help(message, args, kwargs):
    # If you want to edit what happens when the user asks for help with
    # `!command --help`, you can edit this function
    await message.channel.send(help_message)
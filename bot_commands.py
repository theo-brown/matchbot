"""
Based on EVL Discord Bot template by Theo Brown
Licensed under GNU GPLv3
https://github.com/theo-brown/EVL-bot-template
"""
import discord
from datetime import datetime

async def hello(message, args, kwargs):
    await message.channel.send("Hello World!")

async def match(message, args, kwargs):
    date_formats = ["%d/%m", "%d.%m", "%a", "%A", "%a"]
    time_formats = ["%H%M","%H:%M", "%I%M", "%I:%M", "%I%M%p", "%I:%M%p", "%I%M %p", "%I:%M %p"]
    help_message_text = "Usage: `-match <@Team1> <@Team2> [-d date -t time]`"
    date = '*Today*'
    time = ''
    
    if 'help' in kwargs.keys() or 'h' in kwargs.keys():
        await message.channel.send(help_message_text)
        return
    
    if len(args) != 2:
        await message.channel.send("Error: Please provide exactly two teams.")
        return
    
    team1 = args[0]
    team2 = args[1]
    
    if 'd' in kwargs.keys():
        date = kwargs['d']
        unmatched_formats = 0
        for date_format in date_formats:
            try:
                datetime.strptime(date, date_format)
                break
            except ValueError:
                unmatched_formats +=1
        if unmatched_formats == len(date_formats):
            await message.channel.send("Error: Date `{}` not recognised.".format(date))
            return
        date = "*" + date + "* "
            
    if 't' in kwargs.keys():
        time = kwargs['t']
        unmatched_formats = 0
        for time_format in time_formats:
            try:
                datetime.strptime(time, time_format)
                break
            except ValueError:
                unmatched_formats +=1
        if unmatched_formats == len(time_formats):
            await message.channel.send("Error: Time `{}` not recognised.".format(time))
            return
        time = "*at " + time + "*"
        
    match_message_text = "**Match scheduled:**\n\n:one: {} vs :two: {}\n\n{}{}".format(team1, team2, date, time)
    
    match_message = await message.channel.send(match_message_text)
    await match_message.add_reaction("1\u20e3")
    await match_message.add_reaction("2\u20e3")


# commands dict has syntax {'command_string': command_function}
commands = {'hello': hello, \
            'match': match}

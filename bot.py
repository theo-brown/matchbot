import discord
from discord import Role, User, Embed, Colour, Member
from discord.ext import commands
from typing import Union
from sql import channels as chn
from sql import leaderboards as ldb
import parsedatetime as pdt
from datetime import datetime

# Enable the bot to see members roles etc
bot_intents = discord.Intents.default()
bot_intents.members = True

# Create a bot instance
bot = commands.Bot(command_prefix='!', intents=bot_intents)

# Create the sql tables if they don't exist
chn.create()
ldb.create()

@bot.event
async def on_ready():
    print("Connected as {}".format(bot.user))

###############################################################################
###############################################################################

# MODERATOR COMMANDS

# Channel    
@bot.command()
@commands.has_permissions(manage_channels=True)
async def channels(ctx, mode="show", mode_arg=''):
    mentioned_channels = ctx.message.raw_channel_mentions
    help_str = "Usage: `!channels [show/add/del/help] [autodelete <#channel(s)>] [redirect <#channel1> <#channel2>]`"
    if mode == "show":
        await ctx.send(chn.display(mode_arg))
    elif mode == "add":
        if mode_arg == "redirect":
            chn.set_redirectchannel(*mentioned_channels)
            await ctx.send("Redirecting bot responses from <#{}> to <#{}>".format(*mentioned_channels),
                     delete_after=10)
        elif mode_arg == "autodelete":
            for channel in mentioned_channels:
                chn.set_autodelete(channel, True)
                await ctx.send("Autodeleting bot triggers in <#{}>".format(channel))
        else:
            await ctx.send(help_str, delete_after=10)
    elif mode == "del":
        if mode_arg == "redirect":
            for channel in mentioned_channels:
                chn.set_redirectchannel(channel, channel)
                await ctx.send("Removed redirecting bot responses from <#{}>".format(channel),
                               delete_after=10)
        elif mode_arg == "autodelete":
            for channel in mentioned_channels:
                chn.set_autodelete(channel, False)
                await ctx.send("Removed autodeleting bot triggers in <#{}>".format(channel),
                         delete_after=10)
        else:
            if mentioned_channels:
                for channel in mentioned_channels:
                    chn.delete_row(channel)
                    await ctx.send("Removing entry <#{}>".format(channel))
            else:
                await ctx.send(help_str, delete_after=10)
    elif mode == "help":
        await ctx.send(help_str, delete_after=10)
        

@bot.listen()
async def on_message(msg):
    if chn.get_autodelete(msg.channel.id) and not msg.author.bot:
        await msg.delete(delay=10)


###############################################################################
###############################################################################

# MATCH COMMAND

@bot.command()
async def match(ctx, team1: Union[Role, Member, str], team2: Union[Role, Member, str], schedule_args=''):
    date = "Today"
    time = ''
    calendar = pdt.Calendar()
    
    for arg in schedule_args.split():
        time_obj, result_flag = calendar.parse(arg)
        if result_flag == 1: # If this is arg is only a date
            date = arg
        elif result_flag == 2: # if this arg is only a time
            time = " at " + arg

    embed = Embed(title="**Match scheduled**", colour=Colour.gold())
    embed.set_footer(text=date+time)

    for i,team in enumerate((team1, team2)):
        emoji = f'{i+1}\N{COMBINING ENCLOSING KEYCAP} '
        if isinstance(team, Member):
            embed.add_field(name=emoji, value=team.mention)
        elif isinstance(team, Role):
            embed.add_field(name=emoji+team.name, value='\n'.join(m.mention for m in team.members))
        else:
            embed.add_field(name=emoji+team, value='\u200b')

    send_channel = ctx.guild.get_channel(chn.get_redirect_channel(ctx.channel.id))
    match_message = await send_channel.send(embed=embed)
    await match_message.add_reaction("1\N{COMBINING ENCLOSING KEYCAP}")
    await match_message.add_reaction("2\N{COMBINING ENCLOSING KEYCAP}")

###############################################################################

# RESULT COMMAND
@bot.command()
async def result(ctx, *args):
    if ctx.message.reference is None:
        await ctx.send("Error: `!result` must be sent as a reply to a match message.")
        return
    elif len(args) % 2:
        await ctx.send("Error: please supply an even number of arguments (MAP/GAME and SCORE)")
        return
    else:
        match_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        match_embed = match_message.embeds[0]
        team1 = match_embed.fields[0].name
        team1_players = match_embed.fields[0].value
        team2 = match_embed.fields[1].name
        team2_players = match_embed.fields[1].value

        scores = {}
        for i in range(len(args) // 2):
            map_i = args[2 * i]
            score_i = args[2 * i + 1]
            scores[map_i] = score_i

        maps_won = [0, 0]
        round_diff = 0

        for map_played, map_score in scores.items():
            map_score_list = map_score.split('-')
            map_score_t1 = int(map_score_list[0])
            map_score_t2 = int(map_score_list[1])
            round_diff += map_score_t1 - map_score_t2
            if map_score_t1 > map_score_t2:
                scores[map_played] = "**{}** - {}\n".format(map_score_t1, map_score_t2)
                maps_won[0] += 1
            else:
                scores[map_played] = "{} - **{}**\n".format(map_score_t1, map_score_t2)
                maps_won[1] += 1

        if maps_won[0] > maps_won[1]:
            winner = team1[3:] + " wins"
            winner_icon = "https://twemoji.maxcdn.com/v/latest/72x72/31-20e3.png"
            winner_reaction_index = 0
        else:
            winner = team2[3:] + " wins"
            winner_icon = "https://twemoji.maxcdn.com/v/latest/72x72/32-20e3.png"
            winner_reaction_index = 1

        description = ""
        for map_played, map_score in scores.items():
            description += map_played + ": " + map_score
        
        # Send result embed
        result_embed = discord.Embed(title="**Match result**", color=0x2ecc71)
        result_embed.description = description
        result_embed.add_field(name=team1 + " ({0:+})".format(round_diff), value=team1_players, inline=True)
        result_embed.add_field(name=team2 + " ({0:+})".format(-round_diff), value=team2_players, inline=True)
        result_embed.set_footer(text=winner, icon_url=winner_icon)
        await match_message.reply(embed=result_embed)

        # Update predictions leaderboard for this channel
        correct_reactors = await match_message.reactions[winner_reaction_index].users().flatten()
        incorrect_reactors = await match_message.reactions[not winner_reaction_index].users().flatten()
        correct_reactors = [reactor for reactor in correct_reactors 
                            if reactor not in incorrect_reactors
                            and reactor.mention not in team1_players + team2_players]
        for user in correct_reactors:
            ldb.add_points(match_message.channel.id, user.id, 1)
        
        await match_message.reply(ldb.get_message(match_message.channel.id))

###############################################################################

# LEADERBOARD COMMAND    
@bot.command()
async def leaderboard(ctx, *args):
    args = list(args)
    if len(ctx.message.channel_mentions) == 0:
        leaderboard_channel_id = ctx.channel.id
    elif len(ctx.message.channel_mentions) == 1:
        leaderboard_channel_id = ctx.message.channel_mentions[0].id
        args.remove(ctx.message.channel_mentions[0].mention)
    else:
        await ctx.send("Error: expected 0 or 1 channel mentions")
        return
    if ctx.author.guild_permissions.manage_channels:
        if len(ctx.message.mentions) == 1:
            user = ctx.message.mentions[0]
            args.remove(user.mention)
        elif len(ctx.message.mentions) > 1:
            await ctx.send("Error: expected 0 or 1 user mentions")
            return
        if "add" in args:
            # This keyword can be used to add a new row, or add points to an
            # existing entry. See leaderboards.add_row for why (it's all done
            # in sqlite rather than python)
            args.remove("add")
            if args:
                points = args[-1]
            else:
                points = 0
            ldb.add_row(leaderboard_channel_id, user.id, points)
            await ctx.send("Added row: <#{}> <@{}> {}pts\n*If row existed, points were added to that row's points*".format(leaderboard_channel_id, user.id, points))
            return
        elif "del" in args:
            ldb.delete_row(leaderboard_channel_id, user.id)
            await ctx.send("Deleted row: <#{}> <@{}>".format(leaderboard_channel_id, user.id))
            return
        elif "set" in args:
            args.remove("set")
            points = args[-1]
            ldb.set_points(leaderboard_channel_id, user.id, points)
            await ctx.send("Set points: <#{}> <@{}> {}pts".format(leaderboard_channel_id, user.id, points))
            return
    await ctx.send(ldb.get_message(leaderboard_channel_id))


###############################################################################
###############################################################################

with open('bot_token.txt') as f:
    bot_token = f.read().strip()
bot.run(bot_token)

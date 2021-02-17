import discord
from discord import Role, User, Embed, Colour, Member, AllowedMentions
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
        await ctx.send("Error: `!result` must be sent as a reply to the match message.")
        return
    if len(args) % 2 or '-' in args[0]:
        await ctx.send("Error: please supply an even number of arguments (MAP/GAME and SCORE)")
        return

    match_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
    match_embed = match_message.embeds[0]
    team1 = match_embed.fields[0].name
    team1_players = match_embed.fields[0].value
    team2 = match_embed.fields[1].name
    team2_players = match_embed.fields[1].value

    embed = Embed(title="**Match Result**", description='', colour=Colour.green())

    maps_won = [0,0]
    round_diff = 0

    iterator = iter(args)  # trick for taking pairs from args
    for map_,score in zip(iterator, iterator):
        t1,t2 = map(int, score.split('-'))
        round_diff += t1 - t2

        t1_str = f"**{t1}**" if t1>=t2 else t1
        t2_str = f"**{t2}**" if t1<=t2 else t2
        embed.description += f"{map_}: {t1_str} - {t2_str}"

        maps_won[0] += t1>t2
        maps_won[1] += t1<t2
        if t1==t2:
            maps_won[0] += 1/2
            maps_won[1] += 1/2

    emotes = {
        1: "1\N{COMBINING ENCLOSING KEYCAP}",
        2: "2\N{COMBINING ENCLOSING KEYCAP}",
        None: "\N{INPUT SYMBOL FOR NUMBERS}",
    }

    if maps_won[0] > maps_won[1]:
        embed.set_footer(
            text=team1[3:] + " wins",
            icon_url="https://twemoji.maxcdn.com/v/latest/72x72/31-20e3.png",
        )
        winner = 1
    elif maps_won[1] > maps_won[0]:
        embed.set_footer(
            text=team2[3:] + " wins",
            icon_url="https://twemoji.maxcdn.com/v/latest/72x72/32-20e3.png",
        )
        winner = 2
    elif maps_won[0] == maps_won[1]:
        embed.set_footer(
            text="Match tied",
            icon_url="https://twemoji.maxcdn.com/v/latest/72x72/1f522.png",
        )
        winner = None

    embed.add_field(name=f"{team1} ({round_diff:+})", value=team1_players)
    embed.add_field(name=f"{team2} ({-round_diff:+})", value=team2_players)
    await match_message.reply(embed=embed)

    async def get_reactors(team):
        react = utils.get(match_message.reactions, emoji=emotes[team])
        if not react:
            return set()  # reaction not present
        return {user.id async for user in react.users() if not user.bot}

    winners = await get_reactors(winner)
    losers = set.union(*[await get_reactors(t) for t in emotes if t!=winner])
    players = team1_players + team2_players

    winners = {w for w in winners if w not in losers and w.mention not in players}

    for user in winners:
        ldb.add_points(match_message.channel.id, user.id, 1)

    await match_message.reply(ldb.get_message(match_message.channel.id),
                              allowed_mentions=AllowedMentions(users=list(winners+losers)))

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

import discord
from discord import Role, User, Embed, Colour, Member
from discord.ext import commands
from typing import Union
from modules import autodelete_functions, channelmap_functions, leaderboard_functions, utility_functions

# Enable the bot to see members roles etc
bot_intents = discord.Intents.default()
bot_intents.members = True

# Create a bot instance
bot = commands.Bot(command_prefix='!', intents=bot_intents)

@bot.event
async def on_ready():
    print("Connected as {}".format(bot.user))

###############################################################################
###############################################################################

# MODERATOR COMMANDS

# Channelmap    
@bot.command()
@commands.has_permissions(manage_channels=True)
async def channelmap(ctx, *args):
    mentioned_channels = ctx.message.raw_channel_mentions
    if len(args) == 0:
        channelmap_text = channelmap_functions.get_as_str()
        if channelmap_text == "":
            await ctx.send("`channelmap` is empty")
        else:
            await ctx.send(channelmap_text)
    elif args[0] == "-r" and len(mentioned_channels) == 1:
        channelmap_functions.remove(mentioned_channels[0])
        await ctx.send("Removed listening on {} from `channelmap`".format(mentioned_channels[0]))
    elif len(mentioned_channels) == 2:
        channelmap_functions.add(mentioned_channels[0], mentioned_channels[1])
        await ctx.send("Added to `channelmap`:\n Listen on {} -> Send on {}".format(mentioned_channels[0], mentioned_channels[1]))

# Autodelete
@bot.command()
@commands.has_permissions(manage_channels=True)
async def autodelete(ctx, *args):
    mentioned_channels = ctx.message.raw_channel_mentions
    if len(args) == 0:
        autodelete_text = autodelete_functions.get_as_str()
        if autodelete_text == "":
            await ctx.send("`autodelete` is empty")
        else:
            await ctx.send(autodelete_text)
    elif args[0] == "-r" and len(mentioned_channels) == 1:
        autodelete_functions.remove(mentioned_channels[0])
        await ctx.send("Removed {} from `autodelete`".format(mentioned_channels[0]))
    else:
        for channel in mentioned_channels:
            autodelete_functions.add(channel)
        await ctx.send("Added to `autodelete`:\n {}".format(mentioned_channels))


@bot.listen()
async def on_message(msg):
    if autodelete_functions.in_autodelete(msg.channel.id) and not msg.author.bot:
        await msg.delete(delay=10)


###############################################################################
###############################################################################

# MATCH COMMAND

@bot.command()
async def match(ctx, team1: Union[Role, Member, str], team2: Union[Role, Member, str], *, schedule_args=''):
    date = "Today"
    time = ''
    schedule_args = schedule_args.split()

    if len(schedule_args) == 1:  # only time provided
        time = schedule_args[0]
    elif len(schedule_args) == 2:  # Date and time provided
        date, time = schedule_args

    timestamp = date + (" at " + time if time else '')

    embed = Embed(title="**Match scheduled**", colour=Colour.gold())
    embed.set_footer(text=timestamp)

    for i,team in enumerate((team1, team2)):
        emoji = f'{i+1}\N{COMBINING ENCLOSING KEYCAP} '
        if isinstance(team, Member):
            embed.add_field(name=emoji, value=team.mention)
        elif isinstance(team, Role):
            embed.add_field(name=emoji+team.name, value='\n'.join(m.mention for m in team.members))
        else:
            embed.add_field(name=emoji+team, value='\u200b')

    send_channel = ctx.guild.get_channel(channelmap_functions.get_send_channel_id(ctx.channel.id))
    match_message = await send_channel.send(embed=embed)
    await match_message.add_reaction("1\N{COMBINING ENCLOSING KEYCAP}")
    await match_message.add_reaction("2\N{COMBINING ENCLOSING KEYCAP}")

###############################################################################

# RESULT COMMAND
@bot.command()
async def result(ctx, *args):
    if ctx.message.reference is None:
        await ctx.send("Error: `!result` must be sent as a reply to a message.")
        return
    elif len(args) % 2:
        await ctx.send("Error: please supply an even number of arguments (MAP and SCORE)")
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

        result_embed = discord.Embed(title="**Match result**", color=0x2ecc71)
        result_embed.description = description
        result_embed.add_field(name=team1 + " ({0:+})".format(round_diff), value=team1_players, inline=True)
        result_embed.add_field(name=team2 + " ({0:+})".format(-round_diff), value=team2_players, inline=True)
        result_embed.set_footer(text=winner, icon_url=winner_icon)
        await match_message.reply(embed=result_embed)

        correct_reactors = await match_message.reactions[winner_reaction_index].users().flatten()
        correct_reactors = [reactor.id for reactor in correct_reactors[1:]]
        # Remove the bot from the correct reactors
        leaderboard_functions.increment(correct_reactors)
        await match_message.reply(leaderboard_functions.get_as_str())

###############################################################################

# LEADERBOARD COMMAND    
@bot.command()
async def leaderboard(ctx, *args):
    if ctx.author.guild_permissions.manage_channels:
        mentions = ctx.message.mentions
        if len(mentions) == 1:
            if args[0] == "-s" and len(args) == 3:
                leaderboard_functions.set_user_score(mentions[0].id, args[2])
                await ctx.send("Set {}'s score to {}".format(mentions[0], args[2]))
            elif args[0] == "-a":
                if len(args) == 3:
                    leaderboard_functions.add_user(mentions[0].id, args[2])
                    await ctx.send("Added {} with score {}".format(mentions[0], args[2]))
                elif len(args) == 2:
                    leaderboard_functions.add_user(mentions[0].id)
                    await ctx.send("Added {} with score 0".format(mentions[0]))
    await ctx.send(leaderboard_functions.get_as_str())


###############################################################################
###############################################################################

utility_functions.run(bot)

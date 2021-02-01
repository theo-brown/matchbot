"""
EVL Discord Bot template by Theo Brown
Licensed under GNU GPLv3
https://github.com/theo-brown/EVL-bot-template
"""
from discord import Embed

help_message = \
"""
`!result`: used in the reply to a message created with `!match` to reflect the score of the match
Syntax: `!result MAPNAME1 SCORELINE1 [MAPNAME2 SCORELINE2 MAPNAME 3 SCORELINE 3 etc]`
MAPNAME should contain no spaces
SCORELINE should be in the form #-#, with the score of team :one: first
"""

from operator import itemgetter

leaderboard = {}


def leaderboard_update(userlist):
    for user in userlist:
        if user in leaderboard.keys():
            leaderboard[user] += 1
        else:
            leaderboard[user] = 1


def leaderboard_generate_text():
    # Create a list of tuples in the form (user, score), ordered from high to low score
    leaderboard_list = sorted(leaderboard.items(), key=itemgetter(1), reverse=True)
    positions = [1]*len(leaderboard_list)
    for i in range(len(leaderboard_list)-1):
        if leaderboard_list[i+1][1] == leaderboard_list[i][1]:
            positions[i+1] = positions[i]
        else:
            positions[i+1] = positions[i] + 1
    leaderboard_text = "**Pick'em Leaderboard:**\n```\n"
    for i, v in enumerate(leaderboard_list):
        leaderboard_text += "{}. {}\t\t({}pts)\n".format(positions[i], v[0], v[1])
    leaderboard_text += "```"
    return leaderboard_text


async def run(message, args, kwargs):
    if message.reference is None:
        await message.channel.send("Error: `!result` must be sent as a reply to a message.")
        return
    elif len(args) % 2:
        await message.channel.send("Error: please supply an even number of arguments (MAP and SCORE)")
        return
    else:
        match_message = await message.channel.fetch_message(message.reference.message_id)
        match_embed = match_message.embeds[0]
        team1 = match_embed.fields[0].name
        team1_players = match_embed.fields[0].value
        team2 = match_embed.fields[1].name
        team2_players = match_embed.fields[1].value
        
        scores = {}
        for i in range(len(args) // 2):
            map_i = args[2*i]
            score_i = args[2*i+1]
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
        
        result_embed = Embed(title="**Match result**", color=0x2ecc71)
        result_embed.description = description
        result_embed.add_field(name=team1 + " ({0:+})".format(round_diff), value=team1_players, inline=True)
        result_embed.add_field(name=team2 + " ({0:+})".format(-round_diff), value=team2_players, inline=True)
        result_embed.set_footer(text=winner, icon_url=winner_icon)
        await match_message.reply(embed=result_embed)
        
        correct_reactors = await match_message.reactions[winner_reaction_index].users().flatten()
        # Remove the bot from the correct reactors
        leaderboard_update(correct_reactors[1:])
        await match_message.reply(leaderboard_generate_text())
        
async def help(message, args, kwargs):
    await message.channel.send(help_message)
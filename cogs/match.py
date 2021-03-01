from typing import Union
from discord import Embed, Role, Member, Colour, utils, AllowedMentions
from discord.ext.commands import *

from . import Cog
import parsing
import sql.channels, sql.leaderboards


class MatchCog(Cog, name='Match commands'):
    @command()
    async def match(self, ctx, team1: Union[Role, Member], team2: Union[Role, Member],
                    *schedule_args):
        "Schedule a match between two teams."
        schedule_args = " ".join(schedule_args)
        # Parse schedule string
        datetime_obj, datetime_str = parsing.parse_date(schedule_args)
        embed = Embed(title="**Match scheduled**", colour=Colour.gold())
        embed.set_footer(text=datetime_str)

        for i, team in enumerate((team1, team2)):
            emoji = f'{i+1}\N{COMBINING ENCLOSING KEYCAP} '
            if isinstance(team, Member):
                embed.add_field(name=emoji, value=team.mention)
            elif isinstance(team, Role):
                embed.add_field(name=emoji + team.name,
                                value='\n'.join(m.mention for m in team.members))
            else:
                await ctx.send(f"Error: teams must be mentioned by role or user "
                               f"({team} is {type(team)}")
                return

        send_channel = ctx.guild.get_channel(sql.channels.get_redirect_channel(ctx.channel.id))
        match_message = await send_channel.send(embed=embed)
        await match_message.add_reaction("1\N{COMBINING ENCLOSING KEYCAP}")
        await match_message.add_reaction("2\N{COMBINING ENCLOSING KEYCAP}")


    @command()
    async def result(self, ctx, *args):
        "Register a match result."
        args = list(args)  # we need args to be mutable to be able to remove the team names
        if len(args) == 0:
            await ctx.send("Error: `!result` expects arguments: either scores only "
                           "(e.g. `16-10 15-16 etc`), or maps/games and scores "
                           "e.g. `Map1 16-10 etc`)")
            return
        match_message = None
        teams, players = ['', ''], ['', '']
        if ctx.message.reference is not None:
            match_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            send_result_message = match_message.reply
            match_embed = match_message.embeds[0]
            teams = [match_embed.fields[0].name, match_embed.fields[1].name]
            players = [match_embed.fields[0].value, match_embed.fields[1].value]
        else:
            send_channel = ctx.guild.get_channel(sql.channels.get_redirect_channel(ctx.channel.id))
            send_result_message = send_channel.send
            mentions = parsing.get_all_mentions_in_order(ctx, args)
            if len(mentions) != 2:
                await ctx.send("Error: `!result` must be either sent in reply to a"
                               " `!match` message, or include mentions of two teams"
                               " (users or roles)")
                return
            for i, team in enumerate(mentions):
                emoji = f'{i + 1}\N{COMBINING ENCLOSING KEYCAP} '
                if isinstance(team, Member):
                    teams[i] = emoji
                    players[i] = team.mention
                elif isinstance(team, Role):
                    teams[i] = emoji + team.name
                    players[i] = '\n'.join(m.mention for m in team.members)
                else:
                    await ctx.send(f"Error: teams must be mentioned by role or user "
                                   f"({team} is {type(team)}")
                    return

        result_dict, result_str = parsing.parse_results(' '.join(args))

        round_diff = 0
        games_won = [0, 0, 0]  # Tiess, team 1 wins, team 2 wins
        for r in result_dict:
            round_diff += r['score'][0] - r['score'][1]
            games_won[r['winner']] += 1  # r['winner'] is 0 if tie, 1 if t1, 2 if t2

        if games_won[1] > games_won[2]:
            winner_emote = "1\N{COMBINING ENCLOSING KEYCAP}"
            loser_emote = "2\N{COMBINING ENCLOSING KEYCAP}"
            if teams[0] == "1\N{COMBINING ENCLOSING KEYCAP} ":
                winner_user_id = parsing.convert_mention_into_id(players[0])
                winner_user = self.bot.get_user(winner_user_id)
                footertext = winner_user.display_name + " wins"
            else:
                footertext = teams[0][3:] + " wins"
            footericon = "https://twemoji.maxcdn.com/v/latest/72x72/31-20e3.png"
        elif games_won[2] > games_won[1]:
            winner_emote = "2\N{COMBINING ENCLOSING KEYCAP}"
            loser_emote = "1\N{COMBINING ENCLOSING KEYCAP}"
            if teams[1] == "2\N{COMBINING ENCLOSING KEYCAP} ":
                winner_user_id = parsing.convert_mention_into_id(players[1])
                winner_user = self.bot.get_user(winner_user_id)
                footertext = winner_user.display_name + " wins"
            else:
                footertext = teams[1][3:] + " wins"
            footericon = "https://twemoji.maxcdn.com/v/latest/72x72/32-20e3.png"
        elif games_won[1] == games_won[2]:
            winner_emote, loser_emote = None, None
            footertext = "Match tied"
            footericon = "https://twemoji.maxcdn.com/v/latest/72x72/1faa2.png"

        result_embed = Embed(title="**Match Result**", description='', colour=Colour.green())
        result_embed.description = result_str
        result_embed.add_field(name=f"{teams[0]} ({round_diff:+})",
                               value=players[0])  # Round diff is (team 1 score - team 2 score)
        result_embed.add_field(name=f"{teams[1]} ({-round_diff:+})", value=players[1])
        result_embed.set_footer(text=footertext, icon_url=footericon)
        await send_result_message(embed=result_embed)

        # If there's a winner, award points to users that made correct predictions
        if winner_emote is not None and match_message is not None:
            # 'correct' is a set of users that reacted with the emote of the winner
            # 'incorrect' is a set of users that reacted with the emote of the loser
            correct, incorrect = set(), set()
            for emote, users in zip((winner_emote, loser_emote),
                                    (correct, incorrect)):
                # Get the reaction object of this emote
                reaction = utils.get(match_message.reactions, emoji=emote)
                # Iterate through everyone who used this emote
                async for user in reaction.users():
                    # Exclude anyone involved in this match
                    if user.mention not in players[0] + players[1]:
                        users.add(user)

            all_reactors = set().union(correct, incorrect)
            correct = correct - incorrect  # Exclude users that also reacted incorrectly

            if bool(all_reactors):  # If there's somebody who reacted with one of the winner/loser emotes
                correct_ids = [user.id for user in correct]
                sql.leaderboards.increment(match_message.channel.id, *correct_ids)

                # Anyone who voted will be mentioned
                await match_message.reply(sql.leaderboards.get_message(match_message.channel.id),
                                          allowed_mentions=AllowedMentions(users=list(all_reactors)))

def setup(bot):
    bot.add_cog(MatchCog(bot))

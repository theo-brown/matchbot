from typing import Union
from discord import Role, Member
from discord.ext.commands import *

from . import Cog
from classes import Map, Team
import menus
import parsing


class LobbyCog(Cog):
    @command()
    async def veto(self, ctx: Context, team1: Union[Role, Member], team2: Union[Role, Member]):
        map_pool = [Map('Cobblestone', 'de_cbble'),
                    Map('Inferno', 'de_inferno'),
                    Map('Nuke', 'de_nuke'),
                    Map('Overpass', 'de_overpass'),
                    Map('Shortdust', 'de_shortdust'),
                    Map('Train', 'de_train'),
                    Map('Vertigo', 'de_vertigo')]
        team1 = Team(team1)
        team2 = Team(team2)
        embed = menus.VetoMenu(team1, team2, map_pool)
        await embed.send(ctx)
        while embed.remaining_options:
            reaction, user = await self.bot.wait_for('reaction_add', check=embed.check_reaction)
            await embed.on_reaction(reaction, user)

    @command()
    async def teams(self, ctx, captain1: Member, captain2: Member, *players):
        players_users = []
        for player in players:
            if isinstance(player, Member):
                players_users.append(player)
            else:
                userid = parsing.convert_mention_into_id(player)
                user = self.bot.get_user(userid)
                players_users.append(user)

        embed = menus.PickTeamsMenu(captain1, captain2, players_users)
        await embed.send(ctx)
        while embed.remaining_options:
            reaction, user = await self.bot.wait_for('reaction_add', check=embed.check_reaction)
            await embed.on_reaction(reaction, user)

def setup(bot):
    bot.add_cog(LobbyCog(bot))

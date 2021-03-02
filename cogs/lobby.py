from typing import Union
from discord import Role, Member
import get5.commands
import discord.ext.commands as cmds

from . import Cog
from classes import Map, Team
import menus
import parsing


class LobbyCog(Cog, name='Pick/ban commands'):
    @cmds.command()
    async def veto(self, ctx: cmds.Context, team1: Union[Role, Member, Team], team2: Union[Role, Member, Team], mode=''):
        """Start a veto between two teams."""
        if mode == 'wingman':
            map_pool = [Map('Cobblestone', 'de_cbble'),
                        Map('Inferno', 'de_inferno'),
                        Map('Nuke', 'de_nuke'),
                        Map('Overpass', 'de_overpass'),
                        Map('Shortdust', 'de_shortdust'),
                        Map('Train', 'de_train'),
                        Map('Vertigo', 'de_vertigo')]
        else:
            map_pool = [Map('Dust 2', 'de_dust2'),
                        Map('Inferno', 'de_inferno'),
                        Map('Mirage', 'de_mirage'),
                        Map('Nuke', 'de_nuke'),
                        Map('Overpass', 'de_overpass'),
                        Map('Train', 'de_train'),
                        Map('Vertigo', 'de_vertigo')]
        teams = []
        for i, team in enumerate([team1, team2]):
            if not isinstance(team, Team):
                teams.append(Team(team))
            else:
                teams.append(team)
        embed = menus.VetoMenu(teams[0], teams[1], map_pool)
        await embed.send(ctx)
        while embed.remaining_options:
            reaction, user = await self.bot.wait_for('reaction_add', check=embed.check_reaction)
            await embed.on_reaction(reaction, user)

    @cmds.command()
    async def teams(self, ctx, captain1: Member, captain2: Member, *players):
        """Start a team pick with two captains."""
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

        await self.veto(ctx, embed.teams[0], embed.teams[1])

def setup(bot):
    bot.add_cog(LobbyCog(bot))

from typing import Union
from discord import Role, Member
import get5.commands
import discord.ext.commands as cmds
from os import getenv
from . import Cog
from classes import Map, Team
import menus
import parsing

wingman_map_pool = [Map('Cobblestone', 'de_cbble'),
                    Map('Inferno', 'de_inferno'),
                    Map('Nuke', 'de_nuke'),
                    Map('Overpass', 'de_overpass'),
                    Map('Shortdust', 'de_shortdust'),
                    Map('Train', 'de_train'),
                    Map('Vertigo', 'de_vertigo')]

active_duty_map_pool = [Map('Dust 2', 'de_dust2'),
                        Map('Inferno', 'de_inferno'),
                        Map('Mirage', 'de_mirage'),
                        Map('Nuke', 'de_nuke'),
                        Map('Overpass', 'de_overpass'),
                        Map('Train', 'de_train'),
                        Map('Vertigo', 'de_vertigo')]

class LobbyCog(Cog, name='Pick/ban commands'):
    @cmds.command()
    async def veto(self, ctx: cmds.Context, team1: Union[Role, Member, Team], team2: Union[Role, Member, Team], mode=''):
        """Start a veto between two teams."""
        if mode == 'wingman':
            map_pool = wingman_map_pool
        else:
            map_pool = active_duty_map_pool
        teams = []
        for i, team in enumerate([team1, team2]):
            if not isinstance(team, Team):
                teams.append(Team(team))
            else:
                teams.append(team)
        if mode == 'bo1':
            bestof = 1
        else:
            bestof = 3
        veto_menu = menus.VetoMenu(self.bot, teams[0], teams[1], map_pool, bestof=bestof)
        await veto_menu.run(ctx)

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

        teams_menu = menus.PickTeamsMenu(self.bot, captain1, captain2, players_users)
        await teams_menu.run(ctx)

    @cmds.command()
    async def startmatch(self, ctx):
        ip = getenv('CSGO_SERVER_IP')
        port = getenv('CSGO_SERVER_PORT')
        password = getenv('CSGO_SERVER_PASSWORD')
        rcon_password = getenv('CSGO_SERVER_RCON_PASSWORD')

        get5.commands.rcon("get5_endmatch", ip, port, rcon_password) # End any existing match
        get5.commands.send_rcon_loadmatch(ip, port, rcon_password) # Send rcon command to trigger new match setup

        connect_str = f"`connect {ip}:{port}; password {password}`"
        await ctx.send(connect_str)

def setup(bot):
    bot.add_cog(LobbyCog(bot))

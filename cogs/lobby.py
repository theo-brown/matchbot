from typing import Union
from discord import Role, Member, Embed
import get5.commands
import discord.ext.commands as cmds
from os import getenv
from cogs import Cog
from classes import Map, Team
import menus


wingman_map_pool = [Map('Cobblestone', 'de_cbble'),
                    Map('Inferno', 'de_inferno'),
                    Map('Nuke', 'de_shortnuke'),
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
    active_lobby = None
    
    @cmds.command()
    async def lobby(self, ctx):
        """Start a new 5v5 lobby"""
        if self.active_lobby is None:
            self.active_lobby = menus.Lobby(self.bot)
            await self.active_lobby.run(ctx)
        else:
            await self.active_lobby.rerun(ctx)
        await self.active_lobby.message.delete()
        teams_menu = menus.PickTeamsMenu(self.bot, self.active_lobby.captains[0], self.active_lobby.captains[1], self.active_lobby.players)
        await teams_menu.run(ctx)
        await teams_menu.message.delete()
        await self.veto(ctx, teams_menu.teams[0], teams_menu.teams[1], gametype='5v5_bo1')
        self.active_lobby = None
    
    @cmds.command()
    async def veto(self, ctx: cmds.Context, team1: Union[Role, Member, Team], team2: Union[Role, Member, Team], gametype='2v2_bo3'):
        """Start a veto between two teams."""
        if '2v2' in gametype:
            map_pool = wingman_map_pool
        else:
            map_pool = active_duty_map_pool
        teams = []
        for i, team in enumerate([team1, team2]):
            if not isinstance(team, Team):
                teams.append(Team(team))
            else:
                teams.append(team)
        veto_menu = menus.VetoMenu(self.bot, teams[0], teams[1], map_pool, gametype)
        await veto_menu.run(ctx)
        await self.startmatch(ctx)


    @cmds.command()
    async def startmatch(self, ctx):
        ip = getenv('CSGO_SERVER_IP')
        port = getenv('CSGO_SERVER_PORT')
        gotv_port = getenv('CSGO_SERVER_GOTV_PORT')
        password = getenv('CSGO_SERVER_PASSWORD')
        rcon_password = getenv('CSGO_SERVER_RCON_PASSWORD')

        # Send rcon command to end existing match and trigger new match setup
        await get5.commands.force_loadmatch(ip, port, rcon_password)

        startmatch_embed = Embed(title="Server ready",
                                 description=(f"Play: \n```connect {ip}:{port}; password {password}```\n"
                                              f"Watch on GOTV: \n```connect {ip}:{gotv_port}```"))
        await ctx.send(embed=startmatch_embed)

def setup(bot):
    bot.add_cog(LobbyCog(bot))

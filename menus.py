from discord import Embed, Role, Member
from typing import Union, Iterable
from classes import Team, Map


class BasicMenu:
    def __init__(self, title="", pre_options="", options=[], 
                 post_options="", fields={}, inline_fields=False, footer=""):
        self.title = title
        self.pre_options = pre_options
        self.options = options
        self.remaining_options = self.options[:]
        self.post_options = post_options
        self.fields = fields
        self.inline_fields = inline_fields
        self.footer = footer
        self.embed = Embed()
        self.message = None
        self.generate_emoji()
        self.update_contents()
    
    def set_title(self, title: str):
        self.title = title
        self.update_contents()
        
    def set_pre_options(self, pre_options: str):
        self.pre_options = pre_options
        self.update_contents()
        
    def set_options(self, options: list):
        self.options = options
        self.remaining_options = options[:]
        self.generate_emoji()
        self.update_contents()
  
    def set_post_options(self, post_options: str):
        self.post_options = post_options
        self.update_contents()
        
    def set_fields(self, fields: dict, inline_fields=None):
        self.fields = fields
        if inline_fields is not None:
            self.inline_fields = inline_fields
        self.update_contents()            

    def set_footer(self, footer: str):
        self.footer = footer
        self.update_contents()
    
    def generate_emoji(self):
        self.emoji_to_option = {f"{i+1}\N{COMBINING ENCLOSING KEYCAP}": option 
                                for i, option in enumerate(self.options)}
        self.option_to_emoji = {option: emoji 
                                for emoji, option in self.emoji_to_option.items()}
        self.emoji = list(self.emoji_to_option.keys())
        
    def get_emoji(self, option):
        return self.option_to_emoji[option]
    
    def get_option(self, emoji):
        return self.emoji_to_option[emoji]
    
    def get_all_emoji(self):
        all_emoji = []
        for option in self.options:
            all_emoji.append(self.get_emoji(option))
        return all_emoji
    
    def get_remaining_emoji(self):
        remaining_emoji = []
        for option in self.remaining_options:
            remaining_emoji.append(self.get_emoji(option))
        return remaining_emoji
    
    def update_contents(self):
        options_str = ""
        for option in self.remaining_options:
            options_str += f"{self.get_emoji(option)} {option}\n"
        if options_str:
            options_str += "\n"
        self.embed.title = self.title
        self.embed.description = (self.pre_options + "\n\n"
                                  + options_str
                                  + self.post_options)
        self.embed.set_footer(text=self.footer)
        
        self.embed.clear_fields()
        for name, value in self.fields.items():
            self.embed.add_field(name=name, value=value, inline=self.inline_fields)
    
    async def add_all_reactions(self):
        for emoji in self.get_all_emoji():
            await self.message.add_reaction(emoji)
            
    async def update_message(self):
        self.update_contents()
        await self.message.edit(embed=self.embed)
        
    async def send(self, ctx):
        self.message = await ctx.send(embed=self.embed)
        await self.add_all_reactions()
        
    def check_reaction(self, reaction, user):
        return (reaction.message == self.message
                and not user.bot
                and str(reaction.emoji) in self.get_remaining_emoji())

    async def on_reaction(self, reaction, user):
        emoji = str(reaction.emoji)
        selected_option = self.get_option(emoji)
        self.post_options += f"{user.mention} chose {self.selected_option}\n"
        self.remaining_options.remove(selected_option)
        await self.message.clear_reaction(emoji)
        await self.update_message()


class PickTeamsMenu(BasicMenu):
    def __init__(self, captain1: Member, captain2: Member,
                 players: Iterable[Member]):
        self.captains = [captain1, captain2]
        self.teams = [Team(captain=captain1), Team(captain=captain2)]
        self.players = {player.mention: player for player in players}
        self.active_captain = captain1
        
        self.title = "**Pick Teams**"
        self.pre_options = ("**Captains:** \n"
                            f"{self.captains[0].mention}\n"
                            f"{self.captains[1].mention}")
        self.options = list(self.players.keys())                
        self.remaining_options = self.options[:]
        self.post_options = ""
        self.fields = {self.teams[0].name: self.teams[0].display(),
                       self.teams[1].name: self.teams[1].display()}
        self.inline_fields = True
        self.footer = ""
        self.embed = Embed()
        self.message = None
        
        self.generate_emoji()
        self.update_contents()

    async def send(self, ctx):
        self.message = await ctx.send(embed=self.embed)
        await self.add_all_reactions()
        self.set_footer(f"{self.active_captain.display_name} to pick")
        await self.update_message()
    
    def next_captain(self):
        for captain in self.captains:
            if captain != self.active_captain:
                return captain
    
    def update_fields(self):
        self.fields = {self.teams[0].name: self.teams[0].display(),
                       self.teams[1].name: self.teams[1].display()}
    
    def update_footer(self):
        if self.remaining_options:
            self.footer = f"{self.active_captain.display_name} to pick"
        else:
            self.footer = ""
    
    def check_reaction(self, reaction, user):
        return (reaction.message == self.message
                and user == self.active_captain
                and str(reaction.emoji) in self.get_remaining_emoji())

    async def on_reaction(self, reaction, user):
        emoji = str(reaction.emoji)
        selected_option = self.get_option(emoji)
        self.remaining_options.remove(selected_option)
        self.post_options += f"*{user.mention} picked {selected_option}*\n"
        await self.message.clear_reaction(emoji)
        selected_user = self.players[selected_option]
        for team in self.teams:
            if team.captain == self.active_captain:
                team.add_player(selected_user)
        self.active_captain = self.next_captain()
        self.update_fields()
        self.update_footer()
        await self.update_message()


class VetoMenu(BasicMenu):
    def __init__(self, team1: Team, team2: Team, maps: Iterable[Map], bestof=3):
        self.teams = [team1, team2]
        self.maps = maps
        self.active_team = self.teams[0]
        self.chosen_maps = []
        
        bo1_veto = ['ban', 'ban', 'ban', 'ban', 'ban', 'ban']
        bo3_veto = ['ban', 'ban', 'pick', 'pick', 'ban', 'ban']
        
        if bestof == 1:
            self.veto = bo1_veto
        elif bestof == 3:
            self.veto = bo3_veto
        
        self.mode = self.next_mode()
        
        self.title = "**Match Veto**"
        self.pre_options = f"{self.teams[0].mention} vs {self.teams[1].mention}"
        self.options = [m.readable_name for m in self.maps]
        self.remaining_options = self.options[:]
        self.post_options = ""
        self.fields = {}
        self.inline_fields = False
        self.footer = ""
        self.embed = Embed()
        self.message = None
                
        self.generate_emoji()
        self.update_contents()
    
    async def send(self, ctx):
        self.message = await ctx.send(embed=self.embed)
        await self.add_all_reactions()
        self.set_footer(f"{self.active_team.name} to {self.mode}")
        await self.update_message()
        
    def next_team(self):
        for team in self.teams:
            if team != self.active_team:
                return team
            
    def next_mode(self):
        return self.veto.pop(0)
        
    def update_fields(self):
        self.fields = {}
        for i, chosen_map in enumerate(self.chosen_maps):
            if chosen_map.pickedby is not None:
                self.fields[f"Map {i+1}: {chosen_map.readable_name}"] = f"*Picked by {chosen_map.pickedby.name}*"
            else:
                self.fields[f"Map {i+1}: {chosen_map.readable_name}"] = "\u200b"
    
    def update_footer(self):
        if self.remaining_options:
            if self.mode == 'pick':
                self.footer = f"{self.active_team.name} to pick"
            elif self.mode == 'ban':
                self.footer = f"{self.active_team.name} to ban"
        else:
            self.footer = ""
    
    def get_map_from_name(self, readable_name):
        for m in self.maps:
            if m.readable_name == readable_name:
                return m
    
    def check_reaction(self, reaction, user):
        return (reaction.message == self.message
                and user in self.active_team.players
                and str(reaction.emoji) in self.get_remaining_emoji())

    async def on_reaction(self, reaction, user):
        emoji = str(reaction.emoji)
        await self.message.clear_reaction(emoji)
        selected_mapname = self.get_option(emoji)
        self.remaining_options.remove(selected_mapname)
        selected_map = self.get_map_from_name(selected_mapname)

        if self.mode == 'pick':
            self.post_options += f"*{self.active_team.name} picked {selected_mapname}*\n"
            selected_map.pick(self.active_team)
            self.chosen_maps.append(selected_map)
        elif self.mode == 'ban':
            self.post_options += f"*{self.active_team.name} banned {selected_mapname}*\n"

        if len(self.remaining_options) == 1:
            finalmap_name = self.remaining_options.pop()
            await self.message.clear_reaction(self.get_emoji(finalmap_name))
            finalmap = self.get_map_from_name(finalmap_name)
            self.chosen_maps.append(finalmap)
            self.post_options += f"{finalmap_name} was left over\n"
        
        self.active_team = self.next_team()
        if self.veto:
            self.mode = self.next_mode()
        self.update_fields()
        self.update_footer()
        await self.update_message()

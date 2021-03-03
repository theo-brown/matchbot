from discord import Embed, Role, Member
from typing import Union, Iterable
from classes import Team, Map
import get5.commands

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

    async def add_remaining_reactions(self):
        for emoji in self.get_remaining_emoji():
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
        self.teams = [Team(captain1), Team(captain2)]
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
        bo3_veto = ['ban', 'ban', 'pick', 'pick', 'ban', 'ban', 'sides', 'sides']
        
        if bestof == 1:
            self.veto = bo1_veto
            self.starting_sides = ['knife']
        elif bestof == 3:
            self.veto = bo3_veto
            self.starting_sides = []
        
        self.mode = self.next_mode()
        
        self.title = "**Map Veto**"
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
                name = f"Map {i+1}: {chosen_map.readable_name}"
                value = f"Pick: {chosen_map.pickedby.name}"
                for side, team in chosen_map.sides.items():
                    if team is not None:
                        value += f"\n{team.name} starting as {side.upper()}"
                self.fields[name] = value
            else:
                self.fields[f"Map {i+1}: {chosen_map.readable_name}"] = "Knife for sides"
    
    def update_footer(self):
        if self.remaining_options:
            if self.mode == 'pick':
                self.footer = f"{self.active_team.name} to pick"
            elif self.mode == 'ban':
                self.footer = f"{self.active_team.name} to ban"
            elif self.mode == 'sides':
                self.footer = (f"{self.active_team.name} to choose starting side "
                               f"({self.get_other_teams_map_pick().readable_name})")
        else:
            self.footer = ""
    
    def get_map_from_name(self, readable_name):
        for m in self.maps:
            if m.readable_name == readable_name:
                return m

    def get_other_teams_map_pick(self):
        for m in self.maps:
            if m.pickedby != self.active_team and m.pickedby is not None:
                return m

    async def setup_pick_sides(self):
        self.options = ["Counter-terrorists", "Terrorists"]
        self.remaining_options = self.options[:]
        self.generate_sides_emoji()
        self.update_footer()
        await self.message.clear_reactions()
        await self.add_all_reactions()
        await self.update_message()

    def generate_sides_emoji(self):
        self.emoji_to_option = {"\N{REGIONAL INDICATOR SYMBOL LETTER T}": "Terrorists",
                                "\N{REGIONAL INDICATOR SYMBOL LETTER C}": "Counter-terrorists"}
        self.option_to_emoji = {option: emoji
                                for emoji, option in self.emoji_to_option.items()}
        self.emoji = list(self.emoji_to_option.keys())

    def check_reaction(self, reaction, user):
        return (reaction.message == self.message
                and user in self.active_team.players
                and str(reaction.emoji) in self.get_remaining_emoji())

    async def on_reaction(self, reaction, user):
        emoji = str(reaction.emoji)
        await self.message.clear_reaction(emoji)
        selected_option = self.get_option(emoji)
        self.remaining_options.remove(selected_option)

        if self.mode == 'pick':
            self.post_options += f"*{self.active_team.name} picked {selected_option}*\n"
            selected_map = self.get_map_from_name(selected_option)
            selected_map.pick(self.active_team)
            self.chosen_maps.append(selected_map)
        elif self.mode == 'ban':
            self.post_options += f"*{self.active_team.name} banned {selected_option}*\n"
        elif self.mode == 'sides':
            other_teams_map = self.get_other_teams_map_pick()
            other_teams_map.choose_side(self.active_team, selected_option)
            self.post_options += f"*{self.active_team.name} chose to start as {selected_option} on {other_teams_map.readable_name}*\n"

        if len(self.remaining_options) == 1:
            final_option = self.remaining_options.pop()
            await self.message.clear_reaction(self.get_emoji(final_option))
            if not self.mode == 'sides':
                finalmap = self.get_map_from_name(final_option)
                self.chosen_maps.append(finalmap)
                self.post_options += f"*{final_option} was left over*\n"
                self.active_team = self.next_team() # Need this so that the active team changes to the second team

        self.active_team = self.next_team()
        if self.veto:
            self.mode = self.next_mode()
            if self.mode == 'sides':
                await self.setup_pick_sides()
        else:
            self.mode = ''
            self.config = await get5.commands.generate_config(self.teams[0], self.teams[1], self.chosen_maps)

        self.update_fields()
        self.update_footer()
        await self.update_message()

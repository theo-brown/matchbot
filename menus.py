from discord import Embed, Role, Member
from typing import Union, Iterable
from classes import Team, Map
import get5.commands
import asyncio


class SelectMenu:
    def __init__(self, bot, title="", pre_options="", options=[], post_options="",
                 fields={}, inline_fields=False, footer=""):
        self.bot = bot
        self.finished = False
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
        return [self.get_emoji(option) for option in self.options]
    
    def get_remaining_emoji(self):
        return [self.get_emoji(option) for option in self.remaining_options]

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
        await self.add_remaining_reactions()

    async def run(self, ctx):
        self.message = await ctx.send(embed=self.embed)
        await self.update_message()
        self.finished = False
        while not self.finished:
            await self.process_reactions()

    async def process_reactions(self):
        reaction, user = await self.bot.wait_for('reaction_add', check=self.check_reaction)
        await self.on_reaction(reaction, user)

    def check_reaction(self, reaction, user):
        return (reaction.message == self.message
                and not user.bot
                and str(reaction.emoji) in self.get_remaining_emoji())

    async def on_reaction(self, reaction, user):
        emoji = str(reaction.emoji)
        selected_option = self.get_option(emoji)
        self.post_options += f"{user.mention} chose {selected_option}\n"
        self.remaining_options.remove(selected_option)
        if len(self.remaining_options) == 0:
            self.finished = True
        await self.update_message()
        await self.message.clear_reaction(emoji)


class PickTeamsMenu(SelectMenu):
    def __init__(self, bot, captain1: Member, captain2: Member, players: Iterable[Member]):
        self.bot = bot
        self.captains = [captain1, captain2]
        self.teams = [Team(captain1), Team(captain2)]
        self.active_captain = self.captains[0]
        self.finished = False
        self.players = {player.mention: player for player in players if player not in self.captains}

        self.title = "Pick Teams"
        self.pre_options = ("**Captains:** \n"
                            f"{self.captains[0].mention}\n"
                            f"{self.captains[1].mention}\n")
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

    def next_captain(self):
        for captain in self.captains:
            if captain != self.active_captain:
                return captain

    def update_fields(self):
        self.fields = {self.teams[0].name: self.teams[0].display(),
                       self.teams[1].name: self.teams[1].display()}

    def update_preoptions(self):
        self.pre_options = ("**Captains:** \n"
                            f"{self.captains[0].mention}\n"
                            f"{self.captains[1].mention}\n")
        if self.remaining_options:
            self.pre_options += f"\n{self.active_captain.mention} **to pick**"

    async def run(self, ctx):
        self.message = await ctx.send(embed=self.embed)
        await self.add_all_reactions()
        self.update_preoptions()
        await self.update_message()
        self.finished = False
        while not self.finished and self.remaining_options:
            await self.process_reactions()

    def check_reaction(self, reaction, user):
        return (reaction.message == self.message
                and user == self.active_captain
                and str(reaction.emoji) in self.get_remaining_emoji())

    async def on_reaction(self, reaction, user):
        emoji = str(reaction.emoji)
        selected_option = self.get_option(emoji)
        selected_user = self.players[selected_option]
        for team in self.teams:
            if team.captain == self.active_captain:
                team.add_player(selected_user)
        self.post_options += f"{user.mention} picked {selected_option}\n"
        self.remaining_options.remove(selected_option)
        self.active_captain = self.next_captain()
        self.update_fields()
        self.update_preoptions()
        if len(self.remaining_options) == 0:
            self.finished = True
        await self.message.clear_reaction(emoji)
        await self.update_message()


class VetoMenu(SelectMenu):
    def __init__(self, bot, team1: Team, team2: Team, maps: Iterable[Map], gametype):
        self.bot = bot
        self.teams = [team1, team2]
        self.maps = maps
        self.gametype = gametype
        self.active_team = self.teams[0]
        self.chosen_maps = []

        bo1_veto = ['ban', 'ban', 'ban', 'ban', 'ban', 'ban']
        bo3_veto = ['ban', 'ban', 'pick', 'pick', 'ban', 'ban', 'sides', 'sides']
        
        if 'bo1' in self.gametype:
            self.veto = bo1_veto
            self.starting_sides = ['knife']
        elif 'bo3' in self.gametype:
            self.veto = bo3_veto
            self.starting_sides = []
        
        self.mode = self.next_mode() # Get the first mode

        self.title = "Map Veto"
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

    async def run(self, ctx):
        self.message = await ctx.send(embed=self.embed)
        self.update_preoptions()
        await self.update_message()
        self.finished = False
        while not self.finished:
            await self.process_reactions()
        await self.message.clear_reactions()

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

    def update_preoptions(self):
        self.pre_options = f"{self.teams[0].mention} vs {self.teams[1].mention}"
        if self.remaining_options:
            if self.mode == 'pick':
                self.pre_options += f"\n\n{self.active_team.mention} **to pick**"
            elif self.mode == 'ban':
                self.pre_options += f"\n\n{self.active_team.mention} **to ban**"
            elif self.mode == 'sides':
                self.pre_options += f"\n\n{self.active_team.mention} **to choose starting side ({self.get_opponents_map_pick().readable_name})**"

    def get_map_from_name(self, readable_name):
        for m in self.maps:
            if m.readable_name == readable_name:
                return m

    def get_inactive_team(self):
        for t in self.teams:
            if t != self.active_team:
                return t

    def get_opponents_map_pick(self):
        for m in self.maps:
            if m.pickedby == self.get_inactive_team():
                return m

    def generate_sides_emoji(self):
        self.emoji_to_option = {"\N{REGIONAL INDICATOR SYMBOL LETTER T}": "Terrorists",
                                "\N{REGIONAL INDICATOR SYMBOL LETTER C}": "Counter-terrorists"}
        self.option_to_emoji = {option: emoji
                                for emoji, option in self.emoji_to_option.items()}
        self.emoji = list(self.emoji_to_option.keys())

    def check_reaction(self, reaction, user):
        if self.active_team.captain is not None:
            allowed_users = [self.active_team.captain]
        else:
            allowed_users = self.active_team.players
        return (reaction.message == self.message
                and user in allowed_users
                and str(reaction.emoji) in self.get_remaining_emoji())

    async def on_reaction(self, reaction, user):
        emoji = str(reaction.emoji)
        selected_option = self.get_option(emoji)
        emoji_to_add, emoji_to_remove = [], []

        if self.mode == 'pick':
            self.post_options += f"*{self.active_team.name} picked {selected_option}*\n"
            selected_map = self.get_map_from_name(selected_option)
            selected_map.pick(self.active_team)
            self.chosen_maps.append(selected_map)
            self.remaining_options.remove(selected_option)
            await self.message.clear_reaction(emoji)
        elif self.mode == 'ban':
            self.post_options += f"*{self.active_team.name} banned {selected_option}*\n"
            self.remaining_options.remove(selected_option)
            await self.message.clear_reaction(emoji)
            if len(self.remaining_options) == 1:
                final_option = self.remaining_options.pop()
                await self.message.clear_reaction(self.get_emoji(final_option))
                self.chosen_maps.append(self.get_map_from_name(final_option))
                self.post_options += f"*{final_option} was left over*\n"
                self.active_team = self.next_team() # Need this so that the active team changes to the second team
        elif self.mode == 'sides':
            opponents_map_pick = self.get_opponents_map_pick()
            opponents_map_pick.choose_side(self.active_team, selected_option)
            self.post_options += (f"*{self.active_team.name} chose to start as "
                                  f"{selected_option} on {opponents_map_pick.readable_name}*\n")

        self.active_team = self.next_team()
        if self.veto:
            prev_mode = self.mode
            self.mode = self.next_mode()
            if self.mode == 'sides' and prev_mode != 'sides':
                self.options = ["Counter-terrorists", "Terrorists"]
                self.remaining_options = self.options[:]
                self.generate_sides_emoji()
                for emoji in emoji_to_remove:
                    await self.message.clear_reaction(emoji)
        else:
            self.mode = ''
            self.remaining_options = []
            self.config = await get5.commands.generate_config(self.teams[0], self.teams[1], self.chosen_maps, self.gametype)
            self.finished = True

        self.update_fields()
        self.update_preoptions()
        await self.update_message()

class Lobby:
    def __init__(self, bot, players=[]):
        self.bot = bot
        self.players = players
        self.captains = []
        self.join_emoji = "\N{BLACK RIGHT-POINTING TRIANGLE}"
        self.captain_emoji = "\N{CROWN}"
        self.emoji = [self.join_emoji, self.captain_emoji]

    async def run(self, ctx):
        self.message = await ctx.send(embed=self.embed())
        for emoji in self.emoji:
            await self.message.add_reaction(emoji)

        while (len(self.players) < 1 or len(self.captains) < 1):
            tasks = [asyncio.create_task(self.process_add_reactions()),
                     asyncio.create_task(self.process_remove_reactions())]
            # Run until one task is completed, then cancel the other one
            completed_tasks, pending_tasks = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in pending_tasks:
                    task.cancel()

        self.message.delete()
            
    async def rerun(self, ctx):
        await self.message.delete()
        await self.run(ctx)
    
    async def process_add_reactions(self):
        reaction, user = await self.bot.wait_for('reaction_add', check=self.check_reaction_add)
        if str(reaction.emoji) == self.join_emoji:
            self.add_player(user)
        elif str(reaction.emoji) == self.captain_emoji:
            self.add_captain(user)
        await self.message.edit(embed=self.embed())

    async def process_remove_reactions(self):
        reaction, user = await self.bot.wait_for('reaction_remove', check=self.check_reaction_remove)
        if str(reaction.emoji) == self.join_emoji:
            self.remove_player(user)
        elif str(reaction.emoji) == self.captain_emoji:
            self.remove_captain(user)
        await self.message.edit(embed=self.embed())

    def check_reaction_add(self, reaction, user):
        return (reaction.message == self.message
                and not user.bot
                and str(reaction.emoji) in self.emoji)

    def check_reaction_remove(self, reaction, user):
        return (reaction.message == self.message
                and user in self.players
                and str(reaction.emoji) in self.emoji)
    
    def add_player(self, user):
        if user not in self.players and len(self.players) <= 10:
            self.players.append(user)

    def remove_player(self, user):
        if user in self.players:
            self.players.remove(user)
        if user in self.captains:
            self.captains.remove(user)

    def add_captain(self, user):
        if user not in self.captains:
            self.captains.append(user)

    def remove_captain(self, user):
        if user in self.captains:
            self.captains.remove(user)

    def embed(self):
        description_str = (f"{self.join_emoji} to join/leave the lobby\n"
                           f"{self.captain_emoji} to join/leave the captain queue\n\n")
        players_str = ""
        
        for user in self.players:
            if user in self.captains[:2]:
                players_str += self.captain_emoji + " "
            players_str += f"{user.mention}\n"

        embed = Embed(title="Matchbot Lobby",
                      description=description_str+players_str)
        embed.set_footer(text=f"{len(self.players)}/10 players")
        return embed
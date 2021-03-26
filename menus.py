from discord import Embed, Emoji
from typing import Union, Iterable
from classes import Team, Map, Match, wingman_maps_by_name, active_duty_maps_by_name


def keycap(number):
    if number <= 10:
        return f"{number}\N{COMBINING ENCLOSING KEYCAP}"
    else:
        raise ValueError(f"Can only keycap numbers from 1-10 (got {number})")

A_EMOJI = "\N{NEGATIVE SQUARED LATIN CAPITAL LETTER A}"
B_EMOJI = "\N{NEGATIVE SQUARED LATIN CAPITAL LETTER B}"

A_EMOJI_URL = "https://twemoji.maxcdn.com/v/latest/72x72/1f170.png"
B_EMOJI_URL = "https://twemoji.maxcdn.com/v/latest/72x72/1f171.png"

CT_EMOJI = "<:counterterrorist:821019184565059594>"
T_EMOJI = "<:terrorist:821019184258351114>"


class SelectMenu:
    def __init__(self, bot, title: str, options: Iterable[str], show_selection_history=True):
        self.bot = bot
        self.title = title
        self.options = options
        self.show_selection_history = show_selection_history
        self.embed = Embed()
        self.emoji_to_option = {keycap(i+1): option for i, option in enumerate(self.options)}
        self.option_to_emoji = {option: keycap(i+1) for i, option in enumerate(self.options)}
        self.remaining_options = options[:]
        self.chosen_options = []
        self.valid_users = []
        self.selection_history = ""

    def remaining_emoji(self):
        return [self.option_to_emoji[option] for option in self.remaining_options]

    def add_field(self, title: str, contents: Union[list, str], inline=False):
        if isinstance(contents, str):
            contents_str = contents
        else:
            contents_str = ""
            for line in contents:
                contents_str += f"{line}\n"
        if contents_str:
            self.embed.add_field(name=title, value=contents_str, inline=inline)

    async def run(self, ctx):
        self.message = await ctx.send(embed=self.embed)
        await self.update()
        while self.remaining_options:
            await self.process_reactions()

    async def process_reactions(self):
        reaction, user = await self.bot.wait_for('reaction_add', check=self.reaction_validator)
        await self.on_reaction(reaction, user)

    def reaction_validator(self, reaction, user):
        """Checks if the reaction is valid.
        Reaction is valid iff:
        - It is a reaction to this message
        - The reaction emoji is the emoji of one of the remaining options
        - The user is in the list of valid users, or, if the list is empty, the user is not a bot"""
        return (reaction.message == self.message
                and str(reaction.emoji) in self.remaining_emoji()
                and (user in self.valid_users or (not self.valid_users and not user.bot)))

    async def on_reaction(self, reaction, user):
        emoji = reaction.emoji
        option = self.emoji_to_option[emoji]
        await self.message.clear_reaction(emoji)
        self.remaining_options.remove(option)
        self.chosen_options.append(option)
        self.selection_history += f"{user} picked {option}\n"
        await self.update()

    async def update(self):
        self.embed.title = self.title
        self.embed.clear_fields()
        self.add_field("Selection history", self.selection_history)
        self.add_field("Options",
                       [f"{emoji} {option}" for emoji, option in zip(self.remaining_emoji(), self.remaining_options)])
        await self.message.edit(embed=self.embed)
        for reaction in self.remaining_emoji():
            await self.message.add_reaction(reaction)


class VetoMenu(SelectMenu):
    def __init__(self, bot, match: Match):
        self.match = match
        self.team_to_emoji = {self.match.teams[0]: A_EMOJI, self.match.teams[1]: B_EMOJI}
        self.team_to_emoji_url = {self.match.teams[0]: A_EMOJI_URL, self.match.teams[1]: B_EMOJI_URL}
        self.team_to_letter = {self.match.teams[0]: 'A', self.match.teams[1]: 'B'}

        if self.match.bestof == 1:
            self.veto = ['ban', 'ban', 'ban', 'ban', 'ban', 'ban']
        elif self.match.bestof == 3:
            self.veto = ['ban', 'ban', 'pick', 'pick', 'ban', 'ban']

        if self.match.gametype == '2v2':
            self.maps = wingman_maps_by_name
        else:
            self.maps = active_duty_maps_by_name

        self.step = 0
        self.valid_users = self.active_team().players
        self.choose_sides = False

        super().__init__(bot=bot, title="Map Veto", options=list(self.maps.keys()))

    async def setup_choose_sides(self):
        self.choose_sides = True

        # Save map veto state
        self.map_options = self.options
        self.remaining_map_options = self.remaining_options
        self.map_option_to_emoji = self.option_to_emoji
        self.map_emoji_to_option = self.emoji_to_option
        await self.message.clear_reactions()

        # Create side pick state
        self.options = ['T', 'CT']
        self.remaining_options = self.options[:]
        self.option_to_emoji = {'T': T_EMOJI, 'CT': CT_EMOJI}
        self.emoji_to_option = {T_EMOJI: 'T', CT_EMOJI: 'CT'}

    async def unsetup_choose_sides(self):
        self.choose_sides = False
        await self.message.clear_reactions()
        self.options = self.map_options
        self.remaining_options = self.remaining_map_options
        self.option_to_emoji = self.map_option_to_emoji
        self.emoji_to_option = self.map_emoji_to_option

    def active_team(self):
        return self.match.teams[self.step % 2]

    def inactive_team(self):
        return self.match.teams[(self.step + 1) % 2]

    async def on_reaction(self, reaction, user):
        emoji = str(reaction.emoji)
        option = self.emoji_to_option[emoji]
        await self.message.clear_reaction(emoji)
        self.remaining_options.remove(option)
        if self.veto[self.step] == 'ban':
            self.selection_history += f"{self.team_to_letter[self.active_team()]} banned {option}\n"
        elif self.veto[self.step] == 'pick':
            if not self.choose_sides:
                self.match.pick(Map(self.maps[option]), self.active_team())
                self.selection_history += f"{self.team_to_letter[self.active_team()]} picked {option}"
                await self.setup_choose_sides()
            else:
                self.match.maps[-1].choose_side(self.inactive_team(), option)
                self.selection_history += f" ({self.team_to_letter[self.inactive_team()]}: {option})\n"
                await self.unsetup_choose_sides()
        if len(self.remaining_options) == 1:
            option = self.remaining_options.pop()
            await self.message.clear_reaction(self.option_to_emoji[option])
            self.match.pick(Map(self.maps[option]), None)
            self.selection_history += f"{option} was left over\n"
        if self.choose_sides:
            self.valid_users = self.inactive_team().players
        else:
            self.step += 1
            self.valid_users = self.active_team().players
        await self.update()

    async def update(self):
        self.embed.title = self.title
        self.embed.clear_fields()
        self.embed.set_footer(text=Embed.Empty, icon_url=Embed.Empty)

        # Field for each team
        for t in self.match.teams:
            self.add_field(f"{self.team_to_emoji[t]} {t.name}", [player.mention for player in t.players], inline=True)

        # Field for each map
        for i, chosen_map in enumerate(self.match.maps):
            field_title = f"Map {i+1}: {self.maps.inverse[chosen_map.ingame_name]}"
            field_contents = ""
            if chosen_map.pickedby is not None:
                field_contents += f"Picked by {chosen_map.pickedby.name}\n"

            if chosen_map.knife:
                field_contents += "Knife for sides"
            else:
                for side, team in chosen_map.sides.items():
                    if team != chosen_map.pickedby and team is not None:
                        field_contents += f"{team.name} starting as {side.upper()}"
            self.add_field(field_title, field_contents)

        # Field for selection history
        self.add_field("\u200b", self.selection_history)

        # Field for remaining options
        if self.remaining_options:
            self.add_field("Options",
                           [f"{emoji} {option}" for emoji, option in zip(self.remaining_emoji(), self.remaining_options)])
            if self.choose_sides:
                self.embed.set_footer(text=f"{self.inactive_team().name} to choose starting side",
                                      icon_url=self.team_to_emoji_url[self.inactive_team()])
            else:
                self.embed.set_footer(text=f"{self.active_team().name} to {self.veto[self.step]}",
                                      icon_url=self.team_to_emoji_url[self.active_team()])

        await self.message.edit(embed=self.embed)
        for reaction in self.remaining_emoji():
            await self.message.add_reaction(reaction)

# class PickTeamsMenu(SelectMenu):
#     def __init__(self, bot, captain1: Member, captain2: Member, players: Iterable[Member]):
#         self.bot = bot
#         self.captains = [captain1, captain2]
#         self.teams = [Team(captain1), Team(captain2)]
#         self.active_captain = self.captains[0]
#         self.finished = False
#         self.players = {player.mention: player for player in players if player not in self.captains}
#
#         self.title = "Pick Teams"
#         self.pre_options = ("**Captains:** \n"
#                             f"{self.captains[0].mention}\n"
#                             f"{self.captains[1].mention}\n")
#         self.options = list(self.players.keys())
#         self.remaining_options = self.options[:]
#         self.post_options = ""
#         self.fields = {self.teams[0].name: self.teams[0].display(),
#                        self.teams[1].name: self.teams[1].display()}
#         self.inline_fields = True
#         self.footer = ""
#         self.embed = Embed()
#         self.message = None
#
#         self.generate_emoji()
#         self.update_contents()
#
#     def next_captain(self):
#         for captain in self.captains:
#             if captain != self.active_captain:
#                 return captain
#
#     def update_fields(self):
#         self.fields = {self.teams[0].name: self.teams[0].display(),
#                        self.teams[1].name: self.teams[1].display()}
#
#     def update_preoptions(self):
#         self.pre_options = ("**Captains:** \n"
#                             f"{self.captains[0].mention}\n"
#                             f"{self.captains[1].mention}\n")
#         if self.remaining_options:
#             self.pre_options += f"\n{self.active_captain.mention} **to pick**"
#
#     async def run(self, ctx):
#         self.message = await ctx.send(embed=self.embed)
#         await self.add_all_reactions()
#         self.update_preoptions()
#         await self.update_message()
#         self.finished = False
#         while not self.finished and self.remaining_options:
#             await self.process_reactions()
#
#     def check_reaction(self, reaction, user):
#         return (reaction.message == self.message
#                 and user == self.active_captain
#                 and str(reaction.emoji) in self.get_remaining_emoji())
#
#     async def on_reaction(self, reaction, user):
#         emoji = str(reaction.emoji)
#         selected_option = self.get_option(emoji)
#         selected_user = self.players[selected_option]
#         for team in self.teams:
#             if team.captain == self.active_captain:
#                 team.add_player(selected_user)
#         self.post_options += f"{user.mention} picked {selected_option}\n"
#         self.remaining_options.remove(selected_option)
#         self.active_captain = self.next_captain()
#         self.update_fields()
#         self.update_preoptions()
#         if len(self.remaining_options) == 0:
#             self.finished = True
#         await self.message.clear_reaction(emoji)
#         await self.update_message()

# class Lobby:
#     def __init__(self, bot, players=[]):
#         self.bot = bot
#         self.players = players
#         self.captains = []
#         self.join_emoji = "\N{BLACK RIGHT-POINTING TRIANGLE}"
#         self.captain_emoji = "\N{CROWN}"
#         self.emoji = [self.join_emoji, self.captain_emoji]
#
#     async def run(self, ctx):
#         self.message = await ctx.send(embed=self.embed())
#         for emoji in self.emoji:
#             await self.message.add_reaction(emoji)
#
#         while (len(self.players) < 1 or len(self.captains) < 1):
#             tasks = [asyncio.create_task(self.process_add_reactions()),
#                      asyncio.create_task(self.process_remove_reactions())]
#             # Run until one task is completed, then cancel the other one
#             completed_tasks, pending_tasks = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
#             for task in pending_tasks:
#                     task.cancel()
#
#         self.message.delete()
#
#     async def rerun(self, ctx):
#         await self.message.delete()
#         await self.run(ctx)
#
#     async def process_add_reactions(self):
#         reaction, user = await self.bot.wait_for('reaction_add', check=self.check_reaction_add)
#         if str(reaction.emoji) == self.join_emoji:
#             self.add_player(user)
#         elif str(reaction.emoji) == self.captain_emoji:
#             self.add_captain(user)
#         await self.message.edit(embed=self.embed())
#
#     async def process_remove_reactions(self):
#         reaction, user = await self.bot.wait_for('reaction_remove', check=self.check_reaction_remove)
#         if str(reaction.emoji) == self.join_emoji:
#             self.remove_player(user)
#         elif str(reaction.emoji) == self.captain_emoji:
#             self.remove_captain(user)
#         await self.message.edit(embed=self.embed())
#
#     def check_reaction_add(self, reaction, user):
#         return (reaction.message == self.message
#                 and not user.bot
#                 and str(reaction.emoji) in self.emoji)
#
#     def check_reaction_remove(self, reaction, user):
#         return (reaction.message == self.message
#                 and user in self.players
#                 and str(reaction.emoji) in self.emoji)
#
#     def add_player(self, user):
#         if user not in self.players and len(self.players) <= 10:
#             self.players.append(user)
#
#     def remove_player(self, user):
#         if user in self.players:
#             self.players.remove(user)
#         if user in self.captains:
#             self.captains.remove(user)
#
#     def add_captain(self, user):
#         if user not in self.captains:
#             self.captains.append(user)
#
#     def remove_captain(self, user):
#         if user in self.captains:
#             self.captains.remove(user)
#
#     def embed(self):
#         description_str = (f"{self.join_emoji} to join/leave the lobby\n"
#                            f"{self.captain_emoji} to join/leave the captain queue\n\n")
#         players_str = ""
#
#         for user in self.players:
#             if user in self.captains[:2]:
#                 players_str += self.captain_emoji + " "
#             players_str += f"{user.mention}\n"
#
#         embed = Embed(title="Matchbot Lobby",
#                       description=description_str+players_str)
#         embed.set_footer(text=f"{len(self.players)}/10 players")
#         return embed
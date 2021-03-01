from discord import Message
from discord.ext.commands import *

from . import Cog
import sql.channels, sql.leaderboards, sql.users

# Create the sql tables if they don't exist
sql.channels.create()
sql.leaderboards.create()

class ChannelCog(Cog, name='Channel management'):
    @Cog.listener()
    async def on_message(self, message: Message):
        if sql.channels.get_autodelete(message.channel.id) and not message.author.bot:
            await message.delete(delay=10)

    @command()
    @has_permissions(manage_channels=True)
    async def channels2(self, ctx: Context, mode='show', mode_arg=''):
        "Show and edit the purged and linked channels."
        mentioned_channels = ctx.message.raw_channel_mentions
        help_str = "Usage: `!channels [show/add/del/help] [autodelete <#channel(s)>] [redirect <#channel1> <#channel2>]`"
        if mode == "show":
            await ctx.send(sql.channels.display(mode_arg))
        elif mode == "add":
            if mode_arg == "redirect":
                sql.channels.set_redirectchannel(*mentioned_channels)
                await ctx.send("Redirecting bot responses from <#{}> to <#{}>".format(*mentioned_channels),
                               delete_after=10)
            elif mode_arg == "autodelete":
                for channel in mentioned_channels:
                    sql.channels.set_autodelete(channel, True)
                    await ctx.send("Autodeleting bot triggers in <#{}>".format(channel))
            else:
                await ctx.send(help_str, delete_after=10)
        elif mode == "del":
            if mode_arg == "redirect":
                for channel in mentioned_channels:
                    sql.channels.set_redirectchannel(channel, channel)
                    await ctx.send("Removed redirecting bot responses from <#{}>".format(channel),
                                   delete_after=10)
            elif mode_arg == "autodelete":
                for channel in mentioned_channels:
                    sql.channels.set_autodelete(channel, False)
                    await ctx.send("Removed autodeleting bot triggers in <#{}>".format(channel),
                                   delete_after=10)
            else:
                if mentioned_channels:
                    for channel in mentioned_channels:
                        sql.channels.delete_row(channel)
                        await ctx.send("Removing entry <#{}>".format(channel))
                else:
                    await ctx.send(help_str, delete_after=10)
        elif mode == "help":
            await ctx.send(help_str, delete_after=10)

def setup(bot):
    bot.add_cog(ChannelCog(bot))

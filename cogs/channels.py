from discord import Message
import discord.ext.commands as cmds

from . import Cog
import sql.channels

class ChannelCog(Cog, name='Channel management'):
    @Cog.listener()
    async def on_message(self, message: Message):
        if (await sql.channels.get_autodelete(message.channel.id)
            and not message.author.bot
            and not message.author.permissions_in(message.channel).manage_messages):
            await message.delete(delay=10)

    @cmds.command()
    @cmds.has_permissions(manage_channels=True)
    async def channels(self, ctx: cmds.Context, mode='show', mode_arg=''):
        "Show and edit the purged and linked channels."
        mentioned_channels = ctx.message.raw_channel_mentions
        help_str = "Usage: `!channels [show/add/del/help] [autodelete <#channel(s)>] [redirect <#channel1> <#channel2>]`"
        if mode == "show":
            await ctx.send(await sql.channels.display(mode_arg))
        elif mode == "add":
            if mode_arg == "redirect":
                await sql.channels.set_redirectchannel(*mentioned_channels)
                await ctx.send("Redirecting bot responses from <#{}> to <#{}>".format(*mentioned_channels),
                               delete_after=10)
            elif mode_arg == "autodelete":
                for channel in mentioned_channels:
                    await sql.channels.set_autodelete(channel, True)
                    await ctx.send("Autodeleting bot triggers in <#{}>".format(channel))
            else:
                await ctx.send(help_str, delete_after=10)
        elif mode == "del":
            if mode_arg == "redirect":
                for channel in mentioned_channels:
                    await sql.channels.set_redirectchannel(channel, channel)
                    await ctx.send("Removed redirecting bot responses from <#{}>".format(channel),
                                   delete_after=10)
            elif mode_arg == "autodelete":
                for channel in mentioned_channels:
                    await sql.channels.set_autodelete(channel, False)
                    await ctx.send("Removed autodeleting bot triggers in <#{}>".format(channel),
                                   delete_after=10)
            else:
                if mentioned_channels:
                    for channel in mentioned_channels:
                        await sql.channels.delete_row(channel)
                        await ctx.send("Removing entry <#{}>".format(channel))
                else:
                    await ctx.send(help_str, delete_after=10)
        elif mode == "help":
            await ctx.send(help_str, delete_after=10)

def setup(bot):
    bot.add_cog(ChannelCog(bot))

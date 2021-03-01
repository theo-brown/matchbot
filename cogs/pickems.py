from discord import AllowedMentions
from discord.ext.commands import *

from . import Cog
import sql.pickems

class PickemsCog(Cog, name="Pick'em prediction commands"):
    @command()
    async def pickems(self, ctx: Context, *args):
        "Show the pick'ems leaderboard. Moderators can edit scores."
        args = list(args)
        if len(ctx.message.channel_mentions) == 0:
            pickem_channel_id = ctx.channel.id
        elif len(ctx.message.channel_mentions) == 1:
            pickem_channel_id = ctx.message.channel_mentions[0].id
            args.remove(ctx.message.channel_mentions[0].mention)
        else:
            await ctx.send("Error: expected 0 or 1 channel mentions")
            return
        if ctx.author.guild_permissions.manage_channels:
            if len(ctx.message.mentions) == 1:
                user = ctx.message.mentions[0]
                args.remove(user.mention)
            elif len(ctx.message.mentions) > 1:
                await ctx.send("Error: expected 0 or 1 user mentions")
                return
            if "add" in args:
                # This keyword can be used to add a new row, or add points to an
                # existing entry. See pickems.add_row for why (it's all done
                # in sqlite rather than python)
                args.remove("add")
                if args:
                    points = args[-1]
                else:
                    points = 0
                sql.pickems.add_row(pickem_channel_id, user.id, points)
                await ctx.send(
                    "Added row: <#{}> <@{}> {}pts\n*If row existed, points were added to that row's points*".format(
                        pickem_channel_id, user.id, points))
                return
            elif "del" in args:
                sql.pickems.delete_row(pickem_channel_id, user.id)
                await ctx.send("Deleted row: <#{}> <@{}>".format(pickem_channel_id, user.id))
                return
            elif "set" in args:
                args.remove("set")
                points = args[-1]
                sql.pickems.set_points(pickem_channel_id, user.id, points)
                await ctx.send("Set points: <#{}> <@{}> {}pts".format(pickem_channel_id, user.id, points))
                return
        await ctx.send(sql.pickems.get_message(pickem_channel_id),
                       allowed_mentions=AllowedMentions(users=False))

def setup(bot):
    bot.add_cog(PickemsCog(bot))

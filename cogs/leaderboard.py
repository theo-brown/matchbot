from discord import AllowedMentions
from discord.ext.commands import *

from . import Cog
import sql.leaderboards

class LeaderboardCog(Cog, name="Pick'em commands"):
    @command()
    async def leaderboard2(self, ctx: Context, *args):
        "Show the pick'ems leaderboard. Moderators can edit scores."
        args = list(args)
        if len(ctx.message.channel_mentions) == 0:
            leaderboard_channel_id = ctx.channel.id
        elif len(ctx.message.channel_mentions) == 1:
            leaderboard_channel_id = ctx.message.channel_mentions[0].id
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
                # existing entry. See leaderboards.add_row for why (it's all done
                # in sqlite rather than python)
                args.remove("add")
                if args:
                    points = args[-1]
                else:
                    points = 0
                sql.leaderboards.add_row(leaderboard_channel_id, user.id, points)
                await ctx.send(
                    "Added row: <#{}> <@{}> {}pts\n*If row existed, points were added to that row's points*".format(
                        leaderboard_channel_id, user.id, points))
                return
            elif "del" in args:
                sql.leaderboards.delete_row(leaderboard_channel_id, user.id)
                await ctx.send("Deleted row: <#{}> <@{}>".format(leaderboard_channel_id, user.id))
                return
            elif "set" in args:
                args.remove("set")
                points = args[-1]
                sql.leaderboards.set_points(leaderboard_channel_id, user.id, points)
                await ctx.send("Set points: <#{}> <@{}> {}pts".format(leaderboard_channel_id, user.id, points))
                return
        await ctx.send(sql.leaderboards.get_message(leaderboard_channel_id),
                       allowed_mentions=AllowedMentions(users=False))

def setup(bot):
    bot.add_cog(LeaderboardCog(bot))

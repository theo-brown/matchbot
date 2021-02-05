###############################################################################

def run(bot):
    with open('bot_token.txt') as f:
        bot_token = f.read().strip()
    bot.run(bot_token)

###############################################################################

def get_users_with_role(ctx, role_id):
    role_id = int(role_id)
    users = []
    for user in ctx.guild.members:
        user_roles_ids = [r.id for r in user.roles]
        if role_id in user_roles_ids:
            users.append(user)
    return users

###############################################################################
from os import scandir
def clear_data():
    for file in scandir(r"data"):
        open(file.path, "w").close()
            
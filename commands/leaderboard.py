from operator import itemgetter

help_message = \
"""
```
!leaderboard [--clear] [USER SCORE]
If no arguments provided, prints the current leaderboard
If --clear provided, deletes the current leaderboard
If arguments provided, interpreted in pairs as <@user> <score>
```
"""

leaderboard = {}

def clear():
    global leaderboard
    leaderboard = {}

def increment(userlist):
    for user in userlist:
        usermention = user.mention
        if usermention in leaderboard.keys():
            leaderboard[usermention] += 1
        else:
            leaderboard[usermention] = 1

def generate_text():
    # Create a list of tuples in the form (user, score), ordered from high to low score
    leaderboard_list = sorted(leaderboard.items(), key=itemgetter(1), reverse=True)
    positions = [1]*len(leaderboard_list)
    for i in range(len(leaderboard_list)-1):
        if leaderboard_list[i+1][1] == leaderboard_list[i][1]:
            positions[i+1] = positions[i]
        else:
            positions[i+1] = positions[i] + 1
    leaderboard_text = "**Pick'em Leaderboard:**\n\n"
    for i, v in enumerate(leaderboard_list):
        leaderboard_text += "{}. {}\t\t({}pts)\n".format(positions[i], v[0], v[1])
    return leaderboard_text


async def run(message, args, kwargs):
    if len(args) == 0 and len(kwargs) == 0:
        await message.channel.send(generate_text())
    elif "clear" in kwargs.keys():
        clear()
    else:
        for i in range(len(args) // 2):
            name = args[2*i]
            score = int(args[2*i+1])
            if name in leaderboard.keys():
                leaderboard[name] += score
            else:
                leaderboard[name] = score
        await message.channel.send(generate_text())


async def help(message, args, kwargs):
    # If you want to edit what happens when the user asks for help with
    # `!command --help`, you can edit this function
    await message.channel.send(help_message)
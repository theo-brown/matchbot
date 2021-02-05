###############################################################################

def run(bot):
    with open('bot_token.txt') as f:
        bot_token = f.read().strip()
    bot.run(bot_token)

###############################################################################
from os import scandir
def clear_data():
    for file in scandir(r"data"):
        open(file.path, "w").close()
            
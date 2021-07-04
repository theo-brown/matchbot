import parsedatetime as pdt
import humanize
from datetime import datetime
import re

def parse_date(string):
    # Parse schedule string
    pdt_obj, status = pdt.Calendar().parse(string) # Turn any human-written string into a pdt object
    datetime_obj = datetime(*pdt_obj[:6]) # Turn the object into a datetime object
    day = humanize.naturalday(datetime_obj, "%A").capitalize() # 'Tomorrow' or 'Wednesday'
    if day not in ["Today", "Tomorrow"]:
        # Set day to be of the format "Wednesday 24th Feb"
        # For full months, swap "%b" for "%B"
        day = " ".join([day,
                        humanize.ordinal(datetime_obj.day),
                        datetime_obj.strftime("%b")])
    time = datetime_obj.strftime(" at %H%M")
    return datetime_obj, day + time


def parse_results(string):
    # Expect scores in format ###-###
    regex = re.compile("\d+-\d+")
    # Split around the scores, ignore blank spaces
    # Produces a list of game/map names and scores
    games = [s.strip() for s in regex.split(string) if s.strip()]
    scores = regex.findall(string)
    # If there are no game names, then we need to create an empty games array
    if not len(games):
        games = [''] * len(scores)
    if len(games) != len(scores):
        raise ValueError(f"Expected either only scores, or the same number of "
                         f"scores and games (got {len(scores)} scores and "
                         f"{len(games)} games)")
    result_dict = []
    result_str = ""
    for game, score in zip(games, scores):
        score1, score2 = map(int, score.split('-'))
        if score1 == score2:
            winner = 0
            score = f"{score1}-{score2}"
        elif score1 > score2:
            winner = 1
            score = f"**{score1}**-{score2}"
        else:
            winner = 2
            score = f"{score1}-**{score2}**"
        result_dict.append({'game': game,
                            'score': (score1, score2),
                            'winner': winner})
        if game:
            game += ": "
        result_str += game + score + '\n'

    return result_dict, result_str


def get_all_mentions_in_order(ctx, args, pop=True):
    user_regex = re.compile("^<@!?(\d+)>$")
    role_regex = re.compile("^<@&(\d+)>$")
    channel_regex = re.compile("^<#(\d+)>$")
    output = []
    temp_args = args[:] # Create a copy so that we can remove elements from the original
    for arg in temp_args:
        userid = user_regex.match(arg)
        roleid = role_regex.match(arg)
        channelid = channel_regex.match(arg)
        if userid:
            output.append(ctx.guild.get_member(int(userid.group(1))))
            if pop: args.remove(arg)
        elif roleid:
            output.append(ctx.guild.get_role(int(roleid.group(1))))
            if pop: args.remove(arg)
        elif channelid:
            output.append(ctx.guild.get_channel(int(channelid.group(1))))
            if pop: args.remove(arg)
    return output

def convert_mention_into_id(mention):
    regex = re.compile("^<(?:@!?|@&|#)(\d+)>$") # matches user mentions, nickname mentions, role mentions and channel mentions
    match = regex.match(mention)
    if match:
        return int(match.group(1))
    else:
        raise ValueError(f"mention must be a standard Discord mention string (got {mention})")
###############################################################################

def run(bot):
    with open('bot_token.txt') as f:
        bot_token = f.read().strip()
    bot.run(bot_token)

###############################################################################
from dateutil.parser import parserinfo

class CustomDateParser(parserinfo):
    # WEEKDAYS is a 7-length array of tuples containing accepted abbreviations
    # for each day. As we're just using dateutil.parser.parse as a binary check
    # of whether a date fits our format, we don't care what day 
    # 'Today'/'Tomorrow' refers to, so we can put it as an accepted
    # abbreviation for any day
    WEEKDAYS=[('Mon', 'Monday', 'Today', 'Tomorrow'), 
              ('Tue', 'Tuesday', 'Today', 'Tomorrow'), 
              ('Wed', 'Wednesday', 'Today', 'Tomorrow'), 
              ('Thu', 'Thursday', 'Today', 'Tomorrow'), 
              ('Fri', 'Friday', 'Today', 'Tomorrow'), 
              ('Sat', 'Saturday', 'Today', 'Tomorrow'), 
              ('Sun', 'Sunday', 'Today', 'Tomorrow')]        
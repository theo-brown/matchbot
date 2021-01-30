"""
EVL Discord Bot template by Theo Brown
Licensed under GNU GPLv3
https://github.com/theo-brown/EVL-bot-template
"""

COMMAND_PREFIX = '!'
KWARG_PREFIX = '-'
ERROR_ON_UNRECOGNISED_COMMAND = False
ECHO_COMMAND_ARGS = False

def parse_args(message):
    # Get all the args separately
    args = message.content.split(' ')
    # Extract command string without prefix
    trigger = args.pop(0)[1:]
    
    # Separate kwargs, args and flags
    kwargs = {}
    for i, arg in enumerate(args):
        if arg.startswith(KWARG_PREFIX):
            if arg.startswith(2*KWARG_PREFIX):
                # Separate flags (keywords that don't have values)
                # Flags are determined by a double prefix (eg --)
                value = ''
            else:    
                # Next item in supplied args is the value
                value = args[i+1]
            # Extract the keyword and strip the prefix
            keyword = args[i].replace(KWARG_PREFIX, '')
            # Save in kwargs
            kwargs[keyword] = value
    for k, v in kwargs.items():
        if v == '':
            args.remove(2*KWARG_PREFIX + k)
        else:
            args.remove(KWARG_PREFIX + k)
            args.remove(v)
    
    return trigger, args, kwargs

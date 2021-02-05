###############################################################################

# data/autodelete.txt is a text file of channel ids in which any 
# messages sent by a user will be deleted
    
def add(channel_id):
    with open("data/autodelete.txt", "a") as f:
        f.write("{}\n".format(channel_id))

def remove(channel_id):
    with open("data/autodelete.txt", "r") as f:
        lines = f.readlines()
    with open("data/autodelete.txt", "w") as f:
        for line in lines:
            if not int(line.strip()) == int(channel_id):
                f.write(line)

def get_as_str():
    autodelete = ""
    with open("data/autodelete.txt", "r") as f:
        lines = f.readlines()
    for line in lines:
        autodelete += "<#{}>\n".format(line.strip())
    return autodelete

def in_autodelete(channel_id):
    with open("data/autodelete.txt", "r") as f:
        autodelete = f.readlines()
    return "{}\n".format(channel_id) in autodelete
       
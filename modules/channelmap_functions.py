###############################################################################        

# data/channelmap.txt is a text file of listen_channel_id->send_channel_id pairs

def add(listen_channel_id, send_channel_id):
    with open("data/channelmap.txt", "a") as f:
        f.write("{}->{}\n".format(listen_channel_id, send_channel_id))
        
def remove(listen_channel_id):
    with open("data/channelmap.txt", "r") as f:
        lines = f.readlines()
    with open("data/channelmap.txt", "w") as f:
        for line in lines:
            if not line.startswith("{}->".format(listen_channel_id)):
                f.write(line)
                
def get_as_str():
    channelmap = ""
    with open("data/channelmap.txt", "r") as f:
        lines = f.readlines()
    for line in lines:
        channel_ids = line.strip().split("->")
        channelmap += "<#{}>-><#{}>\n".format(channel_ids[0], channel_ids[1])
    return channelmap

def get_send_channel_id(listen_channel_id):
    with open("data/channelmap.txt", "r") as f:
        lines = f.readlines()
    for line in lines:
        if line.startswith("{}->".format(listen_channel_id)):
            return int(line.strip().split("->")[1])
    return int(listen_channel_id)

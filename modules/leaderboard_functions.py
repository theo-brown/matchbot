from operator import itemgetter

def add_user(user_id, score=0):
    with open("data/leaderboard.txt", "a") as f:
        f.write("{}:{}\n".format(user_id, score))

def set_user_score(user_id, score):
    with open("data/leaderboard.txt", "r") as f:
        lines = f.readlines()
    with open("data/leaderboard.txt", "w") as f:
        for line in lines:
            if line.startswith("{}:".format(user_id)):
                line = "{}:{}".format(user_id, score)
            f.write(line + "\n")

def increment(list_user_ids):
    with open("data/leaderboard.txt", "r") as f:
        lines = f.readlines()
    scores = {}
    for line in lines:
        if line != "\n":
            user_id, score = line.strip().split(":")
            if user_id in list_user_ids:
                scores[user_id] = int(score) + 1
                list_user_ids.remove(user_id)
            else:
                scores[user_id] = int(score)
    for user_id in list_user_ids:
        scores[user_id] = 1
    with open("data/leaderboard.txt", "w") as f:
        f.writelines(["{}:{}\n".format(user_id, score) for user_id, score in scores.items()])

def get_as_str():
    with open("data/leaderboard.txt", "r") as f:
        lines = f.readlines()
    user_scores = [l.strip().split(":") for l in lines if l != '\n']
    user_scores.sort(key=itemgetter(1), reverse=True)
    
    positions = [1]*len(user_scores)
    for i in range(len(user_scores)-1):
        if user_scores[i+1][1] == user_scores[i][1]:
            positions[i+1] = positions[i]
        else:
            positions[i+1] = positions[i] + 1
    
    leaderboard_text = "**Pick'em Leaderboard:**\n\n"
    for i, v in enumerate(user_scores):
        leaderboard_text += "{}. <@{}>\t\t({}pts)\n".format(positions[i], v[0], v[1])
    return leaderboard_text
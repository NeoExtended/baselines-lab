def check(freespace, locations):
    valid = []
    for loc in locations:
        valid.append(freespace[loc[0]][loc[1]])
    return valid
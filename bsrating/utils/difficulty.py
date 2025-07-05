

def diff_from_str(diff_str : str):
    assoc = {
        "Easy" :        1,
        "Normal" :      3,
        "Hard" :        5,
        "Expert":       7,
        "ExpertPlus":   9
    }
    
    if diff_str in assoc:
        return assoc[diff_str]
    
    return -1
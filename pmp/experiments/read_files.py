def read_candidates(lines):
    candidates = []
    for l in lines:
        s = l.split()[1:]
        candidates.append((s[0], s[1], 'None'))
    return candidates


def read_voters(lines):
    candidates = []
    for l in lines:
        s = l.split()
        candidates.append((s[0], s[1], 'None'))
    return candidates


def read_preferences(lines):
    preferences = []
    for l in lines:
        s = l.split()
        preferences.append((s[0], s[1], 'None'))
    return preferences

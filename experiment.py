from profiles.ordinal import Ordinal
from rules.sntv import SntvRule

candidates = [x for x in range(4)]

vectors = [
    [0, 1, 2, 3],
    [3, 1, 0, 2],
    [3, 0, 2, 1],
    [1, 0, 2, 3],
    [2, 1, 0, 3],
]

voters = [Ordinal(vectors[i]) for i in range(5)]



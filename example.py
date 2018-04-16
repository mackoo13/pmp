from profiles.ordinal import Ordinal
from rules.sntv import SntvRule

x = Ordinal([1, 0, 2])
scores = [0, 0, 0]
s = SntvRule()

s.score_from_voter(x, scores)
print(scores)

# noinspection PyUnresolvedReferences
from pmp.rules import MultigoalCCBorda, MultigoalTBloc
from pmp.preferences import Ordinal, Profile

n = 2
m = 3
k = 2
orders = [
    [0, 2, 1],
    [1, 0, 2],
    [0, 2, 1],
]

preferences = [Ordinal(o) for o in orders]
candidates = [0, 1, 2]

profile = Profile(candidates, preferences)

rule = MultigoalCCBorda((0, 0))
# rule = MultigoalTBloc((0, 0))

# committee = rule.find_committee(k, profile, method='Bruteforce', criterion='max_appr')
committee = rule.find_committee(k, profile, method='ILP', criterion='max_appr')

print('Selected committees:', list(committee))

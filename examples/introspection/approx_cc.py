from pmp.rules import ChamberlinCourant
from pmp.preferences import Ordinal, Profile

# In case of CCB default is ILP
# Let's give a try Bruteforce implementation

k = 2
orders = [
    [1, 2, 0],
    [2, 1, 0],
    [2, 0, 1],
    [1, 2, 0],
    [1, 0, 2]
]

preferences = [Ordinal(o) for o in orders]
candidates = [0, 1, 2]

profile = Profile(candidates, preferences)

# No thresholds needed for approximation
cc = ChamberlinCourant()

committee_cc = list(cc.find_committee(k, profile))
committee_cc_greedy = list(cc.find_committee(k, profile, method='Approx_Greedy'))
committee_cc_p = list(cc.find_committee(k, profile, method='Approx_P'))

score_cc = cc.committee_score(committee_cc, profile)
score_ccb_greedy = cc.committee_score(committee_cc_greedy, profile)
score_ccb_p = cc.committee_score(committee_cc_p, profile)

print('Selected committees:')
print('CC:          {} \tscore: {}'.format(list(committee_cc), score_cc))
print('CC (Greedy): {} \tscore: {}'.format(list(committee_cc_greedy), score_ccb_greedy))
print('CC (P):      {} \tscore: {}'.format(list(committee_cc_p), score_ccb_p))

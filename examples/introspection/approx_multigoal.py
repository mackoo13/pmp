from pmp.rules import MultigoalCCBorda, Borda, ChamberlinCourant
from pmp.preferences import Ordinal, Profile

k = 4
orders = [
    [1, 5, 4, 3, 2, 0],
    [2, 3, 1, 0, 4, 5],
    [4, 3, 2, 5, 0, 1],
    [1, 2, 5, 4, 0, 3],
    [1, 5, 0, 2, 3, 4]
]

preferences = [Ordinal(o) for o in orders]
candidates = [0, 1, 2, 3, 4, 5]

profile = Profile(candidates, preferences)

# No thresholds needed for approximation
cc = ChamberlinCourant()
b = Borda()
ccb = MultigoalCCBorda((None, None))

committee_cc = list(cc.find_committee(k, profile))
committee_b = list(b.find_committee(k, profile))
committee_ccb_greedy = list(ccb.find_committee(k, profile, method='Approx_Greedy'))
committee_ccb_p = list(ccb.find_committee(k, profile, method='Approx_P'))

score_cc = cc.committee_score(committee_cc, profile)
score_b = b.committee_score(committee_b, profile)
score_ccb_greedy = ccb.committee_score(committee_ccb_greedy, profile)
score_ccb_p = ccb.committee_score(committee_ccb_p, profile)

print('Selected committees:')
print('CC:                {} \tscore: {}'.format(list(committee_cc), score_cc))
print('Borda:             {} \tscore: {}'.format(list(committee_b), score_b))
print('CC+Borda (Greedy): {} \tscore: {}'.format(list(committee_ccb_greedy), score_ccb_greedy))
print('CC+Borda (P):      {} \tscore: {}'.format(list(committee_ccb_p), score_ccb_p))

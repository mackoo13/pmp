def get_best_score(rule, profile, k):
    best_committee = list(rule.find_committee(k, profile))
    return rule.committee_score(best_committee, profile)

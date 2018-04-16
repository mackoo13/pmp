class SntvRule:
    def score_from_voter(self, voter, scores):
        vote = voter.order[0]
        scores[vote] += 1
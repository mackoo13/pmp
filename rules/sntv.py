class SntvRule:
    def score_from_voter(self, voter, scores):
        vote = voter[0]
        scores[vote] += 1
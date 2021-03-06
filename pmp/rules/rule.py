from .tie_breaking import random_winner


class Rule:
    """Scoring rule."""

    def __init__(self, tie_break=random_winner):
        self.tie_break = tie_break

    def __str__(self):
        return self.__class__.__name__

    def find_committee(self, k, profile, random_winning_committee):
        raise NotImplementedError()

    def compute_candidate_scores(self, k, profile):
        """Fill self.scores hash"""
        raise NotImplementedError()

    def compute_committee_score(self, committee, k, profile):
        raise NotImplementedError()

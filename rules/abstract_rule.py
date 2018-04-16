class AbstractRule:
    """ Abstract class for rules
        Methods that should be supplied:
        * score_from_voter(voter, scores)
    """

    def score_from_voter(self, voter, scores):
        raise NotImplementedError("Should have implemented this")

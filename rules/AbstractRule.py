class AbstractRule( object ):
    """ Abstract class for rules """
    def score_from_vote(self, voter, scores):
        raise NotImplementedError("Should have implemented this")

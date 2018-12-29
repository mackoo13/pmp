from .weakly_separable import WeaklySeparable


class Borda(WeaklySeparable):
    """Borda vote scoring rule."""

    def initialise_weights(self, _k, profile):
        self.weights = self._borda_weights(len(profile.candidates))

    def find_committee(self, k, profile):
        self.initialise_weights(k, profile)
        committee = WeaklySeparable.find_committee(self, k, profile)
        return committee

    def compute_score(self, candidate, k, profile):
        self.initialise_weights(k, profile)
        score = WeaklySeparable.compute_score(self, candidate, k, profile)
        return score

    def _borda_weights(self, size):
        return [size - i for i in range(1, size + 1)]

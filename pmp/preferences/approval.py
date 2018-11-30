class Approval:
    """Approval preference profile."""

    def __init__(self, approved):
        self.approved = set(approved)

import random


def random_winner(committees):
    return random.choice(committees)


def lexical_winner(committees):
    committees = [sorted(committee) for committee in committees]
    sorted_committees = sorted(committees)
    return sorted_committees[0]

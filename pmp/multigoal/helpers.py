import numpy as np


def get_distribution_name(distribution):
    if distribution.__name__ == 'generate_uniform':
        return 'square'
    elif distribution.__name__ == 'generate_circle':
        return'circle'
    return 'gauss'


def read_scores(file_path):
    with open(file_path, 'r') as f:
        scores = f.read().strip().split()
        scores = np.array(scores).astype('float')
    return scores
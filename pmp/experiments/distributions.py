def get_distribution_name(distribution):
    if distribution.__name__ == 'generate_uniform':
        return 'square'
    elif distribution.__name__ == 'generate_circle':
        return 'circle'
    elif distribution.__name__ == 'generate_gauss':
        return 'gauss'
    elif distribution.__name__ == 'generate_urn':
        return 'urn'
    elif distribution.__name__ == 'generate_mallows':
        return 'mallows'
    else:
        return distribution.__name__

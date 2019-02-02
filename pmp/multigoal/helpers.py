def get_distribution_name(distribution):
    if distribution.__name__ == 'generate_uniform':
        return 'square'
    elif distribution.__name__ == 'generate_circle':
        return'circle'
    return 'gauss'

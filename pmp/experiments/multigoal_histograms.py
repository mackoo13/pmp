import os

from glob import glob
from cplex.exceptions import CplexSolverError

from pmp.MW2D import mw2d_generate_histogram, mw2d_draw_histogram
from pmp.experiments.experiment import preference_orders, visualize_from_win_file
from pmp.preferences import Profile
from pmp.MW2D.pref import create_pref_orders
from pmp.rules import ChamberlinCourant, Borda, Bloc
from pmp.rules.tbloc import TBloc
from pmp.rules.utils import get_best_score


def generate_winner_files(current_dir, m, n, k, multigoal_rule, percentages,
                          distribution, reps, log_errors=False, methods=None,
                          approximation=False, return_approximations=False):

    if methods is None:
        methods = ['ILP']

    approximations = {method: [] for method in methods}
    rule_name = multigoal_rule.__name__

    if rule_name == 'MultigoalBlocBorda':
        rules = (Bloc(), Borda())
    elif rule_name == 'MultigoalCCBorda':
        rules = (ChamberlinCourant(), Borda())
    else:
        rules = [TBloc(i + 1) for i, _ in enumerate(percentages)]

    perc = '_'.join([str(p) for p in percentages])
    repetition = 1
    while repetition <= reps:
        tmp_filename = 'tmp.in'
        tmp_filename = os.path.join(current_dir, tmp_filename)

        # Generating candidates, voters and their preferences
        if distribution.__name__ == 'generate_uniform':
            voters = distribution(-3, -3, 3, 3, n, 'None')
            candidates = distribution(-3, -3, 3, 3, m, 'None')
            distribution_name = 'square'
        elif distribution.__name__ == 'generate_circle':
            voters = distribution(0, 0, 3, n, 'None')
            candidates = distribution(0, 0, 3, m, 'None')
            distribution_name = 'circle'
        else:
            voters = distribution(0, 0, 1, n, 'None')
            candidates = distribution(0, 0, 1, m, 'None')
            distribution_name = 'gauss'

        preferences = preference_orders(candidates, voters)
        candidates_list = list(range(m))
        profile = Profile(candidates_list, preferences)
        candidates_map = {c: (candidates[c][0], candidates[c][1])for c in candidates_list}

        # Creating temporary file with voters and candidates
        with open(tmp_filename, 'w') as f:
            f.write('{} {}\n'.format(m, n))
            for i, candidate in enumerate(candidates):
                f.write('{}\t{} {}\n'.format(i, candidate[0], candidate[1]))
            for voter in voters:
                f.write('{} {}\n'.format(voter[0], voter[1]))

        # Computing winning committee based on given parameters
        if approximation and not return_approximations:
            rules_bests = [None] * len(methods)
            rules_thresholds = [None] * len(methods)
        else:
            rules_bests = []
            rules_thresholds = []
            for i, p in enumerate(percentages):
                rule_best = get_best_score(rules[i], profile, k)
                rules_bests.append(float(rule_best))
                rule_threshold = rule_best * percentages[i] / 100
                rules_thresholds.append(rule_threshold)

        rule = multigoal_rule(rules_thresholds, log_errors=log_errors)

        for method in methods:
            out_filename = '{}_{}_{}_k{}-{}-{}.win'.format(rule_name, distribution_name, perc, k, method, repetition)
            out_filename = os.path.join(current_dir, out_filename)

            try:
                committee = list(rule.find_committees(k, profile, method=method))
                if approximation and return_approximations:
                    approximations[method].append(
                        rule.committee_score(committee, profile) / rules_bests
                    )

                # Creating winners file
                with open(out_filename, 'w') as out_file:
                    preference = create_pref_orders(tmp_filename, k)
                    out_file.write(preference)
                    for c in committee:
                        out_file.write('{}\t{} {}\n'.format(c, candidates_map[c][0], candidates_map[c][1]))
                print('Generated: {}'.format(out_filename))
                repetition += 1
            except CplexSolverError:
                continue

        os.remove(tmp_filename)

    if approximation and return_approximations:
        return approximations
    else:
        return None


def draw_histogram(current_dir, multigoal_rule, k, percentages, distribution, reps, threshold=None, methods=None):
    if methods is None:
        methods = ['ILP']

    distribution_name = get_distribution_name(distribution)
    perc = '_'.join([str(p) for p in percentages])

    for method in methods:
        winner_filename = '{}_{}_{}_k{}-{}'.format(multigoal_rule.__name__, distribution_name, perc, k, method)
        file_path = os.path.join(current_dir, winner_filename)
        mw2d_generate_histogram(file_path, reps)

        histogram_filename = file_path + '.hist'
        mw2d_draw_histogram(histogram_filename, threshold)

        os.remove(histogram_filename)


def visualize_elections(current_dir, elections_num=None):
    for f in glob(os.path.join(current_dir, '*.win'))[:elections_num]:
        visualize_from_win_file(f)


def delete_winner_files(current_dir):
    for f in glob(os.path.join(current_dir, '*.win')):
        os.remove(f)


def get_distribution_name(distribution):
    if distribution.__name__ == 'generate_uniform':
        return 'square'
    elif distribution.__name__ == 'generate_circle':
        return'circle'
    return 'gauss'

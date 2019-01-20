import os

from glob import glob
from cplex.exceptions import CplexSolverError

from pmp.MW2D import mw2d_generate_histogram, mw2d_draw_histogram
from pmp.experiments.distributions import get_distribution_name
from pmp.experiments.experiment import preference_orders, visualize_from_win_file
from pmp.preferences import Profile
from pmp.MW2D.pref import create_pref_orders
from pmp.rules import ChamberlinCourant, Borda, Bloc
from pmp.rules.tbloc import TBloc
from pmp.rules.utils import get_best_score


def generate_in_file(distribution, m, n, in_filename):
    if os.path.isfile(in_filename):
        return

    if distribution.__name__ == 'generate_uniform':
        voters = distribution(-3, -3, 3, 3, n, 'None')
        candidates = distribution(-3, -3, 3, 3, m, 'None')
    elif distribution.__name__ == 'generate_circle':
        voters = distribution(0, 0, 3, n, 'None')
        candidates = distribution(0, 0, 3, m, 'None')
    elif distribution.__name__ == 'generate_gauss':
        voters = distribution(0, 0, 1, n, 'None')
        candidates = distribution(0, 0, 1, m, 'None')
    else:
        voters = [(0, 0, 'None') for _ in range(n)]
        candidates = [(0, 0, 'None') for _ in range(m)]

    with open(in_filename, 'w') as f:
        f.write('{} {}\n'.format(m, n))
        for i, candidate in enumerate(candidates):
            f.write('{}\t{} {}\n'.format(i, candidate[0], candidate[1]))
        for voter in voters:
            f.write('{} {}\n'.format(voter[0], voter[1]))

    return candidates, voters


def generate_preferences(distribution, candidates, voters, pref_filename):
    m = len(candidates)
    n = len(voters)

    if distribution.__name__ in ['generate_uniform', 'generate_circle', 'generate_gauss']:
        preferences = preference_orders(candidates, voters)
    elif distribution.__name__ == 'generate_urn':
        preferences = distribution(1/float(m), m, n)
    elif distribution.__name__ == 'generate_mallows':
        preferences = distribution(0.4, m, n)
    else:
        raise ValueError

    candidates_list = list(range(m))
    profile = Profile(candidates_list, preferences)
    candidates_map = {c: (candidates[c][0], candidates[c][1])for c in candidates_list}

    with open(pref_filename, 'w') as f:
        for pref in profile.preferences:
            f.write(' '.join([str(pos) for pos in pref.order]) + '\n')

    return profile, candidates_map


def get_best_scores(best_scores_filename, rules, profile, k):
    rules_bests = [get_best_score(rule, profile, k) for rule in rules]

    with open(best_scores_filename, 'w') as out_file:
        out_file.write(' '.join([str(best) for best in rules_bests]))

    return rules_bests


def get_rules(multigoal_rule, percentages):
    rule_name = multigoal_rule.__name__

    if rule_name == 'MultigoalBlocBorda':
        rules = (Bloc(), Borda())
    elif rule_name == 'MultigoalCCBorda':
        rules = (ChamberlinCourant(), Borda())
    else:
        rules = [TBloc(i + 1) for i, _ in enumerate(percentages)]

    return rules


def generate_winner_files(current_dir, m, n, k, multigoal_rule, percentages,
                          distribution, reps, log_errors=False, method='ILP'):

    rule_name = multigoal_rule.__name__
    distribution_name = get_distribution_name(distribution)
    rules = get_rules(multigoal_rule, percentages)

    perc = '_'.join([str(p) for p in percentages])

    repetition = 1
    while repetition <= reps:

        file_prefix = '{}_{}_{}_k{}_n{}_m{}_{}'.format(rule_name, distribution_name, perc, k, n, m, repetition)
        in_filename = os.path.join(current_dir, file_prefix + '.in')
        pref_filename = os.path.join(current_dir, file_prefix + '.pref')
        best_scores_filename = os.path.join(current_dir, file_prefix + '_Best_Scores.score')

        out_filename = '{}_{}'.format(file_prefix, method)
        win_filename = os.path.join(current_dir, out_filename + '.win')
        score_filename = os.path.join(current_dir, out_filename + '.score')

        # Generating the distribution
        candidates, voters = generate_in_file(distribution, m, n, in_filename)
        profile, candidates_map = generate_preferences(distribution, candidates, voters, pref_filename)

        # Best scores for each rule
        rules_bests = get_best_scores(best_scores_filename, rules, profile, k)

        # Computing winning committee based on given parameters
        rules_thresholds = [rule_best * p / 100 for rule_best, p in zip(rules_bests, percentages)]

        if os.path.isfile(win_filename) and os.path.isfile(score_filename):
            repetition += 1
            continue

        rule = multigoal_rule(rules_thresholds, log_errors=log_errors)

        try:
            committee = list(rule.find_committees(k, profile, method=method))

            # Creating winners file
            with open(win_filename, 'w') as out_file:
                preference = create_pref_orders(in_filename, k)
                out_file.write(preference)
                for c in committee:
                    out_file.write('{}\t{} {}\n'.format(c, candidates_map[c][0], candidates_map[c][1]))

            # Creating score file
            with open(score_filename, 'w') as out_file:
                out_file.write(' '.join(rule.committee_score(committee, profile).astype('str')))

            print('Generated: {}'.format(out_filename))
            repetition += 1
        except CplexSolverError:
            continue


def draw_histogram(current_dir, multigoal_rule, k, percentages, distribution, reps, n, m, threshold=None, methods=None):
    if methods is None:
        methods = ['ILP']

    distribution_name = get_distribution_name(distribution)
    perc = '_'.join([str(p) for p in percentages])

    for method in methods:
        winner_filename = '{}_{}_{}_k{}_n{}_m{}_{}'.format(
            multigoal_rule.__name__, distribution_name, perc, k, n, m, method)
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

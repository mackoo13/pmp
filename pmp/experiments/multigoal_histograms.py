import os

from cplex.exceptions import CplexSolverError

from pmp.MW2D import mw2d_generate_histogram, mw2d_draw_histogram
from pmp.experiments.experiment import preference_orders
from pmp.preferences import Profile
from pmp.MW2D.pref import create_pref_orders
from pmp.rules.utils import get_best_score


def generate_winner_files(current_dir, m, n, k, multigoal_rule, rule1, rule2, r1_percentage, r2_percentage,
                          distribution, reps, log_errors=False):
    for repetition in range(1, reps + 1):

        out_filename = '{}_{}_{}_k{}-{}.win'.format(multigoal_rule.__name__, r1_percentage, r2_percentage,
                                                    k, repetition)
        tmp_filename = 'tmp.in'

        # Generating candidates, voters and their preferences
        voters = distribution(-3, -3, 3, 3, n, 'None')
        candidates = distribution(-3, -3, 3, 3, m, 'None')
        preferences = preference_orders(candidates, voters)
        candidates_list = list(range(m))
        profile = Profile(candidates_list, preferences)
        candidates_map = {c: (candidates[c][0], candidates[c][1])for c in candidates_list}

        # Creating temporary file with voters and candidates
        tmp_file_path = os.path.join(current_dir, tmp_filename)
        with open(tmp_filename, 'w') as f:
            f.write('{} {}\n'.format(m, n))
            for i, candidate in enumerate(candidates):
                f.write('{}\t{} {}\n'.format(i, candidate[0], candidate[1]))
            for voter in voters:
                f.write('{} {}\n'.format(voter[0], voter[1]))

        # Computing winning committee based on given parameters
        rule1_best = get_best_score(rule1(), profile, k)
        rule2_best = get_best_score(rule2(), profile, k)
        rule1_threshold = rule1_best * r1_percentage / 100
        rule2_threshold = rule2_best * r2_percentage / 100
        rule = multigoal_rule(s1=rule1_threshold, s2=rule2_threshold, log_errors=log_errors)

        try:
            committee = list(rule.find_committees(k, profile, method='ILP'))
            # Creating winners file
            with open(out_filename, 'w') as out_file:
                preference = create_pref_orders(tmp_file_path, k)
                out_file.write(preference)
                for c in committee:
                    out_file.write('{}\t{} {}\n'.format(c, candidates_map[c][0], candidates_map[c][1]))
            print('Generated: {}'.format(out_filename))

        except CplexSolverError:
            continue
        finally:
            os.remove(tmp_filename)


def draw_histogram(current_dir, multigoal_rule, k, r1, r2, reps, threshold=None):
    winner_filename = '{}_{}_{}_k{}'.format(multigoal_rule.__name__, r1, r2, k)
    file_path = os.path.join(current_dir, winner_filename)
    mw2d_generate_histogram(file_path, reps)

    histogram_filename = file_path + '.hist'
    mw2d_draw_histogram(histogram_filename, threshold)

    os.remove(histogram_filename)


def delete_winner_files(current_dir, multigoal_rule, k, r1, r2, reps):
    for r in range(1, reps + 1):
        winner_filename = '{}_{}_{}_k{}-{}.win'.format(multigoal_rule.__name__, r1, r2, k, r)
        file_path = os.path.join(current_dir, winner_filename)
        try:
            os.remove(file_path)
        except OSError:
            pass


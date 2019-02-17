from pmp.experiments import generate_uniform
from pmp.multigoal import MultigoalExperimentConfig, MultigoalExperiment
from pmp.multigoal.approximation import calculate_approx_ccborda_ratio, draw_approx_ccborda_ratio
from pmp.multigoal.helpers import get_distribution_name
from pmp.rules import MultigoalCCBorda
import os

current_file = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file)

# Configuration
k = 10   # committee_size
m = 100   # candidates number
n = 100   # voters number

repetitions = 30
k_ccs = range(0, k+1)

methods = ['Approx_P', 'Approx_Greedy']
multigoal_rule = MultigoalCCBorda
distribution = generate_uniform

experiments = []
for _ in range(repetitions):
    config = MultigoalExperimentConfig()
    config.add_candidates(distribution(-3, -3, 3, 3, m, 'None'))
    config.add_voters(distribution(-3, -3, 3, 3, n, 'None'))
    config.set_distribution_name(get_distribution_name(distribution))

    experiment = MultigoalExperiment(config)
    experiment.set_multigoal_election(MultigoalCCBorda, k, percent_thresholds=[0, 0])
    experiments.append(experiment)

for repetition, experiment in enumerate(experiments):
    for i, k_cc in enumerate(k_ccs):
        file_prefix = 'kcc' + str(k_cc)
        experiment.set_filename(file_prefix)
        experiment.run(n=1, n_start=repetition+1, methods=methods, k_cc=k_cc, cplex_trials=5,
                       save_in=False, save_out=False, save_best=True, save_win=True, save_score=True)

out_dir = experiments[0].get_generated_dir_path()
file_prefixes = ['kcc' + str(k_cc) for k_cc in k_ccs]
res = calculate_approx_ccborda_ratio(out_dir, file_prefixes, methods, repetitions)
draw_approx_ccborda_ratio(out_dir, res, methods, k_ccs)

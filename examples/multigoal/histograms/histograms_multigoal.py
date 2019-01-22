from pmp.experiments import generate_uniform
from pmp.experiments.multigoal_histograms import visualize_elections
from pmp.multigoal import MultigoalExperimentConfig, MultigoalExperiment
from pmp.multigoal.helpers import get_distribution_name
from pmp.multigoal.visualize import draw_histogram
from pmp.rules import MultigoalBlocBorda

# Configuration
m = 10   # candidates number
n = 20   # voters number
k = 3   # committee_size
repetitions = 10
multigoal_rule = MultigoalBlocBorda
percentages = [10, 10]

distribution = generate_uniform

config = MultigoalExperimentConfig()
config.set_candidates(distribution(-3, -3, 3, 3, m, 'None'))
config.add_voters(distribution(-3, -3, 3, 3, n, 'None'))
config.set_distribution_name(get_distribution_name(distribution))

experiment = MultigoalExperiment(config)
experiment.set_multigoal_election(multigoal_rule, k, percent_thresholds=percentages)
experiment.run(visualization=True, n=repetitions, save_in=True, save_out=True, save_win=True)

out_dir = experiment.get_generated_dir_path()
draw_histogram(out_dir, multigoal_rule, k, percentages, distribution, repetitions, n, m, 'ILP')
visualize_elections(out_dir)

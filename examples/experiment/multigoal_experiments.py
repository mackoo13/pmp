from pmp.multigoal.helpers import get_distribution_name
from pmp.rules import MultigoalBlocBorda, MultigoalCCBorda

try:
    from pmp.multigoal import MultigoalExperiment, MultigoalExperimentConfig
    from pmp.experiments import generate_uniform, impartial
    from pmp.rules.bloc import Bloc
    from pmp.rules.borda import Borda
    from pmp.experiments import FileType
except (ImportError, NameError) as e:
    print("Cannot import pmp. Check whether pmp is installed.\n" + str(e))
    exit()

# Generating voters and candidates using functions and lambdas
distribution = generate_uniform

config = MultigoalExperimentConfig()
config.set_candidates(distribution(-3, -3, 3, 3, 100, 'None'))
config.add_voters(distribution(-3, -3, 3, 3, 10, 'None'))
config.set_distribution_name(get_distribution_name(distribution))

experiment = MultigoalExperiment(config)
experiment.set_multigoal_election(MultigoalCCBorda, [5, 6], 3)
experiment.set_generated_dir_path("bloc_example")
experiment.run(visualization=True, n=2, save_in=True, save_out=True, save_win=True)

# Adding one voter and one candidate
# config = experiment_config.ExperimentConfig()
# config.add_one_candidate((999.88, 11.22, 2.2), 'Be')
# config.add_one_voter((1000, 11, 2))

# experiment = MultigoalExperiment(config)
# experiment.set_election(Borda, 1)
# experiment.run(n=5, save_out=True)

# Impartial
# config = experiment_config.ExperimentConfig()
# config.impartial(4, 10)
# config.add_voters(lambda c: impartial(len(c), 10))

# experiment = MultigoalExperiment(config)
# experiment.set_election(Borda, 2)
# experiment.set_filename("impartial")
# experiment.run(n=3, save_in=True)


import math

from pmp.experiments.multigoal_charts import draw_chart
from pmp.rules import Bloc, Borda, ChamberlinCourant, MultigoalTBloc, MultigoalBlocBorda, MultigoalCCBorda
from pmp.rules.tbloc import TBloc

repetitions = 10
ks = [2, 10, 20, 50]
n = 200
m = 200

for k in ks:
    filename = 'bb-chart-k{}-n{}-m{}'.format(k, n, m)
    draw_chart(filename, k, n, m, repetitions,  Bloc(), Borda(), MultigoalBlocBorda, start=70, step=2, log_errors=False)

    filename = 'ccb-chart-k{}-n{}-m{}'.format(k, n, m)
    draw_chart(filename, k, n, m, repetitions, ChamberlinCourant(), Borda(), MultigoalCCBorda, start=70, step=2,
               log_errors=False)

    filename = 'mbloc(1,k)-chart-k{}-n{}-m{}'.format(k, n, m)
    draw_chart(filename, k, n, m, repetitions, TBloc(1), TBloc(k), MultigoalTBloc, start=0, step=2, log_errors=False)

    k_2 = int(math.floor(k/2))

    filename = 'mbloc(1,k2)-chart-k{}-n{}-m{}'.format(k, n, m)
    draw_chart(filename, k, n, m, repetitions, TBloc(1), TBloc(k_2), MultigoalTBloc, start=0, step=2,
               log_errors=False)

    filename = 'mbloc(k2,k)-chart-k{}-n{}-m{}'.format(k, n, m)
    draw_chart(filename, k, n, m, repetitions, TBloc(k_2), TBloc(k), MultigoalTBloc, start=0, step=2,
               log_errors=False)

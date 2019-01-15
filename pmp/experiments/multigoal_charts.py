

def draw_approximation_charts(out_dir, ms, k_percs, res):
    for im, m in enumerate(ms):
        filename = os.path.join(out_dir, 'approx_m{}'.format(m))
        ks = k_percs * m

        axes = plt.gca()

        axes.set_xlim([0, m])
        axes.set_ylim([0, 1])

        plt.xlabel('k')
        plt.ylabel('approximation')

        plt.plot(ks, res['Approx_Greedy'][im, :])
        plt.plot(ks, res['Approx_P'][im, :])
        plt.legend(['Greedy', 'P'])
        plt.title('Approximation in CC+kB')
        plt.savefig(filename)
        plt.clf()
def dist(x, y):
    return (sum([(x[i] - y[i]) ** 2 for i in range(len(x))])) ** 0.5


def computeDist(v, C):
    m = len(C)
    d = [(j, dist(v, C[j])) for j in range(m)]
    return d


def second(x):
    return x[1]


def preferenceOrders(C, V):
    P = []
    for v in V:
        v_dist = computeDist(v, C)
        v_sorted = sorted(v_dist, key=second)
        v_order = [cand for (cand, dis) in v_sorted]
        P += [v_order]
    return P


def createPrefOrders(C, V, P, k):
    m = len(C)
    n = len(V)
    res = '{} {} {}\n'.format(m, n, k)

    for i in range(len(C)):
        res += '{}\t{} {}\n'.format(i, C[i][0], C[i][1])

    for i in range(len(P)):
        pref = " ".join([str(p) for p in P[i]])
        res += '{}\t{} {}\n'.format(pref, V[i][0], V[i][1])
    return res


def readData(filename):
    with open(filename, 'r') as f:
        data = f.readlines()
        P = []
        C = []
        m, n = data[0].split()
        m = int(m)
        n = int(n)

        for l in data[1:m + 1]:
            _, x, y = l.split()
            C += [(float(x), float(y))]

        for l in data[m + 1:m + n + 1]:
            x, y = l.split()
            P += [(float(x), float(y))]

        return m, n, C, P


def create_pref_orders(filename, k):
    m, n, C, V = readData(filename)

    P = preferenceOrders(C, V)
    return createPrefOrders(C, V, P, k)

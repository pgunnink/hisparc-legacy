import tables

from pylab import *
from numpy import *

def get_front_arrival_time(sim, R, dR, theta):
    query = '(R - dR <= core_distance) & (core_distance < R + dR)'
    c = 3e-1 # m / ns

    t_list = []
    for shower in sim:
        particles = shower.leptons.readWhere(query)
        x = particles[:]['x']
        t = particles[:]['arrival_time']

        dt = x * sin(theta) / c
        t += dt

        t_list.extend(t)

    return array(t_list)

def monte_carlo_timings(n, bins, size):
    x0 = min(bins)
    x1 = max(bins)
    y0 = 0
    y1 = max(n)

    t_list = []
    while len(t_list) < size:
        x = random.uniform(x0, x1)
        y = random.uniform(y0, y1)
        idx = bins.searchsorted(x) - 1
        if y <= n[idx]:
            t_list.append(x)

    return t_list

@vectorize
def my_std_t(data, N):
    sim = data.root.showers.E_1PeV.zenith_22_5
    t = get_front_arrival_time(sim, 30, 5, pi / 8)
    n, bins = histogram(t, bins=linspace(0, 50, 201))
    mct = monte_carlo_timings(n, bins, 10000)
    print "Monte Carlo:", N

    mint_list = []
    i = 0
    while i < len(mct):
        try:
            values = mct[i:i + N]
        except IndexError:
            break
        if len(values) == N:
            mint_list.append(min(values))
        i += N
    return median(mint_list)

def my_std_t_for_R(data, N_list, R_list):
    sim = data.root.showers.E_1PeV.zenith_22_5

    value_list = []
    for N, R in zip(N_list, R_list):
        t = get_front_arrival_time(sim, R, 2, pi / 8)
        n, bins = histogram(t, bins=linspace(0, 50, 201))
        mct = monte_carlo_timings(n, bins, 10000)
        print "Monte Carlo:", N

        mint_list = []
        i = 0
        while i < len(mct):
            try:
                values = mct[i:i + N]
            except IndexError:
                break
            if len(values) == N:
                mint_list.append(min(values))
            i += N
        value_list.append(median(mint_list))
    return array(value_list)

def my_t_draw_something(data, N, num_events):
    sim = data.root.showers.E_1PeV.zenith_22_5
    t = get_front_arrival_time(sim, 30, 5, pi / 8)
    n, bins = histogram(t, bins=linspace(0, 50, 201))
    mct = monte_carlo_timings(n, bins, num_events * N)
    print "Monte Carlo:", N

    mint_list = []
    i = 0
    while i < len(mct):
        try:
            values = mct[i:i + N]
        except IndexError:
            break
        if len(values) == N:
            mint_list.append(min(values))
        i += N
    return mint_list

def plot_R():
    hist(data.root.simulations.E_1PeV.zenith_22_5.shower_0.coincidences.col('r'), bins=100, histtype='step')
    shower = data.root.simulations.E_1PeV.zenith_22_5.shower_0
    ids = shower.observables.getWhereList('(n1 >= 1) & (n3 >= 1) & (n4 >= 1)')
    R = shower.coincidences.readCoordinates(ids, field='r')
    hist(R, bins=100, histtype='step')
    xlabel("Core distance [m]")
    ylabel("Number of events")

    print "mean", mean(R)
    print "median", median(R)

def plot_arrival_times():
    figure()
    sim = data.root.showers.E_1PeV.zenith_22_5
    t = get_front_arrival_time(sim, 30, 2, pi / 8)
    n, bins = histogram(t, bins=linspace(0, 50, 201))
    mct = monte_carlo_timings(n, bins, 100000)
    hist(mct, bins=linspace(0, 20, 101), histtype='step')

    mint = my_t_draw_something(data, 2, 100000)
    hist(mint, bins=linspace(0, 20, 101), histtype='step')

    xlabel("Arrival time [ns]")
    ylabel("Number of events")



if __name__ == '__main__':
    if not 'data' in globals():
        data = tables.openFile('master-ch4v2.h5')

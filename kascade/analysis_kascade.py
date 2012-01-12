from __future__ import division

import tables
from itertools import izip
import os.path

import progressbar as pb

from pylab import *

from scipy import integrate
from scipy.special import erf

import utils

from sapphire.analysis import DirectionReconstruction, BinnedDirectionReconstruction


DATADIR = '../analysis/plots'

USE_TEX = True

TIMING_ERROR = 4
#TIMING_ERROR = 7

# For matplotlib plots
if USE_TEX:
    rcParams['font.serif'] = 'Computer Modern'
    rcParams['font.sans-serif'] = 'Computer Modern'
    rcParams['font.family'] = 'sans-serif'
    rcParams['figure.figsize'] = [4 * x for x in (1, 2. / 3)]
    rcParams['figure.subplot.left'] = 0.175
    rcParams['figure.subplot.bottom'] = 0.175
    rcParams['font.size'] = 10
    rcParams['legend.fontsize'] = 'small'
    rcParams['text.usetex'] = True


def do_reconstruction_plots(data):
    """Make plots based upon earlier reconstructions"""

    table = data.root.reconstructions

    plot_uncertainty_mip(table)
    plot_uncertainty_zenith(table)
#
    plot_phi_reconstruction_results_for_MIP(table, 1)
    plot_phi_reconstruction_results_for_MIP(table, 2)
    boxplot_theta_reconstruction_results_for_MIP(table, 1)
    boxplot_theta_reconstruction_results_for_MIP(table, 2)
    boxplot_phi_reconstruction_results_for_MIP(table, 1)
    boxplot_phi_reconstruction_results_for_MIP(table, 2)
    boxplot_arrival_times(table, 1)
    boxplot_arrival_times(table, 2)
    boxplot_core_distances_for_mips(table)
#    plot_detection_efficiency_vs_R_for_angles(1)
#    plot_detection_efficiency_vs_R_for_angles(2)
#    plot_reconstruction_efficiency_vs_R_for_angles(1)
#    plot_reconstruction_efficiency_vs_R_for_angles(2)
#    plot_reconstruction_efficiency_vs_R_for_mips()

def plot_uncertainty_mip(table):
    rec = DirectionReconstruction

    # constants for uncertainty estimation
    station = table.attrs.cluster.stations[0]
    r1, phi1 = station.calc_r_and_phi_for_detectors(1, 3)
    r2, phi2 = station.calc_r_and_phi_for_detectors(1, 4)

    THETA = deg2rad(22.5)
    DTHETA = deg2rad(5.)
    DN = .1

    figure()
    x, y, y2 = [], [], []
    for N in range(1, 6):
        x.append(N)
        events = table.readWhere('(abs(min_n134 - N) <= DN) & (abs(reference_theta - THETA) <= DTHETA)')
        print len(events),
        errors = events['reference_theta'] - events['reconstructed_theta']
        # Make sure -pi < errors < pi
        errors = (errors + pi) % (2 * pi) - pi
        errors2 = events['reference_phi'] - events['reconstructed_phi']
        # Make sure -pi < errors2 < pi
        errors2 = (errors2 + pi) % (2 * pi) - pi
        y.append(std(errors))
        y2.append(std(errors2))

    print
    print "mip: min_n134, theta_std, phi_std"
    for u, v, w in zip(x, y, y2):
        print u, v, w
    print

    # Simulation data
    sx, sy, sy2 = loadtxt(os.path.join(DATADIR, 'DIR-plot_uncertainty_mip.txt'))

    # Uncertainty estimate
    ex = linspace(1, 5, 50)
    phis = linspace(-pi, pi, 50)
    phi_errsq = mean(rec.rel_phi_errorsq(pi / 8, phis, phi1, phi2, r1, r2))
    theta_errsq = mean(rec.rel_theta1_errorsq(pi / 8, phis, phi1, phi2, r1, r2))
    ey = TIMING_ERROR * std_t(ex) * sqrt(phi_errsq)
    ey2 = TIMING_ERROR * std_t(ex) * sqrt(theta_errsq)

    # Plots
    plot(x, rad2deg(y), '^', label="Theta")
    plot(sx, rad2deg(sy), '^', label="Theta (sim)")
    plot(ex, rad2deg(ey2), label="Estimate Theta")
    plot(x, rad2deg(y2), 'v', label="Phi")
    plot(sx, rad2deg(sy2), 'v', label="Phi (sim)")
    plot(ex, rad2deg(ey), label="Estimate Phi")

    # Labels etc.
    xlabel("$N_{MIP} \pm %.1f$" % DN)
    ylabel("Angle reconstruction uncertainty [deg]")
    title(r"$\theta = 22.5^\circ \pm %d^\circ$" % rad2deg(DTHETA))
    legend(numpoints=1)
    utils.saveplot()
    print

def plot_uncertainty_zenith(table):
    rec = DirectionReconstruction

    # constants for uncertainty estimation
    station = table.attrs.cluster.stations[0]
    r1, phi1 = station.calc_r_and_phi_for_detectors(1, 3)
    r2, phi2 = station.calc_r_and_phi_for_detectors(1, 4)

    N = 2
    DTHETA = deg2rad(1.)
    DN = .1

    figure()
    rcParams['text.usetex'] = False
    x, y, y2 = [], [], []
    for theta in 0, 5, 22.5, 35:
        x.append(theta)
        THETA = deg2rad(theta)
        events = table.readWhere('(abs(min_n134 - N) <= DN) & (abs(reference_theta - THETA) <= DTHETA)')
        print theta, len(events),
        errors = events['reference_theta'] - events['reconstructed_theta']
        # Make sure -pi < errors < pi
        errors = (errors + pi) % (2 * pi) - pi
        errors2 = events['reference_phi'] - events['reconstructed_phi']
        # Make sure -pi < errors2 < pi
        errors2 = (errors2 + pi) % (2 * pi) - pi
        y.append(std(errors))
        y2.append(std(errors2))
    print
    print "zenith: theta, theta_std, phi_std"
    for u, v, w in zip(x, y, y2):
        print u, v, w
    print

    # Simulation data
    sx, sy, sy2 = loadtxt(os.path.join(DATADIR, 'DIR-plot_uncertainty_zenith.txt'))

    # Uncertainty estimate
    ex = linspace(0, deg2rad(35), 50)
    phis = linspace(-pi, pi, 50)
    ey, ey2, ey3 = [], [], []
    for t in ex:
        ey.append(mean(rec.rel_phi_errorsq(t, phis, phi1, phi2, r1, r2)))
        ey3.append(mean(rec.rel_phi_errorsq(t, phis, phi1, phi2, r1, r2)) * sin(t) ** 2)
        ey2.append(mean(rec.rel_theta1_errorsq(t, phis, phi1, phi2, r1, r2)))
    ey = TIMING_ERROR * sqrt(array(ey))
    ey3 = TIMING_ERROR * sqrt(array(ey3))
    ey2 = TIMING_ERROR * sqrt(array(ey2))

    # Plots
    plot(x, rad2deg(y), '^', label="Theta")
    plot(sx, rad2deg(sy), '^', label="Theta (sim)")
    plot(rad2deg(ex), rad2deg(ey2), label="Estimate Theta")
    # Azimuthal angle undefined for zenith = 0
    plot(x[1:], rad2deg(y2[1:]), 'v', label="Phi")
    plot(sx[1:], rad2deg(sy2[1:]), 'v', label="Phi (sim)")
    plot(rad2deg(ex), rad2deg(ey), label="Estimate Phi")
    plot(rad2deg(ex), rad2deg(ey3), label="Estimate Phi * sin(Theta)")

    # Labels etc.
    xlabel(r"Shower zenith angle [deg $\pm %d^\circ$]" % rad2deg(DTHETA))
    ylabel("Angle reconstruction uncertainty [deg]")
    title(r"$N_{MIP} = 2 \pm %.1f$" % DN)
    ylim(0, 100)
    legend(numpoints=1)
    if USE_TEX:
        rcParams['text.usetex'] = True
    utils.saveplot()
    print

# Time of first hit pamflet functions
Q = lambda t, n: ((.5 * (1 - erf(t / sqrt(2)))) ** (n - 1)
                  * exp(-.5 * t ** 2) / sqrt(2 * pi))

expv_t = vectorize(lambda n: integrate.quad(lambda t: t * Q(t, n)
                                                      / n ** -1,
                                            - inf, +inf))
expv_tv = lambda n: expv_t(n)[0]
expv_tsq = vectorize(lambda n: integrate.quad(lambda t: t ** 2 * Q(t, n)
                                                        / n ** -1,
                                              - inf, +inf))
expv_tsqv = lambda n: expv_tsq(n)[0]

std_t = lambda n: sqrt(expv_tsqv(n) - expv_tv(n) ** 2)

def plot_phi_reconstruction_results_for_MIP(table, N):
    THETA = deg2rad(22.5)
    DTHETA = deg2rad(5.)

    events = table.readWhere('(min_n134 >= N) & (abs(reference_theta - THETA) <= DTHETA)')
    sim_phi = events['reference_phi']
    r_phi = events['reconstructed_phi']

    figure()
    plot_2d_histogram(rad2deg(sim_phi), rad2deg(r_phi), 180)
    xlabel(r"$\phi_{KASCADE}$ [deg]")
    ylabel(r"$\phi_{reconstructed}$ [deg]")
    title(r"$N_{MIP} \geq %d, \quad \theta = 22.5^\circ \pm %d^\circ$" % (N, rad2deg(DTHETA)))

    utils.saveplot(N)

def boxplot_theta_reconstruction_results_for_MIP(table, N):
    figure()

    DTHETA = deg2rad(1.)

    angles = [0, 5, 22.5, 35]
    r_dtheta = []
    for angle in angles:
        theta = deg2rad(angle)
        sel = table.readWhere('(min_n134 >= N) & (abs(reference_theta - theta) <= DTHETA)')
        r_dtheta.append(rad2deg(sel[:]['reconstructed_theta'] - sel[:]['reference_theta']))

    boxplot(r_dtheta, sym='', positions=angles, widths=2.)

    xlabel(r"$\theta_{KASCADE}$ [deg]")
    ylabel(r"$\theta_{reconstructed} - \theta_{KASCADE}$ [deg]")
    title(r"$N_{MIP} \geq %d$" % N)

    axhline(0)
    ylim(-20, 25)

    utils.saveplot(N)

def boxplot_phi_reconstruction_results_for_MIP(table, N):
    figure()

    THETA = deg2rad(22.5)
    DTHETA = deg2rad(5.)

    bin_edges = linspace(-180, 180, 18)
    x, r_dphi = [], []
    for low, high in zip(bin_edges[:-1], bin_edges[1:]):
        rad_low = deg2rad(low)
        rad_high = deg2rad(high)
        query = '(min_n134 >= N) & (rad_low < reference_phi) & (reference_phi < rad_high) & (abs(reference_theta - THETA) <= DTHETA)'
        sel = table.readWhere(query)
        dphi = sel[:]['reconstructed_phi'] - sel[:]['reference_phi']
        dphi = (dphi + pi) % (2 * pi) - pi
        r_dphi.append(rad2deg(dphi))
        x.append((low + high) / 2)

    boxplot(r_dphi, positions=x, widths=1 * (high - low), sym='')

    xlabel(r"$\phi_{KASCADE}$ [deg]")
    ylabel(r"$\phi_{reconstructed} - \phi_{KASCADE}$ [deg]")
    title(r"$N_{MIP} \geq %d, \quad \theta = 22.5^\circ \pm %d^\circ$" % (N, rad2deg(DTHETA)))

    xticks(linspace(-180, 180, 9))
    axhline(0)

    utils.saveplot(N)

def boxplot_arrival_times(table, N):
    figure()

    THETA = deg2rad(0)
    DTHETA = deg2rad(5.)

    bin_edges = linspace(0, 100, 10)
    x, arrival_times = [], []
    for low, high in zip(bin_edges[:-1], bin_edges[1:]):
        query = '(min_n134 >= N) & (low <= r) & (r < high) & (abs(reference_theta - THETA) <= DTHETA)'
        sel = table.readWhere(query)
        t2 = sel[:]['t2']
        t1 = sel[:]['t1']
        ct1 = t1.compress((t1 > -999) & (t2 > -999))
        ct2 = t2.compress((t1 > -999) & (t2 > -999))
        print len(t1), len(t2), len(ct1), len(ct2)
        arrival_times.append(ct2 - ct1)
        x.append((low + high) / 2)

    boxplot(arrival_times, positions=x, widths=1 * (high - low), sym='')

    xlabel("Core distance [m]")
    ylabel("Arrival time difference $t_2 - t_1$ [ns]")
    title(r"$N_{MIP} \geq %d, \quad \theta = 0^\circ \pm %d^\circ$" % (N, rad2deg(DTHETA)))

    xticks(arange(0, 100.5, 10))

    utils.saveplot(N)

def boxplot_core_distances_for_mips(table):
    THETA = deg2rad(22.5)
    DTHETA = deg2rad(5.)
    DN = .1

    r_list = []
    for N in range(1, 5):
        sel = table.readWhere('(abs(min_n134 - N) <= DN) & (abs(reference_theta - THETA) <= DTHETA)')
        r = sel[:]['r']
        r_list.append(r)

    figure()
    boxplot(r_list)
    xticks(range(1, 5))
    xlabel("Minimum number of particles $\pm %.1f$" % DN)
    ylabel("Core distance [m]")
    title(r"$\theta = 22.5^\circ \pm %d^\circ$" % rad2deg(DTHETA))

    ylim(0, 100)

    utils.saveplot()

def plot_detection_efficiency_vs_R_for_angles(N):
    figure()

    bin_edges = linspace(0, 100, 20)
    x = (bin_edges[:-1] + bin_edges[1:]) / 2.

    for angle in [0, 5, 22.5, 35]:
        angle_str = str(angle).replace('.', '_')
        shower_group = '/simulations/E_1PeV/zenith_%s' % angle_str

        efficiencies = []
        for low, high in zip(bin_edges[:-1], bin_edges[1:]):
            shower_results = []
            for shower in data.listNodes(shower_group):
                sel_query = '(low <= r) & (r < high)'
                coinc_sel = shower.coincidences.readWhere(sel_query)
                ids = coinc_sel['id']
                obs_sel = shower.observables.readCoordinates(ids)
                assert (obs_sel['id'] == ids).all()

                o = obs_sel
                sel = obs_sel.compress((o['n1'] >= N) & (o['n3'] >= N) &
                                       (o['n4'] >= N))
                shower_results.append(len(sel) / len(obs_sel))
            efficiencies.append(mean(shower_results))

        plot(x, efficiencies, label=r'$\theta = %s^\circ$' % angle)

    xlabel("Core distance [m]")
    ylabel("Detection efficiency")
    title(r"$N_{MIP} \geq %d$" % N)
    legend()

    utils.saveplot(N)

def plot_reconstruction_efficiency_vs_R_for_angles(N):
    group = data.root.reconstructions.E_1PeV

    figure()

    bin_edges = linspace(0, 100, 10)
    x = (bin_edges[:-1] + bin_edges[1:]) / 2.

    for angle in [0, 5, 22.5, 35]:
        angle_str = str(angle).replace('.', '_')
        shower_group = '/simulations/E_1PeV/zenith_%s' % angle_str
        reconstructions = group._f_getChild('zenith_%s' % angle_str)

        efficiencies = []
        for low, high in zip(bin_edges[:-1], bin_edges[1:]):
            shower_results = []
            for shower in data.listNodes(shower_group):
                sel_query = '(low <= r) & (r < high)'
                coinc_sel = shower.coincidences.readWhere(sel_query)
                ids = coinc_sel['id']
                obs_sel = shower.observables.readCoordinates(ids)
                assert (obs_sel['id'] == ids).all()

                o = obs_sel
                sel = obs_sel.compress((o['n1'] >= N) & (o['n3'] >= N) &
                                       (o['n4'] >= N))
                shower_results.append(len(sel))
            ssel = reconstructions.readWhere('(min_n134 >= N) & (low <= r) & (r < high)')
            efficiencies.append(len(ssel) / sum(shower_results))

        plot(x, efficiencies, label=r'$\theta = %s^\circ$' % angle)

    xlabel("Core distance [m]")
    ylabel("Reconstruction efficiency")
    title(r"$N_{MIP} \geq %d$" % N)
    legend()

    utils.saveplot(N)

def plot_reconstruction_efficiency_vs_R_for_mips():
    reconstructions = data.root.reconstructions.E_1PeV.zenith_22_5

    figure()

    bin_edges = linspace(0, 100, 10)
    x = (bin_edges[:-1] + bin_edges[1:]) / 2.

    for N in range(1, 5):
        shower_group = '/simulations/E_1PeV/zenith_22_5'

        efficiencies = []
        for low, high in zip(bin_edges[:-1], bin_edges[1:]):
            shower_results = []
            for shower in data.listNodes(shower_group):
                sel_query = '(low <= r) & (r < high)'
                coinc_sel = shower.coincidences.readWhere(sel_query)
                ids = coinc_sel['id']
                obs_sel = shower.observables.readCoordinates(ids)
                assert (obs_sel['id'] == ids).all()

                o = obs_sel
                sel = o.compress(amin(array([o['n1'], o['n3'], o['n4']]), 0) == N)

                shower_results.append(len(sel))
            ssel = reconstructions.readWhere('(min_n134 == N) & (low <= r) & (r < high)')
            print sum(shower_results), len(ssel), len(ssel) / sum(shower_results)
            efficiencies.append(len(ssel) / sum(shower_results))

        plot(x, efficiencies, label=r'$N_{MIP} = %d' % N)

    xlabel("Core distance [m]")
    ylabel("Reconstruction efficiency")
    title(r"$\theta = 22.5^\circ$")
    legend()

    utils.saveplot()

def plot_2d_histogram(x, y, bins):
    H, xedges, yedges = histogram2d(x, y, bins)
    imshow(H.T, extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]],
           origin='lower left', interpolation='lanczos', aspect='auto')
    colorbar()


if __name__ == '__main__':
    # invalid values in arcsin will be ignored (nan handles the situation
    # quite well)
    np.seterr(invalid='ignore', divide='ignore')

    try:
        data
    except NameError:
        data = tables.openFile('kascade.h5', 'r')

    utils.set_prefix("KAS-")
    do_reconstruction_plots(data)

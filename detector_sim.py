""" HiSPARC detector simulation

    This simulation takes an Extended Air Shower simulation ground
    particles file and uses that to simulate numerous showers hitting a
    HiSPARC detector station.  Only data of one shower is used, but by
    randomly selecting points on the ground as the position of a station,
    the effect of the same shower hitting various positions around the
    station is simulated.

"""
from __future__ import division

import tables
import os.path

import clusters
from simulations import BaseSimulation


DATAFILE = 'data-e15.h5'


if __name__ == '__main__':
    try:
        data
    except NameError:
        data = tables.openFile(DATAFILE, 'a')

    sim = 'E_1PeV/zenith_0'
    cluster = clusters.SimpleCluster()
    simulation = BaseSimulation(cluster, data,
                                os.path.join('/showers', sim, 'leptons'),
                                os.path.join('/simulations', sim),
                                R=100, N=100)
    simulation.run()
    simulation.store_observables()

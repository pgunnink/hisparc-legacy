import sys
sys.path.append('/home/pieter/sapphire')

import logging
from math import pi

import tables
import numpy as np

from sapphire.kascade import StoreKascadeData, KascadeCoincidences
from sapphire.analysis import process_events
from sapphire import clusters
from sapphire.analysis.direction_reconstruction import KascadeDirectionReconstruction

import pdb

class Master(object):
    hisparc_group = '/hisparc/cluster_kascade/station_601'
    kascade_group = '/kascade'

    def __init__(self, data_filename, kascade_filename):
        self.data = tables.openFile(data_filename, 'a')
        self.kascade_filename = kascade_filename

    def main(self):
        self.store_cluster_instance()
        self.read_and_store_kascade_data()
        self.search_for_coincidences()
        self.process_events(process_events.ProcessIndexedEvents,destination='events_with_traces')
        #self.process_events(process_events.ProcessIndexedEventsWithLINT,
        #                    'lint_events')
        #self.reconstruct_direction('events', '/reconstructions')
        self.reconstruct_direction('events_with_traces', '/reconstructions_offsets_new3',
                                   correct_offsets=False)
        #self.reconstruct_direction('lint_events', '/lint_reconstructions')
        #self.reconstruct_direction('lint_events', '/lint_reconstructions_offsets',
        #                           correct_offsets=True)

    def store_cluster_instance(self):
        group = self.data.getNode(self.hisparc_group)

        if 'cluster' not in group._v_attrs:
            cluster = clusters.SingleStation()
            cluster.set_xyalpha_coordinates(65., 20.82, pi)

            group._v_attrs.cluster = cluster

    def read_and_store_kascade_data(self):
        """Read KASCADE data into analysis file"""

        print "Reading KASCADE data"

        try:
            kascade = StoreKascadeData(self.data, self.hisparc_group,
                                       self.kascade_group,
                                       self.kascade_filename)
        except RuntimeError, msg:
            print msg
            return
        else:
            kascade.read_and_store_data()

    def search_for_coincidences(self):
        hisparc = self.hisparc_group
        kascade = self.kascade_group

        try:
            coincidences = KascadeCoincidences(self.data, hisparc, kascade)
        except RuntimeError, msg:
            print msg
            return
        else:
            print "Searching for coincidences"
            coincidences.search_coincidences(timeshift=-13.180220188,
                                             dtlimit=1e-3)
            print "Storing coincidences"
            coincidences.store_coincidences()
            print "Done."

    def process_events(self, process_cls, destination=None):
        print "Processing HiSPARC events"

        c_index = self.data.getNode(self.kascade_group, 'c_index')
        index = c_index.col('h_idx')

        process = process_cls(self.data, self.hisparc_group, index)
        try:
            process.process_and_store_results(destination, overwrite=True)
            pdb.set_trace()
        except RuntimeError, msg:
            print msg
            return

    def reconstruct_direction(self, source, destination, correct_offsets=False):
        print "Reconstructing shower directions"

        offsets = None
        if correct_offsets:
            process = process_events.ProcessEvents(self.data, self.hisparc_group)
            offsets = process.determine_detector_timing_offsets()

        try:
            reconstruction = KascadeDirectionReconstruction(self.data,
                                                            destination,
                                                            min_n134=0.)
        except RuntimeError, msg:
            print msg
            return
        else:
            reconstruction.reconstruct_angles(self.hisparc_group,
                                              self.kascade_group, source,
                                              offsets)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    np.seterr(invalid='ignore', divide='ignore')

    master = Master('/mnt/shared/kascade.h5', '/mnt/shared/HiSparc-new.dat.gz')
    master.main()

import tables


class HisparcEvent(tables.IsDescription):
    event_id = tables.UInt64Col()
    timestamp = tables.Time32Col()
    nanoseconds = tables.UInt32Col()
    ext_timestamp = tables.UInt64Col()
    pulseheights = tables.Int16Col(shape=4, dflt=-9999)
    integrals = tables.Int32Col(shape=4, dflt=-9999)
    n_peaks = tables.Int32Col(shape=4, dflt=-9999)
    traces = tables.Int32Col(shape=4, dflt=-1)


class Coincidence(tables.IsDescription):
    event_id = tables.UInt64Col()
    k_event_id = tables.UInt64Col()
    timestamp = tables.Time32Col()
    nanoseconds = tables.UInt32Col()
    ext_timestamp = tables.UInt64Col()
    pulseheights = tables.Int16Col(shape=4, dflt=-9999)
    integrals = tables.Int32Col(shape=4, dflt=-9999)
    n_peaks = tables.Int32Col(shape=4, dflt=-9999)
    traces = tables.Int32Col(shape=4, dflt=-1)
    k_timestamp = tables.Time32Col()
    k_nanoseconds = tables.UInt32Col()
    k_ext_timestamp = tables.UInt64Col()
    k_energy = tables.FloatCol()
    k_core_pos = tables.FloatCol(shape=2)
    k_zenith = tables.FloatCol()
    k_azimuth = tables.FloatCol()
    k_Num_e = tables.FloatCol()
    k_Num_mu = tables.FloatCol()
    k_dens_e = tables.FloatCol(shape=4)
    k_dens_mu = tables.FloatCol(shape=4)
    k_P200 = tables.FloatCol()
    k_T200 = tables.FloatCol()

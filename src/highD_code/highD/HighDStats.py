
import pandas as pd
from .PlotHelper import Histogram
from .ManeuverFilter import *


# this class provides statistics for a single highD dataset 
# the location of vehicle (x, y) are the top left corner of the vehicle !!!Important!!!

class HighDStats():
    def __init__(self, DataContainer):

        self.data_container = DataContainer
        print("Inside HighD again stats")       
        pass

    def find_initial_states(self):

        df_dict_list = []
        tracksMeta = self.data_container.tracksMeta
        tracks = self.data_container.tracks

        print("tracksMeta col ", tracksMeta.columns)
        print("tracks col ", tracks.columns)

        trackIDs = tracksMeta['id']

        for id in trackIDs:
            track_meta = tracksMeta[tracksMeta['id'] == id]

            initial_frame_num = track_meta['initialFrame'].values[0]
            initial_frame = tracks[tracks['id'] == id]
            initial_frame = initial_frame[initial_frame['frame'] == initial_frame_num]

            v_type = track_meta['class'].values[0]
            init_lane = initial_frame['laneId'].values[0]
            init_speed = initial_frame['xVelocity'].values[0]
            init_acceleration = initial_frame['xAcceleration'].values[0]

            df_dict = {'id': id,
                       'vType': v_type,
                       'initLane': init_lane,
                       'initSpeed': init_speed, 
                       'initAcceleration': init_acceleration}
            df_dict_list.append(df_dict)
            print(df_dict)

    def min_velocity_distribution(self):
        tracksMeta = self.data_container.tracksMeta.copy()
        tracksMeta['minXVelocity'] = tracksMeta['minXVelocity'] * 3.6
        Histogram.plotMetricsDF(tracksMeta, 'minXVelocity', xlabel='Min Velocity (km/h)', bins=100, kde=True)
        pass

    def max_velocity_distribution(self):
        tracksMeta = self.data_container.tracksMeta.copy()
        tracksMeta['maxXVelocity'] = tracksMeta['maxXVelocity'] * 3.6
        Histogram.plotMetricsDF(tracksMeta, 'maxXVelocity', xlabel='Max Velocity (km/h)', bins=100, kde=True)
        pass

    def mean_velocity_distribution(self):
        tracksMeta = self.data_container.tracksMeta.copy()
        tracksMeta['meanXVelocity'] = tracksMeta['meanXVelocity'] * 3.6
        Histogram.plotMetricsDF(tracksMeta, 'meanXVelocity', xlabel='Mean Velocity (km/h)', bins=100, kde=True)
        pass

    def min_distance_headway(self):
        tracksMeta = self.data_container.tracksMeta.copy()
        Histogram.plotMetricsDF(tracksMeta, 'minDHW', xlabel='Min Distance Headway (m)', bins=100, kde=True)
        pass

    def min_time_headway(self):
        tracksMeta = self.data_container.tracksMeta.copy()
        tracksMeta = tracksMeta[tracksMeta['minTHW'] > 0]
        Histogram.plotMetricsDF(tracksMeta, 'minTHW', xlabel='Min Time Headway (s)', bins=100, kde=True)
        pass

    def min_ttc(self):
        tracksMeta = self.data_container.tracksMeta.copy()
        tracksMeta = tracksMeta[tracksMeta['minTTC'] > 0]
        tracksMeta = tracksMeta[tracksMeta['minTTC'] < 200]
        Histogram.plotMetricsDF(tracksMeta, 'minTTC', xlabel='Min TTC (s)', bins=100, kde=True)
        pass

    def min_acceleration(self):
        tracksMeta = self.data_container.tracksMeta.copy()
        tracks = self.data_container.tracks.copy()

        # group tracks by id
        grouped_tracks = tracks.groupby('id')
        

        Histogram.plotMetricsDF(tracksMeta, 'minXAcceleration', xlabel='Min Acceleration (m/s^2)', bins=100, kde=True)
        pass
 
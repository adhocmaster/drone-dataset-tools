
import pandas as pd

from .PlotHelper import Histogram



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
            # print('initial_frame_num ', initial_frame_num)
            df_dict = {'id': id,
                       'vType': v_type,
                       'initLane': init_lane,
                       'initSpeed': init_speed, 
                       'initAcceleration': init_acceleration}
            df_dict_list.append(df_dict)
            print(df_dict)

    
    def min_velocity_distribution(self):

        df = pd.DataFrame(columns=['MinVelocity'])
        tracksMeta = self.data_container.tracksMeta

        for track in tracksMeta:
            print(track['id'])
        
        pass

           

    




    
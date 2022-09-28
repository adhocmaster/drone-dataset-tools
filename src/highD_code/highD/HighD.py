import copy
import pandas as pd
from data_management.read_csv import *
import cv2
import os
import time
import statistics

from .DataContainer import DataContainer
from .Visual import Visualizer
from .ManeuverFilter import *


SCALE_FACTOR = 4 * 0.10106

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0,255,255)
MAGENTA = (255,0,255)



class HighD:
    def __init__(self, 
                 id, 
                 image_path, 
                 recordingMeta_path, 
                 tracksMeta_path, 
                 tracks_path,
                 output_path):
        
        self.id = id
        self.name = 'highD_' + str(id) 
        print('collecting data for highway with ID ',self.id)

        self.image = self.read_image(image_path)
        self.recordingMeta = self.read_recordingMeta_csv(recordingMeta_path)
        self.tracksMeta = self.read_trackMeta_csv(tracksMeta_path)
        self.tracks = self.read_track_csv(tracks_path)

        self.data_processor = DataContainer(self.recordingMeta,
                                            self.tracksMeta,
                                            self.tracks)

        self.recordingMeta_dict = self.data_processor.recordingMeta_dict
        self.tracksMeta_dict = self.data_processor.tracksMeta_dict
        self.track_dict = self.data_processor.tracks_dict

        if output_path is None:
            self.output_path = '../../output'
        else:
            self.output_path = output_path

        self.left2right, self.right2left = self.split_dataset()

        self.car_follow = None
        self.lane_change = None

        pass

    
    @property
    def numCars(self):
        return self.recordingMeta['numCars']

    @property
    def numTrucks(self):
        return self.recordingMeta['numTrucks']

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    # reads data from the dataset based on given path
    #  return image array using cv2 (RGB)
    def read_image(self, image_path):
        return cv2.imread(image_path)

    #  returns data frame object
    def read_track_csv(self, tracks_path):
        df_obj = pd.read_csv(tracks_path)
        return df_obj

    def read_trackMeta_csv(self, tracksMeta_path):
        df_obj = pd.read_csv(tracksMeta_path)
        return df_obj

    def read_recordingMeta_csv(self, recordingMeta_path):
        df_obj = pd.read_csv(recordingMeta_path)
        return df_obj
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# all then getter functions for the data
    def get_highway_image(self):
        if self.image is None:
            print('image is not loaded')
            return None
        return self.image

    def get_recordingMeta(self):
        if self.recordingMeta is None:
            print('recordingMeta is not loaded')
            return None
        return self.recordingMeta

    def get_tracksMeta(self):
        if self.tracksMeta is None:
            print('tracksMeta is not loaded')
            return None
        return self.tracksMeta
    
    def get_tracks(self):
        if self.tracks is None:
            print('tracks is not loaded')
            return None
        return self.tracks
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 


    def draw_frame(self, frame_id, ego_id, target_id, ego_color, target_color):
        
        # print(self.tracks)
        data = Visualizer.draw_frame(image=self.image,
                                     tracks=self.tracks,
                                     frame_id=frame_id,
                                     ego_id=ego_id,
                                     target_id=target_id,
                                     ego_color=ego_color,
                                     target_color=target_color)

        return data

    def create_and_save_video_from_frames(self, start, end, fps=25, video_name=None):
        Visualizer.create_video_from_frames(image=self.image,
                                            tracks=self.tracks,
                                            start=start,
                                            end=end,
                                            fps=fps,
                                            video_name=video_name,
                                            output_dir=self.output_path)
        pass

    def create_and_save_video_for_agent(self, agent_id, fps=25, video_name=None):
        Visualizer.create_video_for_agent(image=self.image,
                                          tracks=self.tracks,
                                          tracksMeta=self.tracksMeta,
                                          agent_id=agent_id,
                                          fps=fps,
                                          video_name=video_name,
                                          output_dir=self.output_path)
        pass


    def create_and_save_video_with_two_agents(self, agent_id, target_id, fps=25, video_name=None):
        Visualizer.create_video_with_two_agents(image=self.image,
                                                tracks=self.tracks,
                                                tracksMeta=self.tracksMeta,
                                                agent_id=agent_id,
                                                target_id=target_id,
                                                fps=fps,
                                                video_name=video_name,
                                                output_dir=self.output_path)
        pass
                

    def filter_car_following(self, ego_type, preceding_type, thw_lower_bound, thw_upper_bound):
        self.car_follow = find_car_following(self.tracksMeta_dict, 
                                             self.track_dict, 
                                             ego_type, 
                                             preceding_type,
                                             thw_lower_bound,
                                             thw_upper_bound)
        return self.car_follow

    def filter_lane_change(self):
        self.lane_change = get_lane_change_trajectory(self.tracksMeta_dict, self.track_dict)
        return self.lane_change

    def lane_change_stats(self):
        result = find_lane_changes(self.tracksMeta_dict, self.track_dict)
        return result

    
    def find_initial_state(self):

        meta_data = self.tracksMeta_dict
        data = self.track_dict

        init_states = []
        for id in range(1, len(meta_data)+1):
            veh_id = meta_data[id].get('id')
            veh_class = meta_data[id].get('class')
            veh_length = meta_data[id].get('width')
            veh_init_frame = meta_data[id].get('initialFrame')
            veh_init_lane = self.get_initial_lane(id)
            veh_init_pos = self.get_initial_position(id)
            veh_init_speed = self.get_initial_speed(id)
            # record the behaviour
            init_states.append(
                {"id": veh_id,
                "length": veh_length,
                "class": veh_class,
                "initial_frame": veh_init_frame,
                "initial_lane": veh_init_lane,
                "initial_position": veh_init_pos,
                "initial_speed": veh_init_speed
                })
        return init_states


    def get_initial_lane(self, id):
        
        data = self.track_dict
        for i in range(0, len(data)):
            if data[i].get('id') == id:
                lane = data[i].get('laneId')[0]
                return lane


    def get_initial_position(self, id):

        meta_data = self.tracksMeta_dict
        data = self.track_dict
        # print('length of the data ' , len(data))
        for i in range(0, len(data)):
            # print('ID ', data[i].get('id'), id, type(data[i].get('id')), type(id))
            if data[i].get('id') == id:
                # print('true', meta_data[id].get('drivingDirection'))
                if meta_data[id].get('drivingDirection') == 2:
                    pos = data[i].get('bbox')[0][0] + data[i].get('bbox')[0][2]
                elif meta_data[id].get('drivingDirection') == 1:
                    pos = data[i].get('bbox')[0][0]
                return pos


    def get_initial_speed(self, id):

        data = self.track_dict
        for i in range(0, len(data)):
            if data[i].get('id') == id:
                speed = data[i].get('xVelocity')[0]
                return speed

    def split_dataset(self):
        df = self.tracksMeta
        l2r = df.loc[(df["drivingDirection"] == 1)]
        r2l = df.loc[(df["drivingDirection"] == 2)]

        agent_l2r = l2r['id'].values
        agent_r2l = r2l['id'].values

        l2r_df = self.tracks.loc[(self.tracks["id"].isin(agent_l2r))]
        r2l_df = self.tracks.loc[(self.tracks["id"].isin(agent_r2l))]
        
        return l2r_df, r2l_df



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
from config import *
from .HighDStats import HighDStats




class HighD:
    def __init__(self, 
                 data_container: DataContainer):
        
        self.id = data_container.id

        self.image = data_container.image
        self.recordingMeta = data_container.recordingMeta
        self.tracksMeta = data_container.tracksMeta
        self.tracks = data_container.tracks

        self.recordingMeta_dict = data_container.recordingMeta_dict
        self.tracksMeta_dict = data_container.tracksMeta_dict
        self.track_dict = data_container.tracks_dict

        self.output_path = OUTPUT_DIRECTORY

        self.highD_stats = HighDStats(data_container)

        # self.left2right, self.right2left = self.split_dataset()

        self.car_follow = None
        self.lane_change = None

        pass

    def get_highway_image(self):
        return self.image

    def get_recordingMeta(self):
        return self.recordingMeta

    def get_tracksMeta(self):
        return self.tracksMeta
    
    def get_tracks(self):
        return self.tracks


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


    # This function filters the car vehicle following scenarios 
    # total 4 types of interaction is possible between two vehicles
    # (Car, Car), (Car, Truck), (Truck, Car), (Truck, Truck)
    # scenario criticality can be defined suing Time Head Way (THW)
    # THW is the time gap between two vehicles with leading vehicle stopped 
    # THW = (x_l - x_f) / v_f

    def filter_car_following(self, ego_type, preceding_type, thw_lower_bound, thw_upper_bound):
        if self.car_follow is None:
            self.car_follow = find_car_following(self.tracksMeta_dict, 
                                                self.track_dict, 
                                                ego_type, 
                                                preceding_type,
                                                thw_lower_bound,
                                                thw_upper_bound)
        return self.car_follow



    # def filter_lane_change(self):
    #     self.lane_change = get_lane_change_trajectory(self.tracksMeta_dict, self.track_dict)
    #     return self.lane_change

    # def lane_change_stats(self):
    #     result = find_lane_changes(self.tracksMeta_dict, self.track_dict)
    #     return result


#     def split_dataset(self):
#         df = self.tracksMeta
#         l2r = df.loc[(df["drivingDirection"] == 1)]
#         r2l = df.loc[(df["drivingDirection"] == 2)]

#         agent_l2r = l2r['id'].values
#         agent_r2l = r2l['id'].values

#         l2r_df = self.tracks.loc[(self.tracks["id"].isin(agent_l2r))]
#         r2l_df = self.tracks.loc[(self.tracks["id"].isin(agent_r2l))]
        
#         return l2r_df, r2l_df



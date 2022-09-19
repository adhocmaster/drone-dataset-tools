import copy
import pandas as pd
from data_management.read_csv import *
import cv2
import os
import time
import statistics
from ManeuverFilter import *


SCALE_FACTOR = 4 * 0.10106

class HighD:
    def __init__(self, 
                 id, 
                 image_path, 
                 recordingMeta_path, 
                 tracksMeta_path, 
                 tracks_path,
                 output_path):
        self.id = id
        print('collecting data for highway with ID ',self.id)

        self.image = self.read_image(image_path)
        self.recordingMeta = self.read_recordingMeta_csv(recordingMeta_path)
        self.tracksMeta = self.read_trackMeta_csv(tracksMeta_path)
        self.tracks = self.read_track_csv(tracks_path)

        if output_path is None:
            self.output_path = '../../output'
        else:
            self.output_path = output_path

        self.left2right, self.right2left = self.split_dataset()

        self.recordingMeta_dict = self.process_recordingMeta()
        self.tracksMeta_dict = self.process_tracksMeta()
        self.track_dict = self.process_tracks()


        self.car_follow = None
        self.lane_change = None

        pass

    
    @property
    def numCars(self):
        return self.recordingMeta['numCars']

    @property
    def numTrucks(self):
        return self.recordingMeta['numTrucks']

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

    def draw_frame_with_id(self, frame_id, ego_id=None, target_id=None):

        #  deep copy of the image
        image = copy.deepcopy(self.image)

        #  get the frame from the tracks
        df_frames = self.tracks
        df_frames = df_frames[df_frames['frame'] == frame_id]

        if ego_id is not None:
            df_ego = df_frames[df_frames['id'] == ego_id]
            df_bbox = df_ego[['x', 'y', 'width', 'height']]
            df_bbox = df_bbox / SCALE_FACTOR
            x = int(df_bbox['x'])
            y = int(df_bbox['y'])
            width = int(df_bbox['width'])
            height = int(df_bbox['height'])
            cv2.rectangle(image, (x, y), (x+width, y+height), (0, 0, 255), 2)
            # filter the other boxes
            df = df_frames[df_frames['id'] != ego_id]
        elif target_id is not None:
            df_target = df_frames[df_frames['id'] == ego_id]
            df_bbox = df_target[['x', 'y', 'width', 'height']]
            df_bbox = df_bbox / SCALE_FACTOR
            x = int(df_bbox['x'])
            y = int(df_bbox['y'])
            width = int(df_bbox['width'])
            height = int(df_bbox['height'])
            cv2.rectangle(image, (x, y), (x+width, y+height), (255, 0, 0), 2)
            # filter the other boxes
            df = df_frames[df_frames['id'] != target_id]
        else:
            df = df_frames

        df_bbox = df[['x', 'y', 'width', 'height']]
        df_bbox = df_bbox / SCALE_FACTOR

        #  drawing non ego vehicles
        for index, row in df_bbox.iterrows():
            x = int(row['x'])
            y = int(row['y'])
            width = int(row['width'])
            height = int(row['height'])
            cv2.rectangle(image, (x, y), (x+width, y+height), (0, 255, 0), 2)
        
        return image


    def create_video_from_frames(self, start, end, fps=25, video_name=None, ego_id=None):



        frameSize = (1022, 92)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')

        if video_name is None:
            video_name = str(int(round(time.time() * 1000))) + '.avi'
        else:
            video_name = str(video_name) + '.avi'
        
        print('creating video with name ', video_name)

        out = cv2.VideoWriter(os.path.join(self.output_path, video_name), fourcc, 25, frameSize)
        for i in range(start, end + 1):
            img = self.draw_frame_with_id(i, ego_id)
            img = cv2.resize(img, frameSize)
            out.write(img)
        
        out.release()
        
        pass

    

    def create_video_for_agent(self, video_name, agent_id):

        df = self.tracks
        df = df.loc[(df["id"] == agent_id)]
        frames = df["frame"].values
        start = frames[0]
        end = frames[-1]
        self.create_video_from_frames(start, end, fps=25, video_name=video_name, ego_id=agent_id)
        pass

    def create_video_car_follow_maneuver(self):
        if self.car_follow is None:
            self.car_follow = self.filter_car_following()
        
        for i in range(len(self.car_follow)):
            
            ego_id = self.car_follow[i]['ego_id']
            pred_id = self.car_follow[i]['pred_id']

            video_name = str(self.id) + '_car_follow_' + str(ego_id) + '_' + str(pred_id)

            start = self.car_follow[i]['following_start']
            end = self.car_follow[i]['following_end']

            self.create_video_from_frames(start, end, 25, video_name, ego_id)
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

    #  processing fucntions
    
    def process_tracksMeta(self):
        df = self.tracksMeta
        static_dictionary = {}
        for i_row in range(df.shape[0]):
            track_id = int(df['id'][i_row])
            static_dictionary[track_id] = {'id': track_id,
                                           'width': int(df[WIDTH][i_row]),
                                           'height': int(df[HEIGHT][i_row]),
                                           'initialFrame': int(df[INITIAL_FRAME][i_row]),
                                           'finalFrame': int(df[FINAL_FRAME][i_row]),
                                           'numFrames': int(df[NUM_FRAMES][i_row]),
                                           'class': str(df[CLASS][i_row]),
                                           'drivingDirection': float(df[DRIVING_DIRECTION][i_row]),
                                           'traveledDistance': float(df[TRAVELED_DISTANCE][i_row]),
                                           'minXVelocity': float(df[MIN_X_VELOCITY][i_row]),
                                           'maxXVelocity': float(df[MAX_X_VELOCITY][i_row]),
                                           'meanXVelocity': float(df[MEAN_X_VELOCITY][i_row]),
                                           'minDHW': float(df[MIN_TTC][i_row]),
                                           'minTHW': float(df[MIN_THW][i_row]),
                                           'minTTC': float(df[MIN_DHW][i_row]),
                                           'numLaneChanges': int(df[NUMBER_LANE_CHANGES][i_row]),
                                           }
        return static_dictionary

    def process_tracks(self):

        df = self.tracks
        grouped = df.groupby([TRACK_ID], sort=False)
        # Efficiently pre-allocate an empty list of sufficient size
        tracks = [None] * grouped.ngroups
        current_track = 0
        for group_id, rows in grouped:
            bounding_boxes = np.transpose(np.array([rows['x'].values,
                                                    rows['y'].values,
                                                    rows['width'].values,
                                                    rows['height'].values]))
            tracks[current_track] = {'id': np.int64(group_id),  # for compatibility, int would be more space efficient
                                     'frame': rows[FRAME].values,
                                     'bbox': bounding_boxes,
                                     'xVelocity': rows['xVelocity'].values,
                                     'yVelocity': rows['yVelocity'].values,
                                     'xAcceleration': rows['xAcceleration'].values,
                                     'yAcceleration': rows['yAcceleration'].values,
                                     'frontSightDistance': rows['frontSightDistance'].values,
                                     'backSightDistance': rows['backSightDistance'].values,
                                     'thw': rows['thw'].values,
                                     'ttc': rows['ttc'].values,
                                     'dhw': rows['dhw'].values,
                                     'precedingXVelocity': rows['precedingXVelocity'].values,
                                     'precedingId': rows['precedingId'].values,
                                     'followingId': rows['followingId'].values,
                                     'leftFollowingId': rows['leftFollowingId'].values,
                                     'leftAlongsideId': rows['leftAlongsideId'].values,
                                     'leftPrecedingId': rows['leftPrecedingId'].values,
                                     'rightFollowingId': rows['rightFollowingId'].values,
                                     'rightAlongsideId': rows['rightAlongsideId'].values,
                                     'rightPrecedingId': rows['rightPrecedingId'].values,
                                     'laneId': rows['laneId'].values
                                     }
            current_track = current_track + 1
        return tracks


    def process_recordingMeta(self):

        df = self.recordingMeta

        extracted_meta_dictionary = {'id': int(df['id'][0]),
                                 'frameRate': int(df['frameRate'][0]),
                                 'locationId': int(df['locationId'][0]),
                                 'speedLimit': float(df['speedLimit'][0]),
                                 'month': str(df['month'][0]),
                                 'weekDay': str(df['weekDay'][0]),
                                 'startTime': str(df['startTime'][0]),
                                 'duration': float(df['duration'][0]),
                                 'totalDrivenDistance': float(df['totalDrivenDistance'][0]),
                                 'totalDrivenTime': float(df['totalDrivenTime'][0]),
                                 'numVehicles': int(df['numVehicles'][0]),
                                 'numCars': int(df['numCars'][0]),
                                 'numTrucks': int(df['numTrucks'][0]),
                                 'upperLaneMarkings': np.fromstring(df['upperLaneMarkings'][0], sep=";"),
                                 'lowerLaneMarkings': np.fromstring(df['lowerLaneMarkings'][0], sep=";")}

        return extracted_meta_dictionary
        
    

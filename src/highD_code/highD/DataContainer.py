
import numpy as np

class DataContainer():
    def __init__(self, recordingMeta, tracksMeta, tracks):
        self.recordingMeta = recordingMeta
        self.tracksMeta = tracksMeta
        self.tracks = tracks

        self.recordingMeta_dict = self.process_recordingMeta()
        self.tracksMeta_dict = self.process_tracksMeta()
        self.tracks_dict = self.process_tracks()

        pass

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




    def process_tracksMeta(self):
        df = self.tracksMeta
        static_dictionary = {}
        for i_row in range(df.shape[0]):
            track_id = int(df['id'][i_row])
            static_dictionary[track_id] = {'id': track_id,
                                           'width': int(df['width'][i_row]),
                                           'height': int(df['height'][i_row]),
                                           'initialFrame': int(df['initialFrame'][i_row]),
                                           'finalFrame': int(df['finalFrame'][i_row]),
                                           'numFrames': int(df['numFrames'][i_row]),
                                           'class': str(df['class'][i_row]),
                                           'drivingDirection': float(df['drivingDirection'][i_row]),
                                           'traveledDistance': float(df['traveledDistance'][i_row]),
                                           'minXVelocity': float(df['minXVelocity'][i_row]),
                                           'maxXVelocity': float(df['maxXVelocity'][i_row]),
                                           'meanXVelocity': float(df['meanXVelocity'][i_row]),
                                           'minDHW': float(df['minDHW'][i_row]),
                                           'minTHW': float(df['minTHW'][i_row]),
                                           'minTTC': float(df['minTTC'][i_row]),
                                           'numLaneChanges': int(df['numLaneChanges'][i_row]),
                                           }
        return static_dictionary



    def process_tracks(self):

        df = self.tracks
        grouped = df.groupby(['id'], sort=False)
        # Efficiently pre-allocate an empty list of sufficient size
        tracks = [None] * grouped.ngroups
        current_track = 0
        for group_id, rows in grouped:
            bounding_boxes = np.transpose(np.array([rows['x'].values,
                                                    rows['y'].values,
                                                    rows['width'].values,
                                                    rows['height'].values]))
            tracks[current_track] = {'id': np.int64(group_id),  # for compatibility, int would be more space efficient
                                     'frame': rows['frame'].values,
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





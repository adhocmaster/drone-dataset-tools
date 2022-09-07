import pandas as pd
from data_management.read_csv import *

class HighD:
    def __init__(self, id, image, recordingMeta, tracksMeta, tracks):
        self.id = id
        self.image = image
        self.recordingMeta = recordingMeta
        self.tracksMeta = tracksMeta
        self.tracks = tracks
        pass

    def read_track_csv(self):
        data_Path = {"input_path": self.tracks}
        data_dict = read_track_csv(data_Path)
        df_obj = pd.DataFrame(data_dict)
        return df_obj

    def read_trackMeta_csv(self):
        data_Path = {"input_static_path": self.tracksMeta}
        data_dict = read_static_info(data_Path)
        df_obj = pd.DataFrame(data_dict)
        return df_obj

    def read_recordingMeta_csv(self):
        data_Path = {"input_meta_path": self.recordingMeta}
        data_dict = read_meta_info(data_Path)
        df_obj = pd.DataFrame(data_dict)
        return df_obj

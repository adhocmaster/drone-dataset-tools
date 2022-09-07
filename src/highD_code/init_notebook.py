import os, sys
from HighD import HighD

currentFolder = os.path.abspath('')
try:
    sys.path.remove(str(currentFolder))
except ValueError: # Already removed
    pass

# projectFolder = 'E:\\AV\\DataSetExploration\\drone-dataset-tools\\src'

projectFolder = 'C:\\Users\\abjaw\\Documents\\GitHub\\drone-dataset-tools\\src\\highD_code'


sys.path.append(str(projectFolder))
os.chdir(projectFolder)
print( f"current working dir{os.getcwd()}")




def get_path_dict(folder_path):

    image_id = '_highway.png'
    meta_id = '_recordingMeta.csv'
    track_meta_id = '_tracksMeta.csv'
    track_id = '_tracks.csv'

    path_dict = {}
    for i in range(1, 61):
        if i < 10:
            id = '0' + str(i)
        else:
            id = str(i)
        image_name =  os.path.join(folder_path, id + image_id)
        recordingMeta_name = os.path.join(folder_path, id + meta_id)
        tracksMeta_name = os.path.join(folder_path, id + track_meta_id)
        tracks_name = os.path.join(folder_path, id + track_id)

        path_object = HighD(id, image_name, recordingMeta_name, tracksMeta_name, tracks_name)

        path_dict[i] = path_object
    return path_dict

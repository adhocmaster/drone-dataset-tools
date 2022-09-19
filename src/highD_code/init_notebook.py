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
        image_path =  os.path.join(folder_path, id + image_id)
        recordingMeta_path = os.path.join(folder_path, id + meta_id)
        tracksMeta_path = os.path.join(folder_path, id + track_meta_id)
        tracks_path = os.path.join(folder_path, id + track_id)

        path_object = {
            'image_path': image_path,
            'recordingMeta_path': recordingMeta_path,
            'tracksMeta_path': tracksMeta_path,
            'tracks_path': tracks_path
        }

        path_dict[i] = path_object
    
    # print(path_dict)

    return path_dict

def read_highD_data(id, path_dict, outputDir):
    
    highD_data = HighD(id, 
                       path_dict[id]['image_path'], 
                       path_dict[id]['recordingMeta_path'], 
                       path_dict[id]['tracksMeta_path'], 
                       path_dict[id]['tracks_path'],
                       outputDir)

    return highD_data

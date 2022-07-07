import pandas as pd
import numpy as np
import glob
import os

# objects
# 25 backpack
# 26 umbrella
# 40 bottle
# 12 stop sign
# 57 chair
# 75 clock

# params
DIST_THRES = {
    'backpack': 1,
    'umbrella': 1,
    'bottle': 1,
    'stop sign': 1,
    'chair': 1,
    'clock': 1
}
# DIST_THRES = {
#     'bicycle': 1,
#     'person': 1,
#     'stop sign': 1
# }



dirname = "/home/team6/detection_data"
objects_name = ['backpack', 'umbrella', 'bottle', 'stop sign', 'chair', 'clock'] # note the stop sign
# objects_name = ['bicycle', 'stop sign', 'person']
fields = ['DetectionID', 'Confidence', 'Position x', 'Position y', 'Position z', 'Label']
result = {}
for key in objects_name:
    result[key] = []    # loc, confidence

filenames = glob.glob(dirname + '*.csv')
# print(filenames)
for filename in filenames:
    df = pd.read_csv(filename)
    for obj_name in objects_name:
        same_objs = df.loc[df['Label'] == obj_name]
        for i, row in same_objs.iterrows():
            loc = np.array([row['Position x'], row['Position y'], row['Position z']])
            if len(result[obj_name]) == 0:
                result[obj_name].append([loc, row['Confidence'], row['DetectionID']])
                print(f'generate new object of {obj_name}, num: {len(result[obj_name])}')
            else:
                renew_flag = 0
                for j in range(len(result[obj_name])):
                    if np.linalg.norm(loc - result[obj_name][j][0]) < (DIST_THRES[obj_name]):
                        renew_flag = 1
                        if row['Confidence'] > result[obj_name][j][1]:
                            result[obj_name][j][0] = loc
                            result[obj_name][j][1] = row['Confidence']
                            result[obj_name][j][2] = row['DetectionID']
                            # print(f'renew location of {obj_name}')
                            
                if renew_flag == 0:
                    # if obj_name == 'bicycle':
                        # print(result[obj_name])
                    result[obj_name].append([loc, row['Confidence'], row['DetectionID']])
                    print(f'generate new object of {obj_name}, num: {len(result[obj_name])}')

for key in objects_name:
    print(key, len(result[key]))

# write to csv file
output  = []
save_dir = '/home/team6'
save_filename = 'output_filtered_objects.csv'
for key in objects_name:
    for i in range(len(result[key])):
        output.append([key, result[key][i][0], result[key][i][1], result[key][i][2]])
df = pd.DataFrame(output, columns=['Label', 'Location', 'Confidence', 'DetectionID'])
df.to_csv(os.path.join(save_dir, save_filename), index=False)
    

#!/usr/bin/env python
import rospy
import tf
from geometry_msgs.msg import PoseStamped
import pandas as pd

if __name__ == '__main__':
    rospy.init_node('point_transform_to_origin')
    listener = tf.TransformListener()
    now = rospy.Time(0)
    listener.waitForTransform(
        "/map", "/origin", rospy.Time(), rospy.Duration(1000))

    p1 = PoseStamped()
    p1.header.frame_id = "/map"
    p1.pose.orientation.w = 1.0

    df = pd.read_csv("some_file.csv")
    new_df = pd.DataFrame(
        columns=['Label', 'DetectionID', 'locx', 'locy', 'locz'])

    for index, row in df.iterrows():
        p1.pose.position.x = row["locx"]
        p1.pose.position.y = row["locy"]
        p1.pose.position.z = row["locz"]
        p1_tf = listener.transformPose("/origin", p1)
        position_tf = p1_tf.pose.position
        new_row = [row['Label'], row["DetectionID"], p1_tf.pose.position.x,
                   p1_tf.pose.position.y, p1_tf.pose.position.z]
        new_df.loc[index] = new_row

    df.to_csv("final_artifacts.csv", index=False)

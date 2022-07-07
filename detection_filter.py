#!/usr/bin/env python
from object_detection_msgs.msg import ObjectDetectionInfoArray
import rospy
import tf
from geometry_msgs.msg import PoseStamped, Point
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import cv2
import pandas as pd
import datetime
import os

CONFIDENCE_THR = 0.7 #TODO: determine threshold
DURATION = 10 #TODO: determine duration

class object_filter:
    def __init__(self):
        rospy.init_node('detection_filter')
        # self.take_images = rospy.get_param('~take_images')
        self.take_images = True
        # self.confidence_threshold = rospy.get_param('~confidence_threshold')
        # self.file_save_interval = rospy.get_param('~file_save_interval')
        # self.detection_rate = rospy.get_param('~detection_rate')

        self.bridge = CvBridge()
        self.df = []
        self.tf_listener = tf.TransformListener()
        self.detection_listener = rospy.Subscriber("/object_detector/detection_info", ObjectDetectionInfoArray, self.detection_filter_callback)

        if self.take_images:
            self.image_listener = rospy.Subscriber("/object_detector/detections_in_image", Image, self.image_callback)
        self.start_stamp = 0
        self.curr_stamp = 0
        self.detection_id = 1
        self.save_image = False
        # self.dirname = "/home/sophiehebe/detection_data"   #TODO: change folder
        self.dirname = "/home/team6/detection_data"   #TODO: change folder

    def detection_filter_callback(self, msg):
        # (trans, rot) = self.tf_listener.lookupTransform('camera_pose_frame', 'base_link', rospy.Time(0))
        # print(trans,rot)

        # transform waypoints to global frame
        p1 = PoseStamped()
        p1.header.frame_id = msg.header.frame_id
        p1.pose.orientation.w = 1.0  # Neutral orientation #TODO:which orientation do we need

        timestamp = msg.header.stamp.secs
        self.curr_stamp = timestamp
        # print(f"Timestamp is: {timestamp}")

        # get all the recognized objects
        for detection in msg.info:
            confidence = detection.confidence
            position = detection.position
            label = detection.class_id

            if confidence > CONFIDENCE_THR and position.z > 0.0:  # filter out based on confidence (or other metrics?)
                p1.pose.position = position
                p1_tf = self.tf_listener.transformPose("/tracking_camera_odom", p1) #TODO: change to map
                # print(f"Position of the object before transform: {p1}")
                # print(f"Position of the object after transform: {p1_tf}")
                position_tf = p1_tf.pose.position
                self.df.append([self.detection_id, label, position_tf.x, position_tf.y, position_tf.z, confidence])
                self.detection_id += 1
                self.save_image = True

        print(f"self.currentstamp = {self.curr_stamp}")
        if (self.curr_stamp - self.start_stamp) > DURATION:
            os.makedirs(self.dirname, exist_ok=True)
            filename = 'detection_' + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")+'.csv'
            print(filename)
            # field names
            fields = ['DetectionID', 'Label', 'Confidence', 'Position x', 'Position y', 'Position z']
            df = pd.DataFrame(self.df, columns=fields)
            df.to_csv(os.path.join(self.dirname, filename), index=False)
            self.start_stamp = self.curr_stamp
            self.df = []

    def image_callback(self, msg):
        print("Received an image!")
        # Convert your ROS Image message to OpenCV2
        if self.save_image:
            cv2_img = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            filename = f"camera_img_{str(self.detection_id)}.jpg"
            cv2.imwrite(os.path.join(self.dirname, filename), cv2_img)
        self.save_image = False

if __name__ == "__main__":
    filter = object_filter()
    rospy.spin()
    print(filter.df)






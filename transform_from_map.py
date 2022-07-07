#!/usr/bin/env python
import rospy
import tf
from geometry_msgs.msg import PoseWithCovarianceStamped 
import time  

def handle_message(msg):
    print(msg)
    init_x = msg.pose.pose.position.x
    init_y = msg.pose.pose.position.y
    init_quaternion = msg.pose.pose.orientation
    br = tf.TransformBroadcaster()
    while not rospy.is_shutdown():
        br.sendTransform((init_x, init_y, 0), (init_quaternion.x, init_quaternion.y,
                                                init_quaternion.z, init_quaternion.w),
                                    rospy.Time.now(),
                                    "origin",
                                    "map")
        time.sleep(1)

if __name__ == '__main__':
   rospy.init_node('artifact_tf')
   rospy.Subscriber('/initialpose', PoseWithCovarianceStamped, handle_message)
   rospy.spin()



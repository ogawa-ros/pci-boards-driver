#! /usr/bin/env python3

name = "cpz7204"

#----
import sys
import time
import threading
import rospy
import std_msgs.msg
import pyinterface


class CPZ7204(object):

    def __init__(self):
        self.rsw_id = rospy.get_param("~rsw_id")

        self.pub = rospy.Publisher(
                        name = "/cpz7204_rsw{0}/di{1}".format(self.rsw_id),
                        data_class = std_msgs.msg.Bool,
                        latch = True,
                        queue_size = 1,
                    )

        self.sub = rospy.Subscriber(
                        name = "/cpz7204_rsw{0}/do{1}".format(self.rsw_id),
                        data_class = std_msgs.msg.Bool,
                        callback = self.output_function,
                        queue_size = 1, 
                    )

        try:
            self.dio = pyinterface.open(7204, self.rsw_id)
        except OSError as e:
            rospy.logerr(e, name, self.rsw_id)
            sys.exit()
        
        pass

    def output_function(self, req, ch):
        self.dio.output_point(req.data ,int(ch))
        return

    def pub_function(self):
        while not rospy.is_shutdown():
            for ch, pub in zip(self.ch_list_di, self.pub):
                ret = self.dio.input_point(int(ch), 1)
                pub.publish(ret)
            
            time.sleep(0.001)
            continue
        
        return


if __name__ == "__main__":
    rospy.init_node(name)
    cpz = CPZ7204()

    pub_thread = threading.Thread(
            target = cpz.pub_function,
            daemon = True,
        )
    pub_thread.start()

    rospy.spin()

#! /usr/bin/env python3

import sys
import time
import numpy
import pyinterface
import threading

import rospy
from std_msgs.msg import Float64
from std_msgs.msg import Int64
from std_msgs.msg import Bool

class cpz7415v_controller(object):

    motion = {
        'x': {
            'clock':  0, 'acc_mode': '', 'low_speed': 0,
            'speed': 0, 'acc': 0, 'dec': 0, 'step': 0
        },
        'y': {
            'clock':  0, 'acc_mode': '', 'low_speed': 0,
            'speed': 0, 'acc': 0, 'dec': 0, 'step': 0
        },
        'z': {
            'clock':  0, 'acc_mode': '', 'low_speed': 0,
            'speed': 0, 'acc': 0, 'dec': 0, 'step': 0
        },
        'u': {
            'clock':  0, 'acc_mode': '', 'low_speed': 0,
            'speed': 0, 'acc': 0, 'dec': 0, 'step': 0
        }
    }

    move_mode = {'x': '', 'y': '', 'z': '', 'u': ''}

    last_position = {'x': 0, 'y': 0, 'z': 0, 'u': 0}

    last_speed = {'x': 0, 'y': 0, 'z': 0, 'u': 0}

    do_status = {1:0, 2:0, 3:0, 4:0}

    
    def __init__(self):
        ###=== Define member-variables ===###
        self.rate = rospy.get_param('~rate')
        self.rsw_id = rospy.get_param('~rsw_id')
        self.node_name = rospy.get_param('~node_name')
        self.move_mode['x'] = rospy.get_param('~mode_x')
        self.move_mode['y'] = rospy.get_param('~mode_y')
        self.move_mode['z'] = rospy.get_param('~mode_z')
        self.move_mode['u'] = rospy.get_param('~mode_u')
        self.step_cmd_flag = False
        self.speed_cmd_flag = False
        self.busy_flag = False
        self.step_cmd_li = []
        self.speed_cmd_li = []
        ###=== Create instance ===###
        try: self.mot = pyinterface.open(7415, self.rsw_id)
        except OSError as e:
            rospy.logerr("{e.strerror}. node={node_name}, rsw={rsw_id}".
                         format(self.node_name, self.rsw_id))
            sys.exit()
        ###=== Setting the board ===###
        self.mot.initialize(axis='xyzu')
        self.motion['x']['clock'] = rospy.get_param('~clock_x')
        self.motion['x']['acc_mode'] = rospy.get_param('~acc_mode')
        self.motion['x']['low_speed'] = rospy.get_param('~low_speed')
        self.motion['x']['speed'] = rospy.get_param('~speed')
        self.motion['x']['acc'] = rospy.get_param('~acc')
        self.motion['x']['dec'] = rospy.get_param{'~dec')
        self.motion['x']['step'] = rospy.get_param('~step')
        self.motion['y']['clock'] = rospy.get_param('~clock_x')
        self.motion['y']['acc_mode'] = rospy.get_param('~acc_mode')
        self.motion['y']['low_speed'] = rospy.get_param('~low_speed')
        self.motion['y']['speed'] = rospy.get_param('~speed')
        self.motion['y']['acc'] = rospy.get_param('~acc')
        self.motion['y']['dec'] = rospy.get_param{'~dec')
        self.motion['y']['step'] = rospy.get_param('~step')
        self.motion['z']['clock'] = rospy.get_param('~clock_x')
        self.motion['z']['acc_mode'] = rospy.get_param('~acc_mode')
        self.motion['z']['low_speed'] = rospy.get_param('~low_speed')
        self.motion['z']['speed'] = rospy.get_param('~speed')
        self.motion['z']['acc'] = rospy.get_param('~acc')
        self.motion['z']['dec'] = rospy.get_param{'~dec')
        self.motion['z']['step'] = rospy.get_param('~step')
        self.motion['u']['clock'] = rospy.get_param('~clock_x')
        self.motion['u']['acc_mode'] = rospy.get_param('~acc_mode')
        self.motion['u']['low_speed'] = rospy.get_param('~low_speed')
        self.motion['u']['speed'] = rospy.get_param('~speed')
        self.motion['u']['acc'] = rospy.get_param('~acc')
        self.motion['u']['dec'] = rospy.get_param{'~dec')
        self.motion['u']['step'] = rospy.get_param('~step')
        self.mot.set_motion(axis='x', mode=self.move_mode['x'], motion=self.motion)
        self.mot.set_motion(axis='y', mode=self.move_mode['y'], motion=self.motion)
        self.mot.set_motion(axis='z', mode=self.move_mode['z'], motion=self.motion)
        self.mot.set_motion(axis='u', mode=self.move_mode['u'], motion=self.motion)
        ###=== Define topic ===###
        topic_step_x_cmd = '/{0}_rsw{1}_x_step_cmd'.format(self.node_name, self.rsw_id)
        topic_step_x =  '/{0}_rsw{1}_x_step'.format(self.node_name, self.rsw_id)
        topic_speed_x_cmd = '/{0}_rsw{1}_x_speed_cmd'.format(self.node_name, self.rsw_id)
        topic_speed_x = '/{0}_rsw{1}_x_speed'.format(self.node_name, self.rsw_id)
        topic_step_y_cmd = '/{0}_rsw{1}_y_step_cmd'.format(self.node_name, self.rsw_id)
        topic_step_y =  '/{0}_rsw{1}_y_step'.format(self.node_name, self.rsw_id)
        topic_speed_y_cmd = '/{0}_rsw{1}_y_speed_cmd'.format(self.node_name, self.rsw_id)
        topic_speed_y = '/{0}_rsw{1}_y_speed'.format(self.node_name, self.rsw_id)
        topic_step_z_cmd = '/{0}_rsw{1}_z_step_cmd'.format(self.node_name, self.rsw_id)
        topic_step_z =  '/{0}_rsw{1}_z_step'.format(self.node_name, self.rsw_id)
        topic_speed_z_cmd = '/{0}_rsw{1}_z_speed_cmd'.format(self.node_name, self.rsw_id)
        topic_speed_z = '/{0}_rsw{1}_z_speed'.format(self.node_name, self.rsw_id)
        topic_step_u_cmd = '/{0}_rsw{1}_u_step_cmd'.format(self.node_name, self.rsw_id)
        topic_step_u =  '/{0}_rsw{1}_u_step'.format(self.node_name, self.rsw_id)
        topic_speed_u_cmd = '/{0}_rsw{1}_u_speed_cmd'.format(self.node_name, self.rsw_id)
        topic_speed_u = '/{0}_rsw{1}_u_speed'.format(self.node_name, self.rsw_id)
        topic_output_do1_cmd = '/{0}_rsw{1}_do1_cmd'.format(self.node_name, self.rsw_id)
        topic_output_do2_cmd = '/{0}_rsw{1}_do2_cmd'.format(self.node_name, self.rsw_id)
        topic_output_do3_cmd = '/{0}_rsw{1}_do3_cmd'.format(self.node_name, self.rsw_id)
        topic_output_do4_cmd = '/{0}_rsw{1}_do4_cmd'.format(self.node_name, self.rsw_id)
        ###=== Define Publisher ===###
        self.pub_step_x = rospy.Publisher(topic_step_x, Int64, queue_size=1)
        self.pub_speed_x = rospy.Publisher(topic_speed_x, Int64, queue_size=1)
        self.pub_step_y = rospy.Publisher(topic_step_y, Int64, queue_size=1)
        self.pub_speed_y = rospy.Publisher(topic_speed_y, Int64, queue_size=1)
        self.pub_step_z = rospy.Publisher(topic_step_z, Int64, queue_size=1)
        self.pub_speed_z = rospy.Publisher(topic_speed_z, Int64, queue_size=1)
        self.pub_step_u = rospy.Publisher(topic_step_u, Int64, queue_size=1)
        self.pub_speed_u = rospy.Publisher(topic_speed_u, Int64, queue_size=1)
        ###=== Define Subscriber ===###
        self.sub_step_x_cmd = rospy.Subscriber(topic_step_x_cmd, Int64, self.set_step, callback_args='x')
        self.sub_speed_x_cmd = rospy.Subscriber(topic_speed_x_cmd, Int64, self.set_speed, callback_args='x')
        self.sub_step_y_cmd = rospy.Subscriber(topic_step_y_cmd, Int64, self.set_step, callback_args='y')
        self.sub_speed_y_cmd = rospy.Subscriber(topic_speed_y_cmd, Int64, self.set_speed, callback_args='y')
        self.sub_step_z_cmd = rospy.Subscriber(topic_step_z_cmd, Int64, self.set_step, callback_args='z')
        self.sub_speed_z_cmd = rospy.Subscriber(topic_speed_z_cmd, Int64, self.set_speed, callback_args='z')
        self.sub_step_u_cmd = rospy.Subscriber(topic_step_u_cmd, Int64, self.set_step, callback_args='u')
        self.sub_speed_u_cmd = rospy.Subscriber(topic_speed_u_cmd, Int64, self.set_speed, callback_args='u')
        self.sub_output_do1_cmd = rospy.Subscriber(topic_output_do1_cmd, Bool, self.output_do, callback_args=1)
        self.sub_output_do2_cmd = rospy.Subscriber(topic_output_do2_cmd, Bool, self.output_do, callback_args=2)
        self.sub_output_do3_cmd = rospy.Subscriber(topic_output_do3_cmd, Bool, self.output_do, callback_args=3)
        self.sub_output_do4_cmd = rospy.Subscriber(topic_output_do4_cmd, Bool, self.output_do, callback_args=4)


    def set_step(self, q, axis):
        self.motion[axis]['step'] = q.data
        return


    def _set_step(self):
        axis = ''
        step = []
        for i in self.move_mode:
            if self.move_mode[i] == 'ptp':
                axis += i
                step.append(self.motion[i]['step']
            else: pass
        self.mot.set_motion(axis=axis, mode='ptp', motion=self.motion)
        self.mot.change_step(axis=axis, step=step)
        return


    def _get_step(self):
        step = self.mot.read_counter(axis='xyzu', cnt_mode='counter')
        if self.last_position['x'] != step[0]: self.pub_step_x.publish(step[0])
        if self.last_position['y'] != step[1]: self.pub_step_y.publish(step[1])
        if self.last_position['z'] != step[2]: self.pub_step_z.publish(step[2])
        if self.last_position['u'] != step[3]: self.pub_step_u.publish(step[3])
        self.last_position['x'] = step[0]
        self.last_position['y'] = step[1]
        self.last_position['z'] = step[2]
        self.last_position['u'] = step[3]
        return


    def set_speed(self, q, axis):
        self.motion[axis]['speed'] = q.data
        return


    def _set_speed(self):
        axis = ''
        speed = []
        for i in self.move_mode:
            if self.move_mode[i] == 'jog':
                axis += i
                speed.append(self.motion[i]['speed'])
            else: pass
        self.mot.set_motion(axis=axis, mode='jog', motion=self.motion)
        self.mot.change_speed(axis=axis, mode='accdec_change', speed=speed)
        return


    def _get_speed(self):
        speed = self.mot.read_speed(axis='xyzu')
        if self.last_speed['x'] != speed[0]: self.pub_speed_x.publish(speed[0])
        if self.last_speed['y'] != speed[1]: self.pub_speed_y.publish(speed[1])
        if self.last_speed['z'] != speed[2]: self.pub_speed_z.publish(speed[2])
        if self.last_speed['u'] != speed[3]: self.pub_speed_u.publish(speed[3])
        self.last_speed['x'] = speed[0]
        self.last_speed['y'] = speed[1]
        self.last_speed['z'] = speed[2]
        self.last_speed['u'] = speed[3]
        return


    def output_do(self, q, ch):
        self.do_status[ch] = q.data
        return
    
    
    def _output_do(self):
        self.mot.driver._output_do(1, int(self.do_status[1]))
        self.mot.driver._output_do(2, int(self.do_status[2]))
        self.mot.driver._output_do(3, int(self.do_status[3]))
        self.mot.driver._output_do(4, int(self.do_status[4]))
        return
    

    def _main_thread(self):
        while not rospy.is_shutdown():
            self._set_position()
            self._set_speed()
            self._get_position()
            self._get_speed()
            self._output_do()
            continue


    def start_thread_ROS(self):
        th = threading.Thread(target=self._main_thread)
        th.setDaemon(True)
        th.start()
        return


if __name__ == '__main__':
    rospy.init_node('cpz7415v')
    ctrl = cpz7415v_controller()
    ctrl.start_thread_ROS()
    rospy.spin()

#!/usr/bin/env python 
# -*- coding: utf-8 -*-
import roslib; roslib.load_manifest('winter_keyboard') 
import rospy
from geometry_msgs.msg import Twist 
from std_msgs.msg import String
from sensor_msgs.msg import Joy
import  os  
import sys, select, termios, tty
import time    
import thread
cmd = Twist()
pub = rospy.Publisher('smooth_cmd_vel',Twist,queue_size=20)

global CurrentSpeedX
global CurrentSpeedY
global CurrentRotate
global ACC
global RotateAcc
global MAXSPEED
global MAXROTATESPEED

MAXSPEED=0.35
MAXROTATESPEED=0.8
ACC=1.5
RotateAcc=2.5
#控制频率
global ControllerFrequecny
ControllerFrequecny=10

CurrentSpeedX=0.0
CurrentSpeedY=0.0
CurrentRotate=0.0


msg="""
Reading form keybord"
    i
j   k  l
    m
press Q to quit
"""
def moveX(speed):
	global ControllerFrequecny
	global ACC
	if speed>0:
		cmd.linear.x+=ACC/ControllerFrequecny
		if(cmd.linear.x>=speed):
			cmd.linear.x=speed
		if cmd.linear.x<=speed:
			cmd.linear.y=0.0
			cmd.angular.z=0.0
			pub.publish(cmd)
			time.sleep(1.0/ControllerFrequecny)
		cmd.linear.y=0.0
		cmd.angular.z=0.0
		pub.publish(cmd)
		time.sleep(1.0/ControllerFrequecny)
		print "move forward!"
	elif speed<0:
		cmd.linear.x-=ACC/ControllerFrequecny
		if(cmd.linear.x<=speed):
			cmd.linear.x=speed
		if(cmd.linear.x>speed):
			cmd.linear.y=0.0
			cmd.angular.z=0.0
			pub.publish(cmd)
			time.sleep(1.0/ControllerFrequecny)
		print "move back!"
	else:
		return
def moveY(speed):
	global ControllerFrequecny
	global ACC
	if speed>0:
		cmd.linear.y+=ACC/ControllerFrequecny
		if(cmd.linear.y>=speed):
			cmd.linear.y=speed
		cmd.linear.x=0.0
		cmd.angular.z=0.0
		pub.publish(cmd)
		time.sleep(1.0/ControllerFrequecny)
		print "move left!"
	elif speed<0:
		cmd.linear.y-=ACC/ControllerFrequecny
		if(cmd.linear.y<=speed):
			cmd.linear.y=speed
			print 'MAX SPEED'
		cmd.linear.x=0.0
		cmd.angular.z=0.0
		pub.publish(cmd)
		time.sleep(1.0/ControllerFrequecny)
		print "move right!"
	else:
		return
def stop_robot():
	global ControllerFrequecny
	global ACC
	global RotateAcc
	fx=False
	fy=False
	fz=False
	while True:
		if(cmd.linear.x>0):
			cmd.linear.x-=ACC/ControllerFrequecny
		elif(cmd.linear.x<0):
			cmd.linear.x+=ACC/ControllerFrequecny
		if(cmd.linear.y>0):
			cmd.linear.y-=ACC/ControllerFrequecny
		elif (cmd.linear.y<0):
			cmd.linear.y+=ACC/ControllerFrequecny
		if (cmd.angular.z>0):
			cmd.angular.z-=RotateAcc/ControllerFrequecny
		elif(cmd.angular.z<0):
			cmd.angular.z+=RotateAcc/ControllerFrequecny
		if(abs(cmd.linear.x)<(ACC/ControllerFrequecny)):
			cmd.linear.x=0.0
			fx=True
		if(abs(cmd.linear.y)<(ACC/ControllerFrequecny)):
			cmd.linear.y=0.0
			fy=True
		if(abs(cmd.angular.z)<(RotateAcc/ControllerFrequecny)):
			cmd.angular.z=0.0
			fz=True
		pub.publish(cmd)
		time.sleep(1.0/ControllerFrequecny)
		print 'stoping robot now'
		if fx and fy and fz:
			return
def rotateRobot(speed):
	global ControllerFrequecny
	global RotateAcc
	if speed>0:
		cmd.angular.z+=RotateAcc/ControllerFrequecny
		if(cmd.angular.z>=speed):
			cmd.angular.z=speed
			print 'MAX SPEED'
		cmd.linear.x=0.0
		cmd.angular.y=0.0
		pub.publish(cmd)
		time.sleep(1.0/ControllerFrequecny)
		print "rotate to left!"
	elif speed<0:
		cmd.angular.z-=RotateAcc/ControllerFrequecny
		if(cmd.angular.z<=speed):
			cmd.angular.z=speed
			print 'MAX SPEED'
		cmd.linear.x=0.0
		cmd.angular.y=0.0
		pub.publish(cmd)
		time.sleep(1.0/ControllerFrequecny)
		print "rotate to left!"
	else:
		return	
def getKey():
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

global currentState
currentState='n'

def callback(msg):
	print 'herer'
	global SPEED
	global currentState
	if msg.buttons[0]==1:
		currentState='rUp'
	elif msg.buttons[1]==1:
		currentState='rRight'
	elif msg.buttons[2]==1:
		currentState='rDown'
	elif msg.buttons[3]==1:
		currentState='rLeft'
	elif msg.buttons[7]==1:
		currentState='R1'
	elif msg.buttons[5]==1:
		currentState='R2'
	elif msg.buttons[4]==1:
		currentState='L2'
	elif msg.buttons[6]==1:
		currentState='L1'
	elif msg.axes[0]==1.0:
		currentState='lLeft'
	elif msg.axes[1]==1.0:
		currentState='lUp'
	elif msg.axes[0]==-1.0:
		currentState='lRight'
	elif msg.axes[1]==-1.0:
		currentState='lDown'
	else:
		currentState='n'
if __name__ == '__main__':
	settings = termios.tcgetattr(sys.stdin)
	rospy.init_node('teleop')
	rospy.Subscriber("/joy",Joy,callback)
	rate = rospy.Rate(rospy.get_param('~hz', 1))  
	#thread.start_new_thread(getCharfromKeyboard,())  
		#rate.sleep()
	last_ch=''
	while not rospy.is_shutdown():
		global currentState
		print currentState
		print msg
		ch=getKey()
		if ch=='i' or currentState=='rUp':
			if last_ch=='i' or currentState=='rUp':
				moveX(MAXSPEED)
		elif ch=='m' or currentState== 'rDown':
			if last_ch=='m' or currentState== 'rDown':
				moveX(0-MAXSPEED)
		elif ch=='j'or currentState=='rLeft':
			if last_ch=='j' or currentState=='rLeft':
				rotateRobot(MAXROTATESPEED)
		elif ch=='l' or currentState=='rRight':
			if last_ch=='l' or currentState=='rRight':
				rotateRobot(0-MAXROTATESPEED)
		elif ch=='u':
			rotateRobot(MAXROTATESPEED)
		elif ch=='o':
			rotateRobot(0-MAXROTATESPEED)
		elif ch=='l':
			rotateRobot(-MAXROTATESPEED)
		elif ch=='k':
			stop_robot()
		elif ch=='q':
			cmd.linear.x=0.0
			cmd.linear.y=0.0
			cmd.angular.z=0.0
			pub.publish(cmd)
			print "shutdown!"
			break
		else:
			if last_ch is '' :
				stop_robot()
		last_ch=ch
		#print "Reading form keybord"
		'''
		print """   i
j  k  l
   m"""
		print 'press Q to quit'
		'''
		#rospy.spinonce()
		#rate.sleep()
			
			

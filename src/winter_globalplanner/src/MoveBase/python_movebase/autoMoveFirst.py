#!/usr/bin/env python
# -*- coding: utf-8 -*-
import rospy
from geometry_msgs.msg import Twist, Point, Quaternion,PoseStamped
from math import radians, copysign, sqrt, pow, pi,cos
from nav_msgs.msg import Path
import PyKDL
import tf
import math


#平滑速度 返回目标点的位置 与方向
#0.1745 10度
def averageSpeed(path):
	Length=len(path.poses)
	finalpath=[]
	last=quat_to_angle(path.poses[0].pose.orientation)
	goalposition=[]
	for i in range(1,Length):
		GD=quat_to_angle(path.poses[i].pose.orientation)
		#if()
		last=GD

def newGoal(path):
	i=30
	#每１米最少一个目标点　防止长距离角度过小的碰撞
	lastj=0
	lastGD=quat_to_angle(path.poses[30].pose.orientation)
	poses=[]
	
	poses.append(path.poses[30])

	while i<len(path.poses)-10:
		GD=quat_to_angle(path.poses[i].pose.orientation)
		errDirection=GD-lastGD
		if(errDirection>3.14):
			errDirection=2*3.1415-errDirection
		elif(errDirection<-3.14):
			errDirection=2*3.1415+errDirection
		
		#0.175 10du 0.35 20 0.524 30degree
		
		if(abs(errDirection))>0.35:
			poses.append(path.poses[i])
			lastGD=GD
			lastj=i
			
		if(i-lastj>50):
			lastj=i
			poses.append(path.poses[i])
		i+=5
		rospy.loginfo("i %d lastj %d ",i,lastj)
	poses.append(path.poses[len(path.poses)-1])
	return poses
def PathCallback(path):
	poses=newGoal(path)
		
	i=0
	rospy.loginfo("has %d goals",len(poses))
	
	while i<len(poses):
		GX=poses[i].pose.position.x
		GY=poses[i].pose.position.y
		GD=quat_to_angle(poses[i].pose.orientation)
		rospy.loginfo("the %d goal is x:%f y:%f diretion:%f ",i,GX,GY,GD)
		rotateToGoalDirection(poses[i].pose,poses[i].pose.orientation,False)
		moveToGoalX(poses[i].pose)
		i+=1
	
	rotateToGoalDirection(poses[i-1].pose,poses[i-1].pose.orientation,True)
	
rospy.init_node('pathlistener', anonymous=False)
rospy.Subscriber('/planner/planner/plan',Path,PathCallback)

mPath=rospy.Publisher('/mplannerplan',Path,queue_size=5)



tf_listener = tf.TransformListener()
cmd_vel = rospy.Publisher('/cmd_vel', Twist, queue_size=5)
rate = 20
r = rospy.Rate(rate)
ROTATE_SPEED=0.8
X_SPEED=0.4


def quat_to_angle(quat):
    rot = PyKDL.Rotation.Quaternion(quat.x, quat.y, quat.z, quat.w)
    return rot.GetRPY()[2]

def canculateAngle(GX,GY,CX,CY):
	ERR_X=GX-CX
	ERR_Y=GY-CY
	if ERR_X>0:
		return math.atan(ERR_Y/ERR_X)
	elif ERR_X<0:
		if ERR_Y>0:
			return math.atan(ERR_Y/ERR_X)+pi
		else:
			return math.atan(ERR_Y/ERR_X)-pi
	else:
		if ERR_Y>0:
			return pi/2
		else:
			return 0-pi/2

#传入目标位置　目标点方向四元素　将机器人转动到向该目标点运动的方向
def rotateToGoalDirection(pose,rot,final):
	goalAngle=0.0
	#获取当前位置
	(position, rotation) = get_odom()
	if(final!=True):
		#获取机器人目标的位置　角度
		GX=pose.position.x
		GY=pose.position.y
		
		CX=position.x
		CY=position.y
		#计算坐标差值
	
		#计算两个目标点与当前点的角度差值
		goalAngle=canculateAngle(GX,GY,CX,CY)
	else:
		goalAngle=quat_to_angle(rot)
	goalAngleC=0.0
	last_angleC=0.0
	#将四元素转化为角度
	#goalAngle=quat_to_angle(rot)
	
	if(goalAngle<0.0):
		goalAngleC=2*pi+goalAngle
	else:
		goalAngleC=goalAngle
	#rospy.loginfo("Goal Angle is %f",goalAngleC)
	# Track the last angle measured
	last_angle = float(rotation)
	# Track how far we have turned
	if(rotation<0.0):
		last_angleC=2*pi+rotation
	else:
		last_angleC=last_angle
	#rospy.loginfo("curretn Angle is %f",rotation)
	turn_angle=goalAngleC-last_angleC
	
	move_cmd=Twist()
	if (0<=turn_angle and turn_angle<=pi) or ((-2*pi)<=turn_angle and turn_angle<=(0-pi)):
		move_cmd.angular.z = ROTATE_SPEED
	else:
		move_cmd.angular.z = 0-ROTATE_SPEED
	#转到运动方向上
	turn_angle=goalAngle-last_angle
	#0.02 大约１．１４度　
	while abs(turn_angle)>0.06 and not rospy.is_shutdown():
			cmd_vel.publish(move_cmd)
			r.sleep()
			(position, rotation) = get_odom()
			turn_angle=goalAngle-rotation
	move_cmd=Twist()
	cmd_vel.publish(move_cmd)
#向目标位置点运动　是在运动方向基础上　前进
#传入参数　目标点的位置 只从机器人前进方向运动
def	moveToGoalX(pose):
	#获取机器人目标的位置　角度
	GX=pose.position.x
	GY=pose.position.y
	(position, rotation) = get_odom()
	x_start=position.x
	y_start=position.y
	move_cmd=Twist()
	move_cmd.linear.x=0.4
	distance = 0
	#到目标点的位置
	goal_distance=sqrt(pow((GX - x_start), 2)+pow((GY - y_start), 2))
	while distance<goal_distance and not rospy.is_shutdown():
		cmd_vel.publish(move_cmd)
		r.sleep()
		(position, rotation) = get_odom()
		distance=sqrt(pow((position.x - x_start), 2)+pow((position.y - y_start), 2))
	move_cmd=Twist()
	cmd_vel.publish(move_cmd)

#传入参数　目标点的位置 时间　全向运动到机器人前进方向运动	
def moveToGoalXY(pose):
	#获取机器人目标的位置　角度
	GX=pose.position.x
	GY=pose.position.y
	(position, rotation) = get_odom()
	x_start=position.x
	y_start=position.y
	move_cmd=Twist()
	
	#获取
	#vx=move_cmd.linear.x*math.cos(rotation)-move_cmd.linear.y*math.sin(rotation)
	#vy=move_cmd.linear.x*math.sin(rotation)+move_cmd.linear.y*math.cos(rotation)
	
	#获取该方向的速度比例
	if abs(GX-x_start)>=abs(GY-y_start):
		if GX-x_start>0:
			vx=0.5
			vy=(GY-y_start)/(GX-x_start)*vx
		else:
			vx=-0.5
			vy=(GY-y_start)/(GX-x_start)*vx
	else:
		if (GY-y_start)>0:
			vy=0.5
			vx=(GX-x_start)/(GY-y_start)*vy
		else:
			vy=-0.5
			vx=(GX-x_start)/(GY-y_start)*vy
	
	
	#求出机器人的运动的速度
	move_cmd.linear.x=vx*math.cos(rotation)+vy*math.sin(rotation)
	move_cmd.linear.y=vy*math.cos(rotation)-vx*math.sin(rotation)
	
	distance = 0
	#到目标点的位置
	goal_distance=sqrt(pow((GX - x_start), 2)+pow((GY - y_start), 2))
	while distance<goal_distance and not rospy.is_shutdown():
		cmd_vel.publish(move_cmd)
		r.sleep()
		(position, rotation) = get_odom()
		distance=sqrt(pow((position.x - x_start), 2)+pow((position.y - y_start), 2))
	move_cmd=Twist()
	cmd_vel.publish(move_cmd)
	
	
def normalize_angle(angle):
    res = angle
    while res > pi:
        res -= 2.0 * pi
    while res < -pi:
        res += 2.0 * pi
    return res

def get_odom():
	(trans, rot) = tf_listener.lookupTransform('/odom','/base_link', rospy.Time(0))
	return Point(*trans),quat_to_angle(Quaternion(*rot))
if __name__ == '__main__':
	rospy.spin()
	

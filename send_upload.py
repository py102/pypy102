# -*- coding: utf-8 -*-
"""
Created on Sat Mar 16 17:21:57 2019

@author: LEE YOUJIN
"""

import cv2
import numpy as np 
import math
from opcua import Server
from opcua import Client
from opcua import ua
import time

cap = cv2.VideoCapture(0)

server = Server()
  
url = 'opc.tcp://192.168.0.0:4840'#opc-ua랑 ip 같게
server.set_endpoint(url)


print("Server started at{}", format(url))

name = "OPCUA_SIMULATION_SERVER"
addspace = server.register_namespace(name)
node = server.get_objects_node()
Param = node.add_object(addspace, "Parameters")
col = Param.add_variable(addspace, "COLOR", 0)
sh = Param.add_variable(addspace, "SHAPE", 0)
ti = Param.add_variable(addspace, "TIME", 0)

col.set_writable()
sh.set_writable()
ti.set_writable()

client = Client("opc.tcp://192.168.0.0:4840") #plc랑 같게
client.connect()

CM1002 = client.get_node(ua.NodeId(793890171,2))
CM1003 = client.get_node(ua.NodeId(156193554,2))
CM1004 = client.get_node(ua.NodeId(2069283405,2))
CM1005 = client.get_node(ua.NodeId(1431586788,2))
CM1006 = client.get_node(ua.NodeId(1197192991,2))

server.start()

while(True):
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray,(5,5),0)    
    res = cv2.bitwise_and(frame, frame, mask = blur)
    hsv = cv2.cvtColor(res, cv2.COLOR_BGR2HSV)
    
    lower_yellow = np.array([15, 70, 70])
    upper_yellow = np.array([35, 255, 255])
    
    lower_blue = np.array([100, 60, 40])
    upper_blue = np.array([135, 255, 255])
    
    mask_y= cv2.inRange(hsv, lower_yellow, upper_yellow)
    mask_b= cv2.inRange(hsv, lower_blue, upper_blue)
    
    kernel_y1 = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
    opening1_y = cv2.morphologyEx(mask_y, cv2.MORPH_OPEN, kernel_y1)
    kernel_y2 = cv2.getStructuringElement(cv2.MORPH_RECT,(4,4))
    opening2_y = cv2.morphologyEx(opening1_y, cv2.MORPH_OPEN, kernel_y2)
    kernel_y3 = cv2.getStructuringElement(cv2.MORPH_RECT,(5,5))
    opening3_y = cv2.morphologyEx(opening2_y, cv2.MORPH_OPEN, kernel_y3)
    
    kernel_b1= cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
    opening1_b = cv2.morphologyEx(mask_b, cv2.MORPH_OPEN, kernel_b1)
    kernel_b2= cv2.getStructuringElement(cv2.MORPH_RECT,(4,4))
    opening2_b = cv2.morphologyEx(opening1_b, cv2.MORPH_OPEN, kernel_b2)
    kernel_b3= cv2.getStructuringElement(cv2.MORPH_RECT,(5,5))#커널(8X6)단위로 open method 보정 2차 시행
    opening3_b = cv2.morphologyEx(opening2_b, cv2.MORPH_OPEN, kernel_b3)
    
    mask_y2=opening3_y.copy()
    mask_b2=opening3_b.copy()
        
    image_y, contours_y, hierachy_y = cv2.findContours(mask_y2, cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
    image_b, contours_b, hierachy_b = cv2.findContours(mask_b2, cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
    
    try:
        cnt_y=contours_y[0]           
        try:
            cnt_b=contours_b[0]
            b_a=cv2.contourArea(cnt_b)
            y_a=cv2.contourArea(cnt_y)
            
            if y_a(float)>b_a(float)+50:
                color="yello"
            
            elif b_a(float)>y_a(float)+50:
                color="blue"
                
            else:
                color="noise"
                
        except:
            color="yello"
        
    except:                
        try:
            cnt_b=contours_b[0]
            color="blue"                
        except:
            color="none"
            
    if color=="none":
        img_f=blur.copy()
        shape="none"
    else:
        if color=="yello":
            img=mask_y2
            img_c=cv2.bitwise_and(frame, frame, mask = img)
        elif color=="blue":            
            img=mask_b2
            img_c=cv2.bitwise_and(frame, frame, mask = img)
        
        blur2=cv2.addWeighted(img,float(80) * 0.01, blur,float(20) * 0.01,0)
        img2=img.copy()
        
        image, contours, hierachy = cv2.findContours(img2, cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
        cnt=contours[0]
        
        areabox = cv2.contourArea(cnt)
        x, y, w, h = cv2.boundingRect(cnt)
        aspect_ratio = float(w)/h               
        
                                 
        try:                                
            circles = cv2.HoughCircles(blur2, cv2.HOUGH_GRADIENT, 1, 1000,param1=50,param2=40,minRadius=40, maxRadius=400)
            circles = np.uint16(np.around(circles))
  
            for i in circles[0,:]:
                cv2.circle(img_c,(i[0],i[1]),i[2],(0,255,0),2)
                cv2.circle(img_c,(i[0],i[1]),2,(0,0,255),3)
    
            shape="round"
                
            img_f=img_c
            
        except:
            rect = cv2.minAreaRect(cnt) #컨투어를 포함하는 최소면적직사각형을 rect
            box = cv2.boxPoints(rect) #rect의 박스포인트
            box = np.int0(box) #box의 좌표를 넘파이로 처리
            
            (x,y), radius = cv2.minEnclosingCircle(cnt) #컨투어 영역을 감싸는 가장 작은 원의 중심과 반지를을 결정
            center = (int(x), int(y)) #중심의 좌표
            radius = int(radius) #반지름을 radius에 저장
        
        #최소 면적
            areabox = cv2.contourArea(box) #박스의 최소면적
            areacir = radius**2*math.pi # 원의 넒이는 pi*r^2
            areacontour = cv2.contourArea(cnt) #컨투어 영역의 넓이
            
            if aspect_ratio<1.5 and aspect_ratio>0.8 and areabox>50 and areacir>50:  
                if areacir<areabox and areacontour<areacir: #원넓이가 박스 넓이보다 작고 컨투어영역이 원 넓이보다 작으면
                    img_f=cv2.circle(img_c,center,radius,(0,255,0),3) #res에 파란색의 원을 그린다.
                    shape="round"
                elif areabox<areacir and areabox>50: #박스넓이가 원넓이보다 작고 컨투어영역이 박스 넓이보다 작으면
                    img_f=cv2.drawContours(img_c,[box],0,(0,0,255),3) #res에 빨간색의 상자를 그린다.
                    shape="rectangle"
                else: #그렇지 않으면
                    img_f=cv2.drawContours(img_c,contours,-1,(255,0,0),3) #초록색 컨투어 라인을 그린다.
                    shape="noise"
    
            else:
                shape="noise"
                img_f=img.copy()   


    t=time.strftime('%H:%M:%S', time.localtime(time.time()))
    tt=str(t)
    
    try:
        colords.append(color)
        
    except:
        colords=[color]
        
    if len(colords)>9:
        colorn=colords[-10:-1]
        
        if colorn.count(color)>5:
            COLOR=color
        else:
            COLOR=COLORF
    else:
        COLOR="wait"
        
        
    try:
        shapeds.append(shape)
        
    except:
        shapeds=[shape]
    
        
    if len(shapeds)>9:
        shapen=shapeds[-10:-1]
        
        if shapen.count(shape)>5:
            SHAPE=shape
        else:
            SHAPE=SHAPEF
    else:
        SHAPE="wait"
            
    TIME = tt

    col.set_value(COLOR)
    sh.set_value(SHAPE)
    ti.set_value(TIME)
    
    print(TIME + ' ' + COLOR + ' ' + SHAPE)
    
    cv2.imshow('i',img_f)
    
    COLORF=COLOR
    SHAPEF=SHAPE

    if SHAPEF == "none" or SHAPEF =="noise" or COLORF =="noise":
        if COLORF == "none":
            CM1002.set_value(False)
            CM1003.set_value(False)
            CM1004.set_value(False)
            CM1005.set_value(False)
            CM1006.set_value(False)

        else:    
            pass
    
    elif SHAPEF == "round" or COLORF == "blue": 
        CM1003.set_value(True) 
        if COLORF == "yello": 
            CM1004.set_value(True) 
        elif SHAPEF == "rectangle": 
            CM1005.set_value(True) 
        else: 
            CM1006.set_value(True) 
    elif SHAPEF == "rectangle" and COLORF == "yello": 
        CM1002.set_value(True) 
    else: 
        CM1002.set_value(False) 
        CM1003.set_value(False) 
        CM1004.set_value(False) 
        CM1005.set_value(False) 
        CM1006.set_value(False)  
                # q누르면 종료

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

client.disconnect()
cap.release()
cv2.destroyAllWindows()

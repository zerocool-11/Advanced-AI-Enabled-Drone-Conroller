import numpy as np


fbrange=[6000,6800]
### it have all the necessary functions that are needed for body tracking and voice control


def track(drone,bbox,w,h,pid,pErrorW,pErrorH):
    # print("track function called...")
    fspeed=0
    area=bbox[0][2]*bbox[0][3]
    cx,cy=bbox[1][0],bbox[1][1]
    errorW=cx-w//2
    errorH=cy-h//2
    speedW=pid[0]*errorW + pid[1]*(errorW-pErrorW)
    speedW=-int(np.clip(speedW,-100,100))
    speedH=pid[0]*errorH + pid[1]*(errorH-pErrorH)
    speedH=-int(np.clip(speedH,-100,100))
    #print("area: ......... ",area)
    if area >fbrange[0] and area< fbrange[1]:
        fspeed=0
    if area>fbrange[1]:
        fspeed=-20
        # print("backward")
    elif area<fbrange[0] and area!=0:
        fspeed=+20
        # print("forward")
    #or -10 <= error <= 10 
    if cx==0 :
        #print("center is zero ---------------------------------------------------------")
        speedW=0
        speedH=0
        errorH=0
        errorW=0
    drone.send_rc_control(0,fspeed,speedH,speedW)
    # print("sending commands maybe:........../././//./././././././././/././././/.//./././././././././././././.")
    # print("distance b/w center and cx ",errorW)
    # print("fspeed: ",fspeed)
    # print("speed: ",speedW)
    # print("speed for up down: ",-speedH)
    return errorW,errorH



# def track(drone,bbox,w,h,pid,pErrorW,pErrorH):
#     global fspeed
#     area=bbox[0][2]*bbox[0][3]
#     cx,cy=bbox[1][0],bbox[1][1]
#     errorW=cx-w//2
#     errorH=cy-h//2
#     speedW=pid[0]*errorW + pid[1]*(errorW-pErrorW)
#     speedW=int(np.clip(speedW,-60,60))
#     speedH=pid[0]*errorH + pid[1]*(errorH-pErrorH)
#     speedH=-int(np.clip(speedH,-60,60))
#     print("area: ......... ",area)
#     if area >fbrange[0] and area< fbrange[1]:
#         fspeed=0
#     if area>fbrange[1]:
#         fspeed=-20
#     elif area<fbrange[0] and area!=0:
#         fspeed=+20
#     #or -10 <= error <= 10 
#     if cx==0 :
#         print("center is zero ---------------------------------------------------------")
#         speedW=0
#         speedH=0
#         errorH=0
#         errorW=0
#     drone.send_rc_control(0,fspeed,speedH,speedW)
#     # print("sending commands maybe:........../././//./././././././././/././././/.//./././././././././././././.")
#     # print("distance b/w center and cx ",errorW)
#     # print("fspeed: ",fspeed)
#     # print("speed: ",speedW)
#     # print("speed for up down: ",-speedH)
#     return errorW,errorH


def voice_controller(me,cmd):
    lr, fb, ud, yv = 0, 0, 0, 0
    speed=30
    
    if "move right" in cmd:
        lr=speed  
        print("moving right.. ",lr)
    elif "move left" in cmd:
        lr=-speed
        print("moving left.. ",lr)
    elif "move forward" in cmd:
        fb=speed
        print("moving forward.. ",fb)
        
    elif "move back" in cmd:
        fb=-speed
        print("moving back... ",fb)
    elif "move up" in cmd:
        ud=speed
        print("moving up.. ",ud)
    elif "move down" in cmd:
        ud=-speed
        print("moving down.. ",ud)
    elif "clockwise" in cmd:
        yv=-speed
        print("moving clockwise.. ",yv)
    elif "anticlockwise" in cmd:
        yv=speed
        print("moving anticlockwise.. ",yv)
    if "stop" in cmd:
        #pass
        lr, fb, ud, yv = 0, 0, 0, 0
    # print("inside func")
    print("final command..",lr,fb,ud,yv)
    me.send_rc_control(lr,fb,ud,yv)
    return [lr,fb,ud,yv]
    
def finger_tracking(img,index):
    if index==1:
        cx=roix+roiw//2
        cy=roiy+roih//2
        error_lr=hand_points[8][0]-cx
        error_fb=hand_points[8][1]-cy
        lr=pid[0]*error_lr + pid[1]*(error_lr-pErrorW)
        lr=int(np.clip(lr,-40,40))
        fb=pid[0]*error_fb + pid[1]*(error_fb-pErrorH)
        fb=-int(np.clip(fb,-40,40))

    
        me.send_rc_control(lr,fb,0,0)
        if lr <=0:
            cv2.putText(img, f'moving: right  {int(lr)}', (340, 20), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 0), 2)
        elif lr >0:
            cv2.putText(img, f'moving: left  {int(lr)}', (340, 20), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 0), 2)
        if fb <=0:
            cv2.putText(img, f'moving: down  {int(fb)}', (340, 90), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 0), 2)
        elif fb >0:
            cv2.putText(img, f'moving: up  {int(fb)}', (340, 90), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 0), 2)
        cv2.circle(img,(cx,cy),5,(255,255,0),-2)
    else:
        pass
        me.send_rc_control(0,0,0,0)
    return img


def finger_check(hand_points):
    ind=0
    thb=0
    mid=0
    wrist = np.array(hand_points[0])
    index = np.array(hand_points[8])
    index_ip=np.array(hand_points[6])
    index_s=np.array(hand_points[5])
    middle=np.array(hand_points[12])
    middle_ip=np.array(hand_points[10])
    middle_s=np.array(hand_points[9])
    thumb=np.array(hand_points[4])
    thumb_ip=np.array(hand_points[3])
    thumb_s=np.array(hand_points[1])
    if index[1]<index_ip[1]:  # checks if finger is up 
        finger_index="up"
        ind=1
        print("index up")
    if index[1]>index_ip[1]:
        finger_index="down"
        ind=0
        print("index down")    
    if middle[1]<middle_ip[1]: # checks if finger is up 
        finger_middle="up"
        mid=1
        print("middle up")
    if middle[1]>middle_ip[1]:
        finger_middle="down"
        mid=0
        print("middle down")

    if thumb[0]>thumb_ip[0]: # checks if thumb is up 
        finger_thumb="up"
        thb=1
        print("thumbs up")
    if thumb[0]<thumb_ip[0]:
        finger_thumb="down"
        thb=0
        print("thumb down")
    return ind,mid,thb

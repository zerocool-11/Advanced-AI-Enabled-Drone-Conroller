from utils.mediapipe_utils import *
from utils.utils import *
from utils.keypoint_classifier import KeyPointClassifier
from djitellopy import tello
from utils import preprocessing
from utils.FaceDetector import Detector
import cv2
import numpy as np
import time
import speech_recognition as sr


model_path="model/model.tflite"

w,h=360, 240
pTime = 0
wait_time=0

pid=[0.2,0.2,0]
pErrorW=0
pErrorH=0
fspeed=0
fbrange=[6000,6800]

text=""
text_old=""
labels=["1","2","palm"]

finalid=[]
itr=0
distance_array=[]
old_control=[0,0,0,0]
init_time=0
end_time=0

##flags for enabling and disabling functions
flag=False
body_track=False
finger_track=False
voice_control=True
get_time_flag=True

## creating objects
r=sr.Recognizer()
m=sr.Microphone()
# me=None
# # kp.init()
detector=Detector()
keypoint_classifier = KeyPointClassifier(model_path)
cap = cv2.VideoCapture(0)
me = tello.Tello()

me.connect()
me.streamoff
me.streamon()
me.takeoff()
# me.send_rc_control(0,0,40,0)
time.sleep(1)

def callback(recognizer,audio):
    global text
    try:
        #audio=r.listen(source)
        text=recognizer.recognize_google(audio)
        print("text: ",text)
        
    except:
        print("say something")

def run_once(): 
    with m as source:
        r.adjust_for_ambient_noise(source) 

me.send_rc_control(0,0,0,0)
while True:
    # _,img=cap.read()
    img = me.get_frame_read().frame
    img=cv2.flip(img,1)
    img = cv2.resize(img, (720, 440))
    img, bbox,hand_points,hand_label = detector.get_face_points(img)
    
    h,w,c=img.shape
    #  KLprint(img.shape)
    # vals = getKeyboardInput()
    # me.send_rc_control(vals[0], vals[1], vals[2], vals[3])
    
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    
    if hand_points and bbox:
    
        finger_tips_x=[hand_points[8][0],hand_points[12][0],hand_points[16][0],hand_points[20][0]] ##finger tips of index,middle,ring,pinky
        finger_tips_y=[hand_points[8][1],hand_points[12][1],hand_points[16][1],hand_points[20][1]]
        #print("fingertops: ",finger_tips)
        if all((i >= bbox[0][0]-220 and i<=(bbox[0][0]-70)) for i in finger_tips_x) and (all( (bbox[0][1]+150>=i>=bbox[0][1]) for i in finger_tips_y)):
            cv2.rectangle(img,(bbox[0][0]-220,bbox[0][1],150,150),(0,255,0),2)
            preprocessed_points=preprocessing.final_distance(hand_points)
            hand_sign_id = keypoint_classifier(preprocessed_points)
            finalid.append(hand_sign_id)
            img = draw_info_text(
                    img,
                    hand_label,
                    labels[hand_sign_id]
                    )
            if itr%3==0:
                nTemp = finalid[0]
                bEqual = True
                
                for item in finalid:
                    if nTemp != item:
                        bEqual = False
                        break;
                    
                if bEqual:
                    
                    if nTemp==0:
                        body_track=True #temp false
                        finger_track=False
                        voice_control=False
                        print("body track enabled")
                    elif nTemp==1:
                        voice_control=True #temp false
                        body_track=False
                        finger_track=False
                        print("voice control enabled")
                    elif nTemp==2:
                        # pass
                        me.land()
                        break
                # else:
                #     print("no")
                finalid=[]
            
        else:
          cv2.rectangle(img,(bbox[0][0]-220,bbox[0][1],150,150),(255,255,0),2)  
    
    if voice_control:
        # print("voice control enabled")
        path_array={}
        if not flag:
            run_once()
            init_time=time.time()
            stop_listening = r.listen_in_background(m, callback)
            flag=True
            me.send_rc_control(0,0,0,0)
        end_time=time.time()
        # if end_time-init_time>=14:
        #     me.send_rc_control(0,0,0,0)

        if text_old!=text:
            text_old=text
            if "activate body tracking" in text:
                body_track=True
                print("body tracking activated")
            elif "deactivate body tracking" in text:
                body_track=False
                print("body tracking deactivated")
            if "land" in text:
                me.land()
                print("landing")
            values=voice_controller(me,text)
            if get_time_flag:
                init_time=time.time()
                get_time_flag=False
            if values!=old_control:
                end_time=time.time()
                total_time=end_time-init_time
                path_array['time']=total_time
                path_array['cmd']=[-j for j in old_control]  ##changing the controls to negative so that it will go back the same path
                distance_array.append(path_array.copy())
                old_control=values
                init_time=end_time

            if "return back to base" in text:
                for z,k in enumerate(reversed(distance_array)):
                    if z==0:
                        time.sleep(2) ##just to make drone to be on standby  
                    print("sending... ",k)
                    me.send_rc_control(k['cmd'][0],k['cmd'][1],k['cmd'][2],k['cmd'][3])
                    print("type: ",type(k['time']))
                    if k['time']>0.5:
                        time.sleep(k['time']-0.2)
                    else:
                        time.sleep(k['time'])
                me.land()
                break
            print("text in main code : ",text)
    # elif flag:
    #     stop_listening(wait_for_stop=False)
    #     flag=False
    # elif not stopthread.stopped():
    #     stopthread.stop()
    
    if bbox:
        cv2.rectangle(img,(bbox[0][0]-220,bbox[0][1],150,150),(255,255,0),2)
        roix,roiy=bbox[0][0]-220,bbox[0][1]
        roiw,roih=150,150
        #for bbox in bboxs:
            #print("dist b/w frame and bbox x: ",w-bbox[0][0])
        #print("bbox: ",bbox)
        if body_track:
                pErrorW,pErrorH=track(me,bbox,w,h,pid,pErrorW,pErrorH)
                cv2.circle(img,(bbox[1][0],bbox[1][1]),5,(255,255,0),-2)
            
        if hand_points:
            # print(finger_track)
            if finger_track:
                index,middle,thumb=finger_check(hand_points)
                img=finger_tracking(img,index)
                
        if fbrange[0]<=bbox[0][2]*bbox[0][3]<=fbrange[1]:
            cv2.putText(img, f'fbrange: {int(bbox[0][2]*bbox[0][3])}', (0, 20), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 0), 2)
        else:
            cv2.putText(img, f'fbrange: {int(bbox[0][2]*bbox[0][3])}', (0, 20), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
    # else:
    #     #me.send_rc_control(0,0,0,0)
    #     if wait_time==20:
    #         # print("no face found rotating.............................................................")
    #         # time.sleep(2)
    #         # wait_time=0
    #         pass 
    
    cv2.putText(img, f'FPS: {int(fps)}', (20, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 2)
    cv2.imshow("Image", img)
    itr+=1
    if cv2.waitKey(1) & 0xFF == 27:
        print("Battery: {}%".format(me.get_battery()))
        me.land()
        break

cap.release()
cv2.destroyAllWindows()

import mediapipe as mp
import cv2
import time 
import numpy as np
from utils.mediapipe_utils import draw_landmarks


def calc_bounding_rect(image, landmarks):
        image_width, image_height = image.shape[1], image.shape[0]

        landmark_array = np.empty((0, 2), int)

        for _, landmark in enumerate(landmarks.landmark):
            landmark_x = min(int(landmark.x * image_width), image_width - 1)
            landmark_y = min(int(landmark.y * image_height), image_height - 1)

            landmark_point = [np.array((landmark_x, landmark_y))]

            landmark_array = np.append(landmark_array, landmark_point, axis=0)

        x, y, w, h = cv2.boundingRect(landmark_array)

        return [x, y, w, h]
    
def calc_landmark_list_for_frames(image, landmarks):
    """Preprocessing keypoints to collect the eculidean distance
    ------- ------- ------- ------- ------- ------- ------- ------- ------- -------
    Args:
        image
        landmarks
    single frame and landmarks from mediapipe
    ------- ------- ------- ------- ------- ------- ------- ------- ------- 
    Returns:
        Preprocessed landmark points
    ------- ------- ------- ------- ------- 
    """
    image_width, image_height = image.shape[1], image.shape[0]

    landmark_point = []

    
    for _, landmark in enumerate(landmarks.landmark):
        landmark_x = min(int(landmark.x * image_width), image_width - 1)
        landmark_y = min(int(landmark.y * image_height), image_height - 1)
        

        landmark_point.append([landmark_x, landmark_y])

    return landmark_point
class Detector:
    def __init__(self,minDet=0.75):
        self.minDet=minDet
        self.holistic = mp.solutions.holistic
        self.holistic=self.holistic.Holistic(min_detection_confidence=0.5,min_tracking_confidence=0.5)
        # self.mp_hand=mp.solutions.hands
        # self.hand=self.KLKLKLmp_hand.Hands(max_num_hands=1,min_detection_confidence=0.5,min_tracking_confidence=0.5)
    def get_face_points(self,img,draw=True):
        self.res=self.holistic.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        #self.results=self.face_detector.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        face=None
        bboxs=[]
        # if self.res.detections:
        #     for id,detection in enumerate(self.res.detections):
        #         bboxC=detection.location_data.relative_bounding_box
        #         ih,iw,ic=img.shape
        #         bbox=int(bboxC.xmin*iw),int(bboxC.ymin*ih),int(bboxC.width*iw),int(bboxC.height*ih)
        #         cx=bbox[0]+bbox[2]//2
        #         cy=bbox[1]+bbox[3]//2
        #         #print("box: ",bbox)
        #         face=[bbox,[cx,cy]]
        #         bboxs.append(face)

        #         cv2.rectangle(img, bbox, (255, 0, 255), 2)
        #         cv2.putText(img, f'{str(int(detection.score[0]*100))}%',
        #                 (bbox[0], bbox[1] - 20), cv2.FONT_HERSHEY_PLAIN,
        #                 2, (255, 0, 255), 2)
        #         break
            
        #     return img,face
                
        if self.res.face_landmarks:
            face_landmark=self.res.face_landmarks
            bbox=calc_bounding_rect(img,face_landmark)
            cv2.rectangle(img, bbox, (255, 0, 255), 2)
            cx=bbox[0]+bbox[2]//2
            cy=bbox[1]+bbox[3]//2
            face=[bbox,[cx,cy]]
        else:
            face=None
        if self.res.right_hand_landmarks:
            # print("inside class")
            landmark_list= calc_landmark_list_for_frames(img,self.res.right_hand_landmarks)
            Label="Left"
            # print(len(landmark_list))
            img = draw_landmarks(img, landmark_list)
        else:
            landmark_list= None
            Label=None

        return img,face,landmark_list,Label

    def get_hand_points(self,img):
        self.res_hand=self.hand.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        Label=None
        if self.res_hand.multi_hand_landmarks:
            for hand_landmarks, handedness in zip(self.res_hand.multi_hand_landmarks,self.res_hand.multi_handedness):
                landmark_list= calc_landmark_list_for_frames(img,hand_landmarks)
                Label=handedness.classification[0].label[0:]
                img = draw_landmarks(img, landmark_list)
        else:
            landmark_list= None
        
        return img,Label,landmark_list

    
        

def main():
    cap = cv2.VideoCapture(0)
    pTime = 0
    detector = Detector()
    while True:
        success, img = cap.read()
        img, bbox = detector.faces(img)
        #print(bbox[2]*bbox[3])

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        if bbox:
            if 6000<=bbox[2]*bbox[3]<=8000:
                cv2.putText(img, f'fbrange: {int(bbox[2]*bbox[3])}', (0, 20), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 0), 2)
            else:
                cv2.putText(img, f'fbrange: {int(bbox[2]*bbox[3])}', (0, 20), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)

        cv2.putText(img, f'FPS: {int(fps)}', (20, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 2)
        cv2.imshow("Image", img)
        if cv2.waitKey(1) & 0xFF == 27:
            break
 
    cap.release()
    #cv2.destroyAllwindows()
 
if __name__ == "__main__":
    main()
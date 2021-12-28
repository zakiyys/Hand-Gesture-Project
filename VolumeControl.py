import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

wCam, hCam = 640, 480

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0
volImg = 400
volPer = 0
vol = 0
detector = htm.handDetector(detectionCon=0.75)


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
#volume.GetMute()
#volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
#volume.SetMasterVolumeLevel(-60.0, None)
minVol = volRange[0]
maxVol = volRange[1]


while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    if lmList is None :
        lmList = [0]
    else :
        #print(lmList[4],lmList[8])

        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1+x2)//2, (y1+y2)//2

        cv2.line(img, (x1,y1),(x2,y2),(255,255,0),3)
        cv2.circle(img, (x1, y1), 7, (255,0,255),cv2.FILLED)
        cv2.circle(img, (x2, y2), 7, (255,0,255),cv2.FILLED)
        cv2.circle(img, (cx, cy), 5, (255,0,255),cv2.FILLED)

        lenght = math.hypot(x2-x1, y2-y1)
        #print(lenght)
        if lenght < 22:
            cv2.circle(img, (cx, cy), 5, (255,255,0),cv2.FILLED)


        #range jempol-telunjuk 11 - 190

        vol = np.interp(lenght,[15,120],[minVol, maxVol])
        volImg = np.interp(lenght,[11,150],[400, 150])
        volPer = np.interp(lenght,[11,150],[0, 100])
        print(int(lenght), vol)

        volume.SetMasterVolumeLevel(vol, None)



    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime

    img = cv2.flip(img, 1)
    cv2.rectangle(img, (50,int(volImg)), (85,400), (0,255,0), cv2.FILLED)
    cv2.rectangle(img, (50,150), (85,400), (0,0,255), 3)
    cv2.putText(img,f'{int(volPer)} %', (50,450), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3 )
    
    cv2.putText(img,f'FPS: {int(fps)}', (50,40), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3 )
    cv2.imshow("Control", img)
    cv2.waitKey(1)

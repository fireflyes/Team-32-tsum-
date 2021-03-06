# https://github.com/fireflyes/Team-32-tsum-
import cv2
import numpy as np
import time
import sys
import TeensySerialMouse

from PyQt5.QtWidgets import (QWidget, QHBoxLayout, 
    QLabel, QApplication)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5 import QtCore
#import all user created functions and classes
from solveGraph import *
from TeensySerialMouse import *
from findTsums import findTsums
import ADBSwipe

class GUI:
    class sample(QWidget):
        def __init__(self):
            super().__init__()
            self.initUI()
            print("Sample Init complete")
        def initUI(self):      
            hbox = QHBoxLayout(self)
            self.pixmap = QPixmap('test.png')
            self.lbl = QLabel(self)
            self.lbl.setPixmap(self.pixmap)
            self.pixmap2 = QPixmap('test.png')
            self.lbl2 = QLabel(self)
            self.lbl2.setPixmap(self.pixmap2)
            hbox.addWidget(self.lbl)
            hbox.addWidget(self.lbl2)
            self.setLayout(hbox)
            self.move(300, 200)
            self.setWindowTitle('Tsum Solver')
            self.show()
        def updateImage(self, frame):
            IMG_HEIGHT = 300
            IMG_WEIGHT = 200
            if (frame is None):
                print("iN")
                return
            height, width, bytesPerComponent = frame.shape         
            bytesPerLine = bytesPerComponent * width
            newFrame = frame.copy()
            cv2.cvtColor(frame, cv2.COLOR_BGR2RGB, newFrame)                                           
            qImg = QImage(newFrame.data, width, height, bytesPerLine, QImage.Format_RGB888)
            pixmap = QPixmap(qImg)
            self.lbl2.setPixmap(pixmap.scaled(IMG_WEIGHT, IMG_HEIGHT))
        def updateVideo(self, frame):
            VID_HEIGHT = 200
            VID_WEIGHT = 300
            if (frame is None):
                print("vN")
                return
            height, width, bytesPerComponent = frame.shape         
            bytesPerLine = bytesPerComponent * width
            newFrame = frame.copy()
            cv2.cvtColor(frame, cv2.COLOR_BGR2RGB, newFrame)                                           
            qImg = QImage(newFrame.data, width, height, bytesPerLine, QImage.Format_RGB888)
            pixmap = QPixmap(qImg)
            self.lbl.setPixmap(pixmap.scaled(VID_WEIGHT,VID_HEIGHT))
            
    def __init__(self):
        self.w = self.sample()
        self.w.resize(250, 150)
        self.w.move(300, 300)
        print(self.w)
        self.cap = cv2.VideoCapture(1)
        #ret, frame = self.cap.read()
        #ret = self.cap.set(4,1080)
        #ret = self.cap.set(3,1920)
        
    def refresh(self):
        frame2 = getVideoFrame(self.cap)
        self.w.updateVideo(frame2)
        frame = getFrame(frame2)
        self.w.updateImage(frame)
        
def myTimeout():
    print("Timer triggered.")
    myGUI.refresh()
    

#mouse = TeensySeial.MouseTeensySeialMouse()

tsm = TeensySerialMouse()
#tsm.port('COM1')
#tsm.swipe(xyList)

print("Starting application")
#myMouse = TeensySerialDisplay()
app = QApplication(sys.argv)
myGUI = GUI()
start = time.time()
seconds = 0.0
count = 0
imageTest = True
shouldtap = False
imageSize = [720, 1280]

def getVideoFrame(cap):
    ret, vFrame = cap.read()
#    vFrame = cv2.imread('test1.png',1)
    ret = cap.set(4,1080)
    ret = cap.set(3,1920)
    
    cv2.rectangle(vFrame, (50,20), (1220,690), (0,255,0), thickness=2, lineType=8, shift=0)
    """
    TODO: Having trouble getting rectangle to draw; might be because I don't have video camera.
    """
    return vFrame


def getFrame(frame):
    im = frame[20:690,50:1220].copy() #the copy is so any manipulatons to frame dont show up in im
    im = np.rot90(im)
    solvedList = parsePaths(im)
    #print(solvedList)
    if(solvedList is not None):
        for path in solvedList:
            tsm.swipe(path) 
            if(path is not None):
                for i in range(len(path)-1):
                    cv2.line(im,(path[i][0],path[i][1]),(path[i+1][0],path[i+1][1]), (0,255,0),3)
    
    return im
    
def parsePaths(frame):  
    if(frame is None):
        print("pPnull")
        return
    tsumList = findTsums(frame)
    if (tsumList is None):
        return
    if(tsumList[0] is not None):
        length = len(tsumList[0])
        if(length > 3):
            print("found all 5")
    allTsums = list()
    for thisType in range(len(tsumList[0])):
        typeList = list()
        for j in tsumList[0][thisType]:
            thisTsum  = list()
            thisTsum.append(j[0])
            thisTsum.append(j[1])
            thisTsum.append(thisType)
            typeList.append(thisTsum)
        allTsums.append(typeList)
    myMap = NodeMap()
    myMap.createMap(allTsums)
    myMap.filterMap()
    allSets = myMap.getAllConnections()
    solvedList = myMap.getAllPaths()
    if(allSets is not None):
        for connection in allSets:
            print(allSets)
            #cv2.line(frame,(connection[0][0],connection[0][1]),(connection[1][0],connection[1][1]), (255,0,0),10)
            
    
#    if(imageTest == True):
 #       tsumList[1] = cv2.resize(tsumList[1],None,fx = 0.5,fy =0.5)

    return solvedList



print("B")
timer = QtCore.QTimer()
timer.setSingleShot(False)
timer.setInterval(1000)
timer.timeout.connect(myTimeout)
timer.start(1000)
#gui.update()
#time.sleep(10000)
## When everything done, release the capture
#cap.release()
cv2.destroyAllWindows()

sys.exit(app.exec_())




#draw rectangle on non searched frame

#crop frame at same points of rectangel for searched frame before findtsums() is called then rotate

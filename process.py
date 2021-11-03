import cv2
from pathlib import Path
#from imutils.perspective import four_point_transform
#from imutils import contours
#import imutils
from math import *

def write2txt(h):
  with open('nothing.txt','w') as f:
    for i in range(len(h)):
      f.write(str(h[i][0]))
      f.write('\n')
    f.close()
  print('save successfully\n')  

def readtxt():
  H=[]
  for i in range(0,10):
    with open('nr' + str(i) + '.txt', 'r') as f:
      lines = f.readlines()
      h=[]
      for line in lines:
        line = line.replace("\n", "")
        h.append(float(line))
    H.append(h)    
  return(H)

def compare_img(Hu_moments, Hu_base):
  aux1=[]
  for i in range(len(Hu_base)):
    aux=0
    for j in range(len(Hu_base[i])):
      #aux=aux + abs(Hu_moments[j] - Hu_base[i][j])/abs(Hu_base[i][j])
      aux=aux + (Hu_moments[j][0] - Hu_base[i][j])**2
    aux1.append(sqrt(aux))

  return()


# ---- main ----

Hu_base=readtxt()

cap=cv2.VideoCapture('timestamped.mp4')

if (cap.isOpened()== False):
  print("Error opening video stream or file")

# Read until video is completed
mypath = Path().absolute()

j=0
while j<2:
  ret, frame = cap.read()
  j=j+1


while(cap.isOpened()):
  # Capture frame-by-frame
  ret, frame = cap.read()
  if ret == True:
    # Display the resulting frame
    height, width, layers = frame.shape
    new_h = int(height / 2)
    new_w = int(width / 2)
    frame = cv2.resize(frame, (new_w, new_h))
    
    cv2.imshow('Frame',frame)
    cv2.waitKey(0)
    
    crop=[]
    b=0
    for i in range(0,12):
      if((i==6) or (i==8) or (i==10)):
        b=b+4
      crop.append(frame[10:25, (570-8*i - b):(577-i*8 - b)])
      #cv2.imshow('Frame',crop[i])
      #cv2.waitKey(0)
      
    for i in range(0,12):
      imggray=cv2.cvtColor(crop[i], cv2.COLOR_BGR2GRAY)
      ret,thresh=cv2.threshold(imggray,127,255,0)

      # Calculate Moments 
      moments = cv2.moments(thresh) 
      # Calculate Hu Moments 
      huMoments = cv2.HuMoments(moments)
      # Log scale hu moments 
      for j in range(0,7):
        if(huMoments[j]==0):
          huMoments[j]=10^-20
        huMoments[j] = -1* copysign(1.0, huMoments[j]) * log10(abs(huMoments[j]))

      # now I should compare
      compare_img(huMoments, Hu_base)
      #write2txt(huMoments)

      #cv2.imshow('Frame',crop[i])
      #cv2.waitKey(0)

    if cv2.waitKey(1) & 0xFF == ord('q'):
      break
    #cv2.imwrite(str(mypath) + '/data/frame' + str(i) + '.jpg' ,frame)
    
  # Break the loop
  else: 
    break
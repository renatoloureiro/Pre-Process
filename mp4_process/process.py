import cv2
from pathlib import Path
#from imutils.perspective import four_point_transform
#from imutils import contours
#import imutils
import numpy as np
from math import *
import os
import csv   
from argparse import ArgumentParser
from pathvalidate.argparse import validate_filename_arg, validate_filepath_arg
import time


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
    with open('number_data/nr' + str(i) + '.txt', 'r') as f:
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

  return(aux1.index(min(aux1)))

def rate_test(N,r_k):
  num = input ("Enter number :")
  num=int(num)
  r=r_k*(N-1)/N + num/N
  return (r)

# --------- main ----------

start = time.time()

parser = ArgumentParser()
parser.add_argument("--filepath", type=validate_filepath_arg, help='write filepath to the *.mp4')
parser.add_argument("--filename", type=validate_filename_arg, help='write filename *.mp4')
parser.add_argument("--output_folder",type=validate_filename_arg, help='output folder where images are stored')
parser.add_argument("--output_data",type=validate_filename_arg, help='output *.csv file')

#parser.add_help()
options = parser.parse_args()

print('--Start processing--')  

if options.filename:
  print("filename: {}".format(options.filename))

if options.filepath:
  print("filepath: {}".format(options.filepath))

if options.output_folder:
  print("output folder: {}".format(options.output_folder))

if options.output_data:
  print("output *.csv file: {}".format(options.output_data))


if not os.path.exists(options.output_folder):
  os.makedirs(options.output_folder)


with open(options.output_data +'.csv', 'a') as f:
    writer = csv.writer(f)
    writer.writerow(['#timestamp [ns]',	'filename'])

Hu_base=readtxt()


cap=cv2.VideoCapture(options.filename)
#cap=cv2.VideoCapture('2022-01-29_10_15_18.mp4')

if (cap.isOpened()== False):
  print("Error opening video stream or file")

# Read until video is completed
mypath = Path().absolute()

j=0
while j<2:
  ret, frame = cap.read()
  j=j+1

rate=0
N=1

while(cap.isOpened()):
  # Capture frame-by-frame
  ret, frame = cap.read()
  if ret == True:
    # Display the resulting frame
    height, width, layers = frame.shape
    new_h = int(height / 2)
    new_w = int(width / 2)
    frame = cv2.resize(frame, (new_w, new_h))
    
    #cv2.imshow('Frame',frame)
    #cv2.waitKey(0)
    
    crop=[]
    b=0
    timestamp=[]
    for i in range(0,12):
      if((i==6) or (i==8) or (i==10)):
        b=b+4
      crop.append(frame[10:25, (570-8*i - b):(577-i*8 - b)])
      #cv2.imshow('Frame',crop[i])
      #cv2.waitKey(0)
      
    for i in range(0,12):
      imggray=cv2.cvtColor(crop[i], cv2.COLOR_BGR2GRAY)
      ret,thresh=cv2.threshold(imggray,90,255,0)

      # Calculate Moments 
      moments = cv2.moments(thresh)
      
      a = np.array([[moments['m20'], moments['m11']], 
              [moments['m11'], moments['m02']]])
      w,v=np.linalg.eig(a)
      #print(degrees(atan(v[1][1]/v[1][0])))

      

      # Calculate Hu Moments 
      huMoments = cv2.HuMoments(moments)
      # Log scale hu moments 
      for j in range(0,7):
        if(huMoments[j]==0):
          huMoments[j]=10^-20
        huMoments[j] = -1* copysign(1.0, huMoments[j]) * log10(abs(huMoments[j]))

      #write2txt(huMoments)

      # now I should compare
      aux=compare_img(huMoments, Hu_base)
      if(aux==2 or aux==5):
        if(max(w)/min(w) -10.59 >0.79):
          aux=5
        else:
          aux=2
      if(aux==2):
        if((max(w) - min(w) - 555210)>13999):
          aux=6
      if(aux==6 or aux==9):
        if((max(w) - min(w) - 583209)>12087.5):
          aux=9
        else:
          aux=6
        
      timestamp.insert(0,aux)
      #print(aux)


      #winname = "Test"
      #cv2.namedWindow(winname)        # Create a named window
      #cv2.moveWindow(winname, 1000,30)  # Move it to (40,30)
      #cv2.imshow(winname, thresh)
      #cv2.imshow('Frame',thresh)
      #cv2.waitKey(500)

      #rate=rate_test(N,rate)
      #N=N+1

      #cv2.imshow('Frame',crop[i])
      #cv2.waitKey(0)

    if cv2.waitKey(1) & 0xFF == ord('q'):
      break
    #cv2.imwrite(str(mypath) + '/data/frame' + str(i) + '.jpg' ,frame)
    #print(timestamp)
    a=timestamp[0]*10 + timestamp[1]
    b=timestamp[2]*10 + timestamp[3]
    c=timestamp[4]*10 + timestamp[5]
    d=timestamp[6]*(10**5) + timestamp[7]*(10**4) + timestamp[8]*(10**3) + timestamp[9]*(10**2) \
      + timestamp[10]*(10) + timestamp[11]

    time1=(a*3600 + b*60 + c + d*10**-6) *10**9
    #print(time)
    
    fields=[str(time1) , str(trunc(time1)) + '.png' ]

    with open(options.output_data + '.csv','a') as f:
      writer = csv.writer(f)
      writer.writerow(fields)

    cv2.imwrite( options.output_folder +'/' + str(trunc(time1)) + '.png',frame[30:540,0:960])
  # Break the loop
  else: 
    break

end = time.time()

# assign size
size = 0
 
# assign folder path
Folderpath = str(mypath) +'/' + options.output_folder
 
# get size
for path, dirs, files in os.walk(Folderpath):
    for f in files:
        fp = os.path.join(path, f)
        size += os.path.getsize(fp)
 
# display size
print("Elapsed time: " + str(int(end - start)) + 's')
print("Folder size: " + f"{size/float(1<<30):,.0f} GB")
#print("Number of frames:" + len(files))



print('--Operation done successfully--\n')  
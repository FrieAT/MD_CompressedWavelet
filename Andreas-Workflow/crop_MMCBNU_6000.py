import cv2
import numpy as np
#from matplotlib import pyplot as plt
import math
from PIL import Image
from ImageData import ScanAssets

# Klasse: MMCBNU_6000
# Threshold 0.80

#from ScanAsset import ScanAsset
#from OrigPic import OrigPic

a = ScanAssets("../images/")
a.do(None)

index = 0


#for image in a.data: # images are OrigPic Elements
 #  imagePath = image.imagePath

for imagePath in a.indexOfAssets['MMCBNU_6000']: # Slicing with [13:]

  print("Cropping (INDEX: "+str(index)+") image "+imagePath.imagePath+"...")
  index += 1

  img = cv2.pyrDown(cv2.imread(imagePath.imagePath, cv2.IMREAD_GRAYSCALE))
  imn = cv2.imread(imagePath.imagePath)


  #plt = Image.fromarray(imn)
  #plt.show()

  # threshold image
  ret, threshed_img = cv2.threshold(img,
                  20, 255, cv2.THRESH_BINARY)
  # find contours and get the external one

  contours, hier = cv2.findContours(threshed_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

  #image, contours, hier = cv2.findContours(threshed_img, cv2.RETR_TREE,
  #                cv2.CHAIN_APPROX_SIMPLE)

  # with each contour, draw boundingRect in green
  # a minAreaRect in red and
  # a minEnclosingCircle in blue
  maxarea = 0
  max2 = 0

  #cv2.cvtColor(img, cv2.COLOR_GRAY2RGB, img)

  (imWidth, imHeight) = img.shape
  imArea = imWidth * imHeight

  #framemax
  print("Contours: "+str(len(contours)))
  for c in contours:
      # get the bounding rect
     x, y, w, h = cv2.boundingRect(c)
      # draw a green rectangle to visualize the bounding rect
     cv2.rectangle(img, (x, y), (x+w, y+h), (255, 255, 255), 2)
     area = w * h
     print (area)
     if area > maxarea:
         max2 = maxarea
         maxarea = area
         framemax = (x,y, w, h)
     elif area > max2:
         max2 = area
         frame2 = (x, y, w, h)
        
  threshold = 0.80
  spaceA = (1.0 / imArea * maxarea)
  spaceB = (1.0 / imArea * max2)
  if spaceA >= threshold:
    frame2 = framemax
    print("Framemax has"+str(spaceA)+" percent space!")
  elif spaceB >= threshold:
    framemax = frame2
    print("Frame2 has"+str(spaceB)+" percent space!")

  #if framemax[1] > frame2[1]:
  #   uborder = cv2.line(img, (framemax[0], framemax[1]+framemax[3]), (framemax[0]+framemax[2], framemax[1]+framemax[3]), (255, 0, 0), 1)
  #   oborder = cv2.line(img, (frame2[0], frame2[1]),(frame2[0]+frame2[2], frame2[1]), (255, 0, 0), 1)
     
  size = img.shape

  cropX = 0
  cropWidth = size[1]
  cropY = framemax[1]
  cropHeight = 0 + (framemax[1]+framemax[3])

  if cropY >= imHeight:
    print("Fehler 1")
  if cropHeight >= imHeight:
    print("Fehler 2")
  if cropWidth >= imWidth:
    #cropWidth = imWidth - 1
    print("Fehler 3! KORRIGIERT")

  crop_img = img[cropY : cropHeight, cropX : cropWidth]
  
  partHeight, partWidth = crop_img.shape
  part_img = crop_img[math.floor(partHeight * 0.15): math.floor(partHeight * 0.85), 0: math.floor(partWidth * 0.80)]

  
  #crop_img = img[frame2[1]: 0 + (framemax[1]+framemax[3]), 0: 0 + size[1]]



  #print("Frame2 [1]: "+str(frame2[1]))
  #print("FrameMax[1] + FrameMax[3]: "+str())

  #print(len(contours))
  #cv2.drawContours(img, contours, -1, (255, 255, 0), 1)

  #print (max2)
  #print (maxarea)
  #print (frame2)
  #print (framemax)
  #print (img.shape)
  #print(crop_img.shape)

  #plt = Image.fromarray(img)
  #plt.show()

  plt = Image.fromarray(crop_img)
  plt.show()
  
  plt = Image.fromarray(part_img)
  plt.show()

  input("Press Enter to continue...")

  #plt.close()

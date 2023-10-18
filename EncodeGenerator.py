import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://faceattendancerealtime-dae39-default-rtdb.firebaseio.com/",
    'storageBucket':"faceattendancerealtime-dae39.appspot.com"
})


# Importing student images
folderPath = "Images"
pathList = os.listdir(folderPath)
print(pathList)
imgList = []
studentNames = []

# THis will tell us if we have imported all the imges or not
for path in pathList:
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
     #to just get the name and not the extensio with it
    studentNames.append(os.path.splitext(path)[0])

    fileName = f'{folderPath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)


    #print(path)
    #print(os.path.splitext(path)[0])

print(studentNames)

#to run and create the encodings we will create a function
def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)


        return encodeList
print("Encoding Started...")
encodeListKnown= findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown,studentNames] #storing the encoding with its respective name in a file

print(encodeListKnown)
print("Encoding Complete")
#pass  #loop through all the images and encode every single image

file = open("EncodeFile.p","wb")
pickle.dump(encodeListKnownWithIds, file)
file.close()
print("File Saved")


#PART-4: FACE RECOGNITION






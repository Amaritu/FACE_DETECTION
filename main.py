import os
import pickle

import cv2
import face_recognition
import numpy as np
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://faceattendancerealtime-dae39-default-rtdb.firebaseio.com/",
    'storageBucket':"faceattendancerealtime-dae39.appspot.com"
})

bucket = storage.bucket()



# Create a VideoCapture object to access the camera (0 for the default camera)
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread("ATTENDANCE SYSTEM.jpg")

# Importing the mode images
folderModePath = "Modes"
modePath = os.listdir(folderModePath)
imgModeList = [cv2.imread(os.path.join(folderModePath, path)) for path in modePath]


# This will tell us if we have imported all the images or not
for path in modePath:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

#print(len(imgModeList))

#load the encoding file

print("Loading Encode File...")
file = open('EncodeFile.p','rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentNames = encodeListKnownWithIds
#print(studentNames)
print("Encode file loaded...")

modeType = 0
counter = 0
id = -1
imgStudent = []


# Check if the camera opened successfully
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

while True:
    # Read a frame from the camera
    ret, frame = cap.read()

    # Check if the frame was read successfully
    if not ret:
        print("Error: Could not read frame.")
        break

    imgS = cv2.resize(frame,(0,0),None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurrFrame = face_recognition.face_locations(imgS)
    encodeCurrFrame = face_recognition.face_encodings(imgS, faceCurrFrame)

    imgBackground[162:162 + 480, 55:55 + 640] = frame
    imgBackground[113:113 + 535, 865:865 + 344] = imgModeList[modeType]

    if faceCurrFrame:

        for faceLoc in faceCurrFrame:
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)


    #cv2.imshow('Attendance', imgBackground)





    for encodeFace, faceLoc in zip(encodeCurrFrame, faceCurrFrame):
            matches = face_recognition.compare_faces(encodeListKnown,encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown,encodeFace) #the lower the face dist the better the match is
            #print("matches", matches)
            #print("faceDis", faceDis)

            matchIndex = np.argmin(faceDis)
             #print("Match Index", matchIndex)

            if matches[matchIndex]:
                  #print("Known Face Detected ")
                #print(studentNames[matchIndex])
                y1,x2,y2,x1 = faceLoc
                y1,x2,y2,x1 = y1*4,x2*4,y2*4,x1*4
                bbox = 640+x1, 865+y1, x2-x1, y2-y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                id = studentNames[matchIndex]
                print(id)

                if counter == 0:
                    cvzone.putTextRect(imgBackground,"Loading",(275, 400))
                    cv2.imshow("Attendance", imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1

    if counter!= 0:

            if counter == 1:
                # Get the data
                studentInfo = db.reference(f'Student/{id}').get()

                if studentInfo is not None:
                    datetimeObject = datetime.strptime(studentInfo.get('last_attended_time', ''), "%Y-%m-%d %H:%M:%S")

                    secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
                    print(secondsElapsed)

                    if secondsElapsed > 30:
                        ref = db.reference(f'Images/{id}')
                        studentInfo['total_attendance_time'] += 1
                        ref.child('total_attendance_time').set(studentInfo['total_attendance_time'])
                        ref.child('last_attended_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    else:
                        modeType = 3
                        counter = 0
                        imgBackground[113:113 + 535, 865:865 + 344] = imgModeList[modeType]
                else:
                    print(f"Student with ID {id} not found.")


            if modeType!=3:
                 if 10<counter<20:
                    modeType = 2
                    cv2.imshow("Mode", imgModeList[modeType])

                    imgBackground[113:113 + 535, 865:865 + 344] = imgModeList[modeType]
                    if counter<=10:
                        cv2.putText(imgBackground, str(studentInfo['total_attendance_time']), (861, 125),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)

                        cv2.putText(imgBackground, str(studentInfo['department']), (1006, 550),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                        cv2.putText(imgBackground, str(studentInfo['EmpID']), (1006, 493),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                        cv2.putText(imgBackground, str(studentInfo['Standing']), (910, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                        cv2.putText(imgBackground, str(studentInfo['Year']), (1025, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                        cv2.putText(imgBackground, str(studentInfo['Starting_year']), (1125, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                        (w,h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1,1)
                        offset = (414-w)//2


                        cv2.putText(imgBackground, str(studentInfo['name']), (808+offset, 445),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                        imgBackground[44:44+535, 808:808+344] = imgStudent
                        #imgBackground[175:1280, 909:1263] = imgStudent


                        counter = counter+1

                        if counter>=20:
                            counter = 0  # basically resetting everything
                            modeType = 0
                            studentInfo = []

                            imgStudent = []
                            imgBackground[113:113 + 535, 865:865 + 344] = imgModeList[modeType]

    else:
            modeType = 0
            counter = 0



            #cvzone.cornerRect(imgBackground, bbox, rt=0)




            #imgBackground[] = "Active.jpeg"
            #imgBackground[] = "Already Marked.jpeg"


            #imgBackground[162:162+480, 55:55+640] = frame
            #imgBackground[113:113+535, 865:865 + 350] = imgModeList[modeType]





            # Display the frame in a window
            #cv2.imshow('Camera', frame)
    cv2.imshow('Attendance', imgBackground)



    # Exit the loop if 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close the OpenCV window
cap.release()
cv2.destroyAllWindows()

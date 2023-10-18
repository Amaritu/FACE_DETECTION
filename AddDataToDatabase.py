import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://faceattendancerealtime-dae39-default-rtdb.firebaseio.com/"
})

ref = db.reference('Students')

data = {
    "amaritu":
        {
            "EmpId": "312745",
            "Department": "IT",
            "Starting year": 2020,
            "total_attendance_time": 19,
            "last_attended_time": "2023-10-10 00:54:34" #time to count if its enough to count in as half day/full day

        },
    "elon":
        {
            "EmpId": "319745",
            "Department": "Corp Marketing",
            "Starting year": 2019,
            "total_attendance_time": 19,
            "last_attended_time": "2023-10-10 00:54:34" #time to count if its enough to count in as half day/full day

        },
    "emma":
        {
            "EmpId": "610745",
            "Department": "HE",
            "Starting year": 2020,
            "total_attendance_time": 19,
            "last_attended_time": "2023-10-10 00:54:34" #time to count if its enough to count in as half day/full day

        }

}
for key,value in data.items():
    ref.child(key).set(value)


from firestore import db
import cv2
import face_recognition
import numpy as np
import io
import json
import pytz
import datetime

def take_attendance(request):
    try:
        # initialize return variables
        student_id_return = []
        student_name_return = []
        bounding_boxes_return = []

        image = request.files['image']
        img = convert_image_to_numpy(image.read())

        student_data, encoding_list_known = get_known_encodings()

        # change img color
        imgS = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # get all the bounding boxes of the faces in the current frame
        facesCurrFrame = face_recognition.face_locations(imgS)
        # get all the 128-dimension face encodings for all the faces in the current frame
        encodesCurrFrame = face_recognition.face_encodings(imgS, facesCurrFrame)

        # for each face detected in the frame
        for encodeFace, faceLoc in zip(encodesCurrFrame, facesCurrFrame):
            # check if the encodings of this face matches any known encodings
            matches = face_recognition.compare_faces(encoding_list_known, encodeFace)
            # get the 'distance' between this face encoding and our known faces encodings
            faceDis = face_recognition.face_distance(encoding_list_known, encodeFace)
            # find the index which has the least 'distance' (best match)
            matchIndex = np.argmin(faceDis)

            # if the matches with the index of least 'distance' is a match
            if matches[matchIndex]:
                # find the name of this student from the index
                student_id, student_name = student_data[matchIndex]
                # scale the bounding box to fit the input video stream image
                y1, x2, y2, x1 = faceLoc
                # draw the rectangle and label the rectangle with the appropriate student name
                # cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                # cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                # cv2.putText(img, student_name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                # we mark the attendance here
                mark_attendance(student_id, student_name)
                # append data
                student_id_return.append(student_id)
                student_name_return.append(student_name)
                bounding_boxes_return.append([x1, y1, x2, y2])

        return json.loads(json.dumps({ "student_id": student_id_return, "student_name": student_name_return, "bounding_boxes": bounding_boxes_return, "success": True, "error": "" }, indent=4, default=myconverter))
    except Exception as e:
        print(str(e))
        return json.loads(json.dumps({ "student_id": [], "student_name": [], "bounding_boxes": [], "success": False, "error": str(e) }, indent=4, default=myconverter))

# helper function to convert numpy arrays to python lists
def myconverter(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()

# helper function to generate encoding for image passed in
# use the face recognition library to generate 128-dimension face encodings
def get_encoding_for_image(image):
    img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    encoding = face_recognition.face_encodings(img)[0]
    return encoding

# helper function to convert input image of type Flask FileStorage to numpy arrays
def convert_image_to_numpy(image):
    file_content = io.BytesIO(image)
    file_bytes = np.asarray(bytearray(file_content.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.COLOR_BGR2RGB)
    return img

# helper function to get all known encodings
def get_known_encodings():
    docs = db.collection("students").stream()
    docs = list(map(lambda doc: doc.to_dict(), docs))
    student_data = list(map(lambda doc : (doc['student_id'], doc['student_name']), docs))
    encodings = list(map(lambda doc : doc['encodings'], docs))
    return student_data, encodings

# helper function to mark attendance
def mark_attendance(student_id, student_name):
    tz = pytz.timezone('Asia/Singapore')
    today = datetime.datetime.now(tz=tz)
    start = today.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + datetime.timedelta(days=1)
    docs = db.collection('attendance').where('student_id', '==', student_id).where('reporting_time', '>=', start).where('reporting_time', '<', end).limit(1).get()
    # mark attendance only if student have not been present today yet
    if len(docs) is 0:
        attendance_obj = {
            'student_id': student_id,
            'student_name': student_name,
            'reporting_time': today
        }
        db.collection('attendance').add(attendance_obj)
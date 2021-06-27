from firestore import db
import cv2
import face_recognition
import numpy as np
import io
import json

def register_person(request):
    try:
        student_id = request.form['student_id']
        student_name = request.form['student_name']
        student_class = request.form['student_class']
        image = request.files['image']

        image = convert_image_to_numpy(image.read())
        image = get_encoding_for_image(image)
        image = image.tolist()

        student_obj = {
            'student_id': student_id,
            'student_name': student_name,
            'student_class': student_class,
            'encodings': image
        }

        doc = check_student_exists(student_id)
        doc.set(student_obj)

        return { "success": True, "error": "" }
    except Exception as e:
        print(e)
        return { "success": False, "error": str(e) }

# helper function to check if student id already exists
# returns the student doc if the doc exists
def check_student_exists(student_id):
    docs = db.collection('students').stream()
    for doc in docs:
        if student_id == doc.to_dict()['student_id']:
            return doc
    return db.collection('students').document()

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
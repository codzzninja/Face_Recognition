import cv2
import sqlite3
import numpy as np
import os
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
recognizer = cv2.face.LBPHFaceRecognizer_create()
label_map = {}

def load_faces_from_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, face_image FROM faces")
    rows = cursor.fetchall()

    faces, labels = [], []
    label_dict, current_label = {}, 0

    for user_id, name, image_blob in rows:
        img_array = np.frombuffer(image_blob, np.uint8)
        image = cv2.imdecode(img_array, cv2.IMREAD_GRAYSCALE)
        if image is None:
            continue

        faces_detected = face_cascade.detectMultiScale(image, scaleFactor=1.1, minNeighbors=5)
        for (x, y, w, h) in faces_detected:
            face_roi = image[y:y+h, x:x+w]
            if name not in label_dict:
                label_dict[name] = current_label
                label_map[current_label] = name
                current_label += 1
            faces.append(face_roi)
            labels.append(label_dict[name])

    conn.close()
    return faces, labels

db_path = './database/face_data.db'
faces, labels = load_faces_from_db(db_path)

if faces:
    recognizer.train(faces, np.array(labels))
else:
    print("[ERROR] No faces found in database.")

@app.route('/recognize', methods=['POST'])
def recognize():
    try:
        data = request.json
        if 'image' not in data:
            return jsonify({"error": "No image provided"}), 400

        img_data = data['image']
        img_bytes = base64.b64decode(img_data.split(',')[1])
        img_array = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        if frame is None:
            return jsonify({"error": "Could not decode image"}), 400

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces_detected = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
        results = []

        for (x, y, w, h) in faces_detected:
            roi = gray[y:y+h, x:x+w]
            try:
                label, confidence = recognizer.predict(roi)
                name = label_map.get(label, "Unknown") if confidence < 100 else "Unknown"
            except:
                name = "Unknown"

            results.append({
                "name": name,
                "top": int(y),
                "right": int(x + w),
                "bottom": int(y + h),
                "left": int(x)
            })

        return jsonify({"results": results})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

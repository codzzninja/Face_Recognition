from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import sqlite3
import os
import numpy as np
import base64

app = Flask(__name__)
CORS(app)

DB_PATH = './database/face_data.db'
MODEL_PATH = 'face_model.xml'
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS faces (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    face_image BLOB NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )''')
    conn.commit()
    conn.close()

def retrain_model():
    """Reloads data from DB, trains recognizer, saves model."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, face_image FROM faces")
    rows = c.fetchall()
    conn.close()

    if not rows:
        print("[WARN] No training data found.")
        return

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    faces = []
    labels = []

    for row in rows:
        label = row[0]
        img_bytes = row[1]
        img_array = np.frombuffer(img_bytes, np.uint8)
        image = cv2.imdecode(img_array, cv2.IMREAD_GRAYSCALE)
        if image is not None:
            faces.append(image)
            labels.append(label)

    if faces and labels:
        recognizer.train(faces, np.array(labels))
        recognizer.save(MODEL_PATH)
        print(f"[INFO] Model trained and saved to {MODEL_PATH}")
    else:
        print("[WARN] No valid faces found for training.")

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        name = data.get('name')
        image_data = data.get('image')

        if not name or not image_data:
            return jsonify({'error': 'Name and image are required'}), 400

        if ',' in image_data:
            _, encoded = image_data.split(',', 1)
        else:
            encoded = image_data

        image_bytes = base64.b64decode(encoded)
        image_array = np.frombuffer(image_bytes, dtype=np.uint8)
        frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        if frame is None:
            return jsonify({'error': 'Invalid image'}), 400

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5)

        if len(faces) == 0:
            return jsonify({'error': 'No face detected'}), 400

        x, y, w, h = faces[0]
        face_roi = gray[y:y+h, x:x+w]
        success, buffer = cv2.imencode('.png', face_roi)

        if not success:
            return jsonify({'error': 'Failed to encode face image'}), 500

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO faces (name, face_image) VALUES (?, ?)", (name, buffer.tobytes()))
        conn.commit()
        conn.close()

        # Retrain model after new registration
        retrain_model()

        return jsonify({'message': f'Face for {name} registered and model updated successfully'}), 200

    except Exception as e:
        print("[EXCEPTION]", str(e))
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5001)

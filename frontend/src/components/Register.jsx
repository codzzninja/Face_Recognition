import React, { useRef, useEffect, useState } from 'react';
import * as faceapi from 'face-api.js';

function Register() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [name, setName] = useState('');
  const [modelsLoaded, setModelsLoaded] = useState(false);

  useEffect(() => {
    const loadModels = async () => {
      try {
        await Promise.all([
          faceapi.nets.tinyFaceDetector.loadFromUri('/models'),
          faceapi.nets.faceLandmark68Net.loadFromUri('/models'),
          faceapi.nets.faceRecognitionNet.loadFromUri('/models'),
        ]);
        setModelsLoaded(true);
      } catch (err) {
        console.error('Error loading models:', err);
      }
    };
    loadModels();
  }, []);

  useEffect(() => {
    async function getVideo() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (err) {
        console.error("Error accessing webcam:", err);
      }
    }
    getVideo();
  }, []);

  const handleVideoPlay = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;

    const displaySize = {
      width: video.videoWidth,
      height: video.videoHeight,
    };

    faceapi.matchDimensions(canvas, displaySize);

    const interval = setInterval(async () => {
      const detections = await faceapi
        .detectAllFaces(video, new faceapi.TinyFaceDetectorOptions())
        .withFaceLandmarks()
        .withFaceDescriptors();

      const resizedDetections = faceapi.resizeResults(detections, displaySize);
      const ctx = canvas.getContext('2d');
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      resizedDetections.forEach((d) => {
        const box = d.detection.box;
        const drawBox = new faceapi.draw.DrawBox(box, { label: name });
        drawBox.draw(canvas);
      });
    }, 100);

    return () => clearInterval(interval);
  };

  const handleRegister = async () => {
    if (!name.trim()) return alert('Please enter a name.');

    const canvas = document.createElement('canvas');
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);

    const image = canvas.toDataURL('image/png');

    try {
      const res = await fetch('http://localhost:5001/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, image }),
      });

      const data = await res.json();
      alert(data.message || data.error);
    } catch (err) {
      console.error('Error registering face:', err);
      alert('Failed to register. See console.');
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h2 style={styles.heading}>Face Registration</h2>

        <input
          type="text"
          placeholder="Enter your name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          style={styles.input}
        />

        <div style={styles.videoWrapper}>
          <video
            ref={videoRef}
            autoPlay
            muted
            playsInline
            width="400"
            height="300"
            onPlay={handleVideoPlay}
            style={styles.video}
          />
          <canvas
            ref={canvasRef}
            width="400"
            height="300"
            style={styles.canvas}
          />
        </div>

        <button onClick={handleRegister} style={styles.button}>
          Register
        </button>
      </div>
    </div>
  );
}

const styles = {
  container: {
    minHeight: '100vh',
    backgroundColor: '#f5f5f5',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    padding: '20px',
  },
  card: {
    backgroundColor: 'white',
    padding: '30px',
    borderRadius: '15px',
    boxShadow: '0 8px 20px rgba(0,0,0,0.1)',
    maxWidth: '500px',
    width: '100%',
    textAlign: 'center',
  },
  heading: {
    marginBottom: '20px',
    color: '#333',
  },
  input: {
    padding: '10px',
    width: '80%',
    fontSize: '16px',
    borderRadius: '8px',
    border: '1px solid #ccc',
    marginBottom: '20px',
    outline: 'none',
  },
  videoWrapper: {
    position: 'relative',
    width: '400px',
    height: '300px',
    margin: '0 auto 20px auto',
  },
  video: {
    position: 'absolute',
    top: 0,
    left: 0,
    borderRadius: '12px',
    zIndex: 1,
    backgroundColor: 'black',
  },
  canvas: {
    position: 'absolute',
    top: 0,
    left: 0,
    borderRadius: '12px',
    zIndex: 2,
    pointerEvents: 'none',
  },
  button: {
    padding: '12px 24px',
    fontSize: '16px',
    color: 'white',
    backgroundColor: '#4CAF50',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'background-color 0.3s',
  },
};

export default Register;

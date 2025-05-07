import React, { useEffect, useRef, useState } from "react";

function Recognize() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [loading, setLoading] = useState(true);
  const [stream, setStream] = useState(null);

  useEffect(() => {
    const startWebcam = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        setStream(stream);
        const video = videoRef.current;
        video.srcObject = stream;

        video.onloadedmetadata = () => {
          video.play();
          setLoading(false);
        };

        const canvas = canvasRef.current;
        const ctx = canvas.getContext("2d");

        const draw = async () => {
          const width = video.videoWidth;
          const height = video.videoHeight;

          if (width === 0 || height === 0) return;

          canvas.width = width;
          canvas.height = height;

          ctx.drawImage(video, 0, 0, width, height);
          const dataURL = canvas.toDataURL("image/jpeg");

          try {
            const response = await fetch("http://localhost:5000/recognize", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ image: dataURL }),
            });

            const data = await response.json();

            ctx.drawImage(video, 0, 0, width, height); // redraw video
            if (data.results) {
              data.results.forEach(({ name, top, right, bottom, left }) => {
                ctx.strokeStyle = "#00ff00";
                ctx.lineWidth = 2;
                ctx.strokeRect(left, top, right - left, bottom - top);
                ctx.fillStyle = "rgba(0, 255, 0, 0.7)";
                ctx.font = "16px Arial";
                ctx.fillText(name, left, top - 8);
              });
            }
          } catch (err) {
            console.error("Recognition error:", err);
          }
        };

        const intervalId = setInterval(draw, 1000);
        return () => clearInterval(intervalId);
      } catch (err) {
        console.error("Camera access error:", err);
      }
    };

    startWebcam();

    // Cleanup on unmount
    return () => {
      if (stream) {
        stream.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
      setStream(null);
      setLoading(true);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-gray-100 to-gray-200 px-4">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">Real-Time Face Recognition</h1>

      <div className="relative w-full max-w-2xl aspect-video rounded-xl shadow-xl border border-gray-300 bg-black overflow-hidden">
        {loading && (
          <div className="absolute z-30 w-full h-full flex items-center justify-center bg-black bg-opacity-60 text-white text-lg">
            Loading camera...
          </div>
        )}
        <video ref={videoRef} autoPlay playsInline className="hidden" />
        <canvas ref={canvasRef} className="w-full h-full" />
      </div>

      <button
        onClick={stopCamera}
        className="mt-6 px-6 py-2 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-md shadow-sm transition"
      >
        Stop Camera
      </button>
    </div>
  );
}

export default Recognize;

import cv2
import requests
import base64
from io import BytesIO
from PIL import Image
import numpy as np
import time

# =============================
# CONFIGURACIÓN DEL MODELO
# =============================
API_KEY = "PFtgraH7GtWANIvWwt1t"
MODEL = "train-detection-4ud7c"
VERSION = 1
SERVER_URL = f"http://localhost:9001/{MODEL}/{VERSION}?api_key={API_KEY}"

# =============================
# PIPELINE GSTREAMER PARA CSI
# =============================
def csi_pipeline(
        sensor_id=0,
        width=1280,
        height=720,
        fps=30):
    return (
        f"nvarguscamerasrc sensor-id={sensor_id} ! "
        f"video/x-raw(memory:NVMM), width={width}, height={height}, "
        f"format=NV12, framerate={fps}/1 ! "
        f"nvvidconv flip-method=0 ! "
        f"video/x-raw, format=BGRx ! "
        f"videoconvert ! "
        f"video/x-raw, format=BGR ! appsink"
    )

cap = cv2.VideoCapture(csi_pipeline(), cv2.CAP_GSTREAMER)

if not cap.isOpened():
    raise RuntimeError("No se pudo iniciar la cámara CSI. Revisa conexión y drivers.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Frame no válido")
        continue

    # Convertir a base64
    pil_img = Image.fromarray(frame)
    buffer = BytesIO()
    pil_img.save(buffer, format="JPEG")
    img_base64 = base64.b64encode(buffer.getvalue()).decode("ascii")

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    t0 = time.time()
    res = requests.post(SERVER_URL, data=img_base64, headers=headers)
    data = res.json()
    infer_time = time.time() - t0

    # Dibujar detecciones
    if "predictions" in data:
        for pred in data["predictions"]:
            x, y = int(pred["x"]), int(pred["y"])
            w, h = int(pred["width"]), int(pred["height"])
            cls = pred["class"]
            conf = pred["confidence"]

            x1 = x - w // 2
            y1 = y - h // 2
            x2 = x + w // 2
            y2 = y + h // 2

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
            cv2.putText(frame, f"{cls} {conf:.2f}",
                        (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0,255,0), 2)

            if "points" in pred:
                pts = np.array([[int(p["x"]), int(p["y"])] for p in pred["points"]])
                cv2.polylines(frame, [pts], True, (0,0,255), 1)

    cv2.putText(frame, f"FPS: {1/infer_time:.2f}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8, (255,255,255), 2)

    cv2.imshow("Detección Roboflow (CSI Camera)", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()

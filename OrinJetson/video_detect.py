import cv2
import requests
import base64
from io import BytesIO
from PIL import Image
import numpy as np
import time

# ==============================
# CONFIGURACIÓN DEL MODELO
# ==============================
API_KEY = "PFtgraH7GtWANIvWwt1t"
MODEL = "train-detection-4ud7c"
VERSION = 1
SERVER_URL = f"http://localhost:9001/{MODEL}/{VERSION}?api_key={API_KEY}"

# ==============================
# CONFIG VIDEO
# ==============================
VIDEO_PATH = 0  # 0 = webcam USB. Para archivo usa: "video.mp4"

cap = cv2.VideoCapture(VIDEO_PATH)

if not cap.isOpened():
    raise RuntimeError("No se pudo abrir la cámara o el video.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Fin del video.")
        break

    # Convertir frame a base64 JPEG
    pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    buffer = BytesIO()
    pil_img.save(buffer, format="JPEG")
    img_base64 = base64.b64encode(buffer.getvalue()).decode("ascii")

    # Enviar a Inference Server
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    t0 = time.time()

    res = requests.post(SERVER_URL, data=img_base64, headers=headers)
    data = res.json()

    infer_time = time.time() - t0

    # ======================
    # DIBUJAR DETECCIONES
    # ======================
    if "predictions" in data:
        for pred in data["predictions"]:
            x, y = int(pred["x"]), int(pred["y"])
            w, h = int(pred["width"]), int(pred["height"])
            cls = pred["class"]
            conf = pred["confidence"]

            x1, y1 = x - w // 2, y - h // 2
            x2, y2 = x + w // 2, y + h // 2

            # Caja
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
            cv2.putText(frame, f"{cls} {conf:.2f}",
                        (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0,255,0), 2)

            # Polígonos si existen
            if "points" in pred:
                pts = np.array([[int(p["x"]), int(p["y"])] for p in pred["points"]])
                cv2.polylines(frame, [pts], True, (0,0,255), 1)

    # Mostrar FPS
    cv2.putText(frame, f"FPS: {1/infer_time:.2f}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8, (255,255,255), 2)

    cv2.imshow("Detección Roboflow (Video)", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

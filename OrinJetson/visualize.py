import requests
import base64
from io import BytesIO
from PIL import Image
import cv2
import numpy as np

api_key = "PFtgraH7GtWANIvWwt1t"
model = "train-detection-4ud7c"
version = 1

# URL de la imagen usada antes
image_url = "https://source.roboflow.com/zD7y6XOoQnh7WC160Ae7/yA6pCzno5RW5tc3LjgSR/original.jpg"

# Descargar imagen
resp = requests.get(image_url, stream=True)
img_pil = Image.open(resp.raw)
img = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

# Codificar a Base64
buffered = BytesIO()
img_pil.save(buffered, format="JPEG")
img_str = base64.b64encode(buffered.getvalue()).decode("ascii")

# Enviar a Inference Server
headers = {"Content-Type": "application/x-www-form-urlencoded"}
res = requests.post(
    f"http://localhost:9001/{model}/{version}?api_key={api_key}",
    data=img_str,
    headers=headers,
)

data = res.json()
print(data)

# Dibujar resultados
for pred in data["predictions"]:
    x = int(pred["x"])
    y = int(pred["y"])
    w = int(pred["width"])
    h = int(pred["height"])
    cls = pred["class"]
    conf = pred["confidence"]

    # Caja
    x1 = x - w // 2
    y1 = y - h // 2
    x2 = x + w // 2
    y2 = y + h // 2

    cv2.rectangle(img, (x1, y1), (x2, y2), (0,255,0), 2)
    cv2.putText(img, f"{cls} {conf:.2f}", (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

    # Si el modelo tiene polygon (points)
    if "points" in pred:
        pts = np.array([[int(p["x"]), int(p["y"])] for p in pred["points"]])
        cv2.polylines(img, [pts], True, (0,0,255), 1)

# Guardar resultado
cv2.imwrite("resultado.jpg", img)
print("Imagen guardada como resultado.jpg")

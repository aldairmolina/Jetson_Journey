import requests
import base64
from io import BytesIO
from PIL import Image

# ============================
# 1. CONFIGURACIÓN
# ============================

api_key = "PFtgraH7GtWANIvWwt1t"
model = "train-detection-4ud7c"
version = 1

# Ejemplo: imagen pública de Roboflow
image_url = "https://source.roboflow.com/zD7y6XOoQnh7WC160Ae7/yA6pCzno5RW5tc3LjgSR/original.jpg"

# ============================
# 2. DESCARGAR IMAGEN Y CODIFICAR A BASE64
# ============================

print("[INFO] Descargando imagen...")
response = requests.get(image_url, stream=True)
response.raise_for_status()

image = Image.open(response.raw)
buffered = BytesIO()
image.save(buffered, format="JPEG", quality=100)

img_str = base64.b64encode(buffered.getvalue()).decode("ascii")

# ============================
# 3. ENVIAR A ROBFLOW INFERENCE SERVER
# ============================

print("[INFO] Enviando imagen al servidor de inferencia...")

headers = {"Content-Type": "application/x-www-form-urlencoded"}

res = requests.post(
    f"http://localhost:9001/{model}/{version}?api_key={api_key}",
    data=img_str,
    headers=headers,
)

print("[INFO] Respuesta del servidor:")
print(res.status_code)
print(res.text)

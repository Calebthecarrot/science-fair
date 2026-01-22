import cv2
import torch
import torchvision.transforms as T
import math
from model import PathNet

CLASSES = ["blocked", "unblocked", "yellow"]

# ===== CAMERA PARAMETERS (TUNE THESE) =====
FOCAL_LENGTH_PIXELS = 700        # adjust experimentally
REAL_PATH_WIDTH_M = 0.30         # meters
GRID_SIZE = 160                 # pixels

device = "cuda" if torch.cuda.is_available() else "cpu"

model = PathNet()
model.load_state_dict(torch.load("pathnet.pth", map_location=device))
model.to(device)
model.eval()

transform = T.Compose([
    T.ToPILImage(),
    T.Resize((224, 224)),
    T.ToTensor()
])

def estimate_distance(pixel_width):
    if pixel_width <= 0:
        return None
    return (REAL_PATH_WIDTH_M * FOCAL_LENGTH_PIXELS) / pixel_width

def detect_and_angle(frame):
    h, w, _ = frame.shape
    best_path = None
    min_distance = float("inf")

    for y in range(0, h - GRID_SIZE, GRID_SIZE):
        for x in range(0, w - GRID_SIZE, GRID_SIZE):
            patch = frame[y:y+GRID_SIZE, x:x+GRID_SIZE]
            if patch.size == 0:
                continue

            img = transform(patch).unsqueeze(0).to(device)

            with torch.no_grad():
                out = model(img)
                probs = torch.softmax(out, dim=1)
                cls = probs.argmax(1).item()
                conf = probs[0][cls].item()

            if conf < 0.8:
                continue

            label = CLASSES[cls]

            if label == "unblocked":
                distance = estimate_distance(GRID_SIZE)

                if distance and distance < min_distance:
                    min_distance = distance
                    best_path = {
                        "x_center": x + GRID_SIZE // 2,
                        "distance": distance
                    }

                cv2.rectangle(frame, (x,y), (x+GRID_SIZE,y+GRID_SIZE), (0,255,0), 2)
                cv2.putText(frame, f"{distance:.2f}m",
                            (x, y-5), cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, (0,255,0), 2)

            elif label == "blocked":
                cv2.rectangle(frame, (x,y), (x+GRID_SIZE,y+GRID_SIZE), (0,0,255), 2)

            elif label == "yellow":
                cv2.rectangle(frame, (x,y), (x+GRID_SIZE,y+GRID_SIZE), (0,255,255), 2)

    if best_path:
        r_pixels = best_path["x_center"] - (w // 2)
        meters_per_pixel = REAL_PATH_WIDTH_M / GRID_SIZE
        r = r_pixels * meters_per_pixel
        d = best_path["distance"]

        angle_rad = math.atan(r / d)
        angle_deg = math.degrees(angle_rad)

        return frame, angle_deg

    return frame, None

import os
import cv2
import time
import numpy as np
from deepface_scripts.model_utils import load_res10_model, face_cropped
from deepface_scripts.embed_utils import load_embeddings


def generate_dataset(user_id, num_images=200, url="http://localhost:8080/stream.mjpg"):
    print(f"[INFO] Capturing {num_images} images with faces for user {user_id} from MJPEG stream")
    images = []
    cap = None
    max_retries = 3
    retry_delay = 1

    # Initialize face detector
    detector = load_res10_model()

    # Open MJPEG stream with retries
    for attempt in range(1, max_retries + 1):
        print(f"[INFO] Opening MJPEG stream, attempt {attempt}/{max_retries}")
        cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
        if cap.isOpened():
            print("[INFO] MJPEG stream opened successfully")
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 236)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 236)
            break
        print(f"[ERROR] Failed to open MJPEG stream on attempt {attempt}")
        cap.release()
        if attempt < max_retries:
            time.sleep(retry_delay)
        else:
            print("[ERROR] Cannot open MJPEG stream after retries")
            return []

    try:
        # Warm-up frames
        for i in range(5):
            ret, frame = cap.read()
            if not ret or frame is None:
                print(f"[ERROR] Failed to read warm-up frame {i+1}/5")
                break
            time.sleep(0.1)

        # Capture images with faces
        img_count = 0
        while img_count < num_images:
            ret, frame = cap.read()
            if not ret or frame is None or not isinstance(frame, np.ndarray):
                print(f"[ERROR] Failed to capture frame {img_count+1}/{num_images}")
                time.sleep(0.1)
                continue

            # Detect face
            cropped = face_cropped(frame, detector)
            if cropped is None:
                print(f"[INFO] No face detected in frame {img_count+1}")
                time.sleep(0.1)
                continue

            # Resize to 200x200 for ArcFace/Res10
            resized = cv2.resize(cropped, (200, 200))
            images.append(resized)
            img_count += 1
            print(f"[INFO] Captured image {img_count}/{num_images}, shape: {resized.shape}")
            time.sleep(0.1)

        return images

    except Exception as e:
        print(f"[ERROR] Image capture failed: {str(e)}")
        return []

    finally:
        if cap:
            cap.release()
            print("[INFO] MJPEG stream released")

def list_users():
    embeddings = load_embeddings()
    return sorted(set(e["user_id"] for e in embeddings))
import logging
import time
import pickle
import cv2
import numpy as np
from collections import deque
from deepface import DeepFace
from scipy.spatial.distance import cosine
from typing import Dict, Any, List, Optional
from datetime import datetime

# Constants
TIMEOUT_SECONDS = 30
CAPTURE_DEVICE = 0  # Default camera index
EMBEDDING_FILE = "face_embedding.pkl"

# Setup logging (consistent with your system)
logging.basicConfig(filename="/home/salah/doorLockGui/Blynk/door_logs.txt", level=logging.INFO, format="[%(asctime)s] %(message)s")

def log_event(message: str):
    """Log an event to door_logs.txt."""
    logging.info(message)

def load_res10_model() -> Optional[Any]:
    """Load the Res10 face detection model."""
    try:
        log_event("Loading Res10 face detector")
        proto_path = "deploy.prototxt"
        model_path = "res10_300x300_ssd_iter_140000.caffemodel"
        if not os.path.exists(proto_path) or not os.path.exists(model_path):
            log_event("[ERROR] Res10 model files not found")
            return None
        net = cv2.dnn.readNetFromCaffe(proto_path, model_path)
        log_event("Res10 model loaded successfully")
        return net
    except Exception as e:
        log_event(f"[ERROR] Failed to load Res10 model: {str(e)}")
        return None

def face_cropped(image: np.ndarray, detector: Any) -> Optional[np.ndarray]:
    """Crop the detected face from an image using the Res10 detector."""
    try:
        if not isinstance(image, np.ndarray) or image.size == 0:
            log_event("[ERROR] Invalid input image for face cropping")
            return None
        h, w = image.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
        detector.setInput(blob)
        detections = detector.forward()
        confidence_threshold = 0.5
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > confidence_threshold:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                startX, startY = max(0, startX), max(0, startY)
                endX, endY = min(w - 1, endX), min(h - 1, endY)
                face = image[startY:endY, startX:endX]
                if face.size == 0:
                    log_event("[ERROR] Cropped face is empty")
                    return None
                log_event("Face cropped successfully")
                return face
        log_event("No face detected in image")
        return None
    except Exception as e:
        log_event(f"[ERROR] Face cropping failed: {str(e)}")
        return None

def capture_images(num_images: int = 10) -> List[np.ndarray]:
    """Capture a specified number of images from the default camera."""
    try:
        log_event(f"Capturing {num_images} images")
        cap = cv2.VideoCapture(CAPTURE_DEVICE)
        if not cap.isOpened():
            log_event("[ERROR] Failed to open capture device")
            return []
        images = []
        for _ in range(num_images):
            ret, frame = cap.read()
            if not ret or frame is None:
                log_event("[ERROR] Failed to capture frame")
                continue
            images.append(frame)
            time.sleep(0.1)  # Brief delay between captures
        cap.release()
        log_event(f"Captured {len(images)} images")
        return images
    except Exception as e:
        log_event(f"[ERROR] Image capture failed: {str(e)}")
        return []

def load_embeddings() -> List[Dict[str, Any]]:
    """Load face embeddings from face_embedding.pkl."""
    try:
        log_event("Loading embeddings from face_embedding.pkl")
        with open(EMBEDDING_FILE, "rb") as f:
            embeddings = pickle.load(f)
        if not isinstance(embeddings, list):
            log_event(f"[ERROR] Invalid embeddings format: expected list, got {type(embeddings)}")
            return []
        log_event(f"Loaded {len(embeddings)} embeddings")
        return embeddings
    except FileNotFoundError:
        log_event("No face_embedding.pkl found, returning empty list")
        return []
    except Exception as e:
        log_event(f"[ERROR] Failed to load embeddings: {str(e)}")
        return []

def process_face_recognition() -> Dict[str, Any]:
    """Process face recognition from captured images.
    
    Returns:
        Dict[str, Any]: Result with match status, name, and optional error.
    """
    log_event("Starting face recognition from captured images")
    
    # Validate captured images
    images = capture_images(num_images=10)
    if not images:
        log_event("[ERROR] No images captured")
        return {"match": False, "name": "error", "error": "No images captured"}
    if not all(isinstance(img, np.ndarray) for img in images):
        log_event("[ERROR] Invalid image format in captured images")
        return {"match": False, "name": "error", "error": "Invalid image format"}

    # Load Res10 model
    try:
        log_event("Loading Res10 model")
        detector = load_res10_model()
        log_event("Res10 model loaded successfully")
        if detector is None:
            log_event("[ERROR] Res10 model returned None")
            return {"match": False, "name": "error", "error": "Res10 model is None"}
    except Exception as e:
        log_event(f"[ERROR] Failed to load Res10 model: {str(e)}")
        return {"match": False, "name": "error", "error": f"Res10 model load failed: {str(e)}"}

    # Load embeddings
    try:
        log_event("Loading embeddings")
        embeddings = load_embeddings()
        log_event(f"Loaded {len(embeddings)} embeddings")
        if not embeddings:
            log_event("No embeddings available, returning unknown")
            return {"match": False, "name": "unknown"}
        # Validate embedding format
        for e in embeddings:
            if not isinstance(e, dict) or "user_id" not in e or "embeddings" not in e:
                log_event(f"[ERROR] Invalid embedding format: {e}")
                return {"match": False, "name": "error", "error": "Invalid embedding format"}
            if not isinstance(e["embeddings"], list) or not e["embeddings"]:
                log_event(f"[ERROR] Empty or invalid embeddings list for user {e.get('user_id', 'unknown')}")
                return {"match": False, "name": "error", "error": "Invalid embeddings list"}
            # Extract the first embedding entry
            emb_entry = e["embeddings"][0]
            if not isinstance(emb_entry, dict) or "embedding" not in emb_entry:
                log_event(f"[ERROR] Invalid embedding entry for user {e.get('user_id', 'unknown')}: {emb_entry}")
                return {"match": False, "name": "error", "error": "Invalid embedding entry"}
            if not isinstance(emb_entry["embedding"], (list, np.ndarray)) or len(emb_entry["embedding"]) != 512:
                log_event(f"[ERROR] Invalid embedding size for user {e.get('user_id', 'unknown')}: {len(emb_entry['embedding']) if isinstance(emb_entry['embedding'], (list, np.ndarray)) else type(emb_entry['embedding'])}")
                return {"match": False, "name": "error", "error": "Invalid embedding size"}
    except Exception as e:
        log_event(f"[ERROR] Failed to load embeddings: {str(e)}")
        return {"match": False, "name": "error", "error": f"Embeddings load failed: {str(e)}"}

    buffer = deque(maxlen=10)
    start = time.time()

    try:
        for idx, frame in enumerate(images, 1):
            if time.time() - start >= TIMEOUT_SECONDS:
                log_event("Timeout reached during processing")
                break

            # Validate frame
            if not isinstance(frame, np.ndarray) or frame.size == 0:
                log_event(f"[ERROR] Invalid frame for image {idx}: shape {frame.shape if isinstance(frame, np.ndarray) else type(frame)}")
                continue

            log_event(f"Processing image {idx}/{len(images)}, shape: {frame.shape}")
            try:
                cropped = face_cropped(frame, detector)
                if cropped is None:
                    log_event(f"⚠️ No face detected in image {idx}")
                    continue
                if not isinstance(cropped, np.ndarray) or cropped.size == 0:
                    log_event(f"[ERROR] Invalid cropped image for image {idx}: shape {cropped.shape if isinstance(cropped, np.ndarray) else type(cropped)}")
                    continue
            except Exception as e:
                log_event(f"[ERROR] Face cropping failed for image {idx}: {str(e)}")
                continue

            try:
                log_event(f"Face detected in image {idx}, running DeepFace embedding")
                result = DeepFace.represent(
                    img_path=cropped,
                    model_name="ArcFace",
                    enforce_detection=False,
                    detector_backend="opencv"
                )
                log_event(f"DeepFace output: {result}")
                if not isinstance(result, list) or not result or "embedding" not in result[0]:
                    log_event(f"[ERROR] Invalid DeepFace output format for image {idx}: {result}")
                    continue
                current_emb = result[0]["embedding"]
                if not isinstance(current_emb, (list, np.ndarray)) or len(current_emb) != 512:
                    log_event(f"[ERROR] Invalid embedding size for image {idx}: {len(current_emb) if isinstance(current_emb, (list, np.ndarray)) else type(current_emb)}")
                    continue
            except Exception as e:
                log_event(f"[ERROR] DeepFace embedding failed for image {idx}: {str(e)}")
                continue

            try:
                matched_label = "unknown"
                best_distance = float("inf")
                for e in embeddings:
                    # Use the embedding from the nested structure
                    emb = e["embeddings"][0]["embedding"]
                    dist = cosine(current_emb, emb)
                    if dist < 0.4 and dist < best_distance:
                        best_distance = dist
                        matched_label = e["user_id"]
                buffer.append(matched_label)
                log_event(f"Buffer: {list(buffer)}")
            except Exception as e:
                log_event(f"[ERROR] Cosine distance calculation failed for image {idx}: {str(e)}")
                continue

            if len(buffer) == buffer.maxlen:
                final = max(set(buffer), key=buffer.count)
                result = {
                    "match": final != "unknown",
                    "name": final
                }
                log_event(f"Face recognition result: {result}")
                # Publish to MQTT (assuming global client)
                try:
                    client.publish("smartlock/logs", f"{datetime.now()} - Face recognition result: {result}")
                    log_event("Published face recognition result to MQTT topic smartlock/logs")
                except NameError:
                    log_event("[WARNING] MQTT client not defined, skipping publish")
                return result

        log_event("Timeout reached or no valid faces recognized")
        return {"match": False, "name": "unknown"}

    except Exception as e:
        log_event(f"[ERROR] Face recognition failed: {str(e)}")
        return {"match": False, "name": "error", "error": str(e)}
import os
import pickle
import cv2
import numpy as np
from deepface import DeepFace
from .model_utils import load_res10_model, face_cropped
from sklearn.cluster import DBSCAN

def extract_embeddings_from_memory(user_id, images):
    embeddings = []
    for idx, img in enumerate(images, 1):
        if not isinstance(img, np.ndarray):
            continue
        try:
            emb = DeepFace.represent(
                img_path=img,
                model_name="ArcFace",
                enforce_detection=False,
                detector_backend="opencv"
            )[0]["embedding"]
            embeddings.append({"user_id": user_id, "embedding": emb})
        except Exception as e:
            print(f"[INFO] Error processing image {idx}: {str(e)}")
    return embeddings

def remove_outliers(embeddings, target_user_ids=None, eps=0.4, min_samples=5):
    if not embeddings:
        return []
    if target_user_ids:
        embeddings = [e for e in embeddings if e["user_id"] in target_user_ids]
    emb_vectors = [e["embedding"] for e in embeddings]
    clustering = DBSCAN(eps=eps, min_samples=min_samples, metric="cosine").fit(emb_vectors)
    filtered = [e for e, label in zip(embeddings, clustering.labels_) if label != -1]
    return filtered

def load_embeddings(file_path="/home/salah/doorLockGui/deepface_scripts/face_embeddings.pkl"):
    try:
        if not os.path.exists(file_path):
            return []
        with open(file_path, "rb") as f:
            return pickle.load(f)
    except Exception:
        return []

def save_embeddings(embeddings, file_path="/home/salah/doorLockGui/deepface_scripts/face_embeddings.pkl"):
    with open(file_path, "wb") as f:
        pickle.dump(embeddings, f)
import cv2
import numpy as np
from deepface_scripts import data_utils, embed_utils
import pickle
import uuid
from core.user_profile import UserProfile, save_user_profile
from hardware.fp_utils import enroll_fingerprint
from hardware.aggregator import log_event

def start_face_embedding_extraction(user_id):
    """Capture images and store face embeddings for a user."""
    try:
        # Capture 200 images
        images = data_utils.generate_dataset(user_id)
        if not images:
            raise ValueError("Failed to capture images")
        
        # Extract and filter embeddings
        embeddings = embed_utils.extract_embeddings_from_memory(user_id, images)
        filtered_embeddings = embed_utils.remove_outliers(embeddings)
        if not filtered_embeddings:
            raise ValueError("No valid embeddings after filtering")
        
        # Load existing embeddings
        existing_embeddings = embed_utils.load_embeddings()
        
        # Append new embeddings
        new_entry = {
            "user_id": user_id,
            "embeddings": filtered_embeddings
        }
        existing_embeddings.append(new_entry)
        
        # Save updated embeddings
        embed_utils.save_embeddings(existing_embeddings)
        log_event(f"Face embeddings saved for user ID {user_id}")
        return True
    except Exception as e:
        log_event("[ERROR] Failed to extract face embeddings", str(e))
        return False

def add_new_user(user_id, name, role, fp_position):
    """Add a new user with fingerprint and face embeddings."""
    try:
        log_event(f"Adding new user {name} (ID: {user_id})")
        
        # Save user profile
        user_profile = UserProfile(
            id=user_id,
            name=name,
            role=role,
            fingerprint_position=str(fp_position)
        )
        save_user_profile(user_profile)
        
        log_event(f"[SUCCESS] Added user {name} (ID: {user_id}, FP: {fp_position})")
        return user_id
    
    except Exception as e:
        log_event("[ERROR] Failed to add new user", str(e))
        return None

def delete_existing_user(user_id):
    emb = load_embeddings()
    filtered = [e for e in emb if e["user_id"] != user_id]
    save_embeddings(filtered)
    print(f"[INFO] User {user_id}'s embeddings were removed")

# Retained for testing
def generate_embeddings(user_id):
        try:
            images = data_utils.generate_dataset(user_id)
            embeddings = embed_utils.extract_embeddings_from_memory(user_id , images)
            filtered_embeddings = embed_utils.remove_outliers(embeddings)
            embed_utils.save_embeddings(filtered_embeddings)
        except Exception as e:
            print(f"[ERROR] Failed to generate embeddings: {e}")

if __name__ == "__main__":
    generate_embeddings("29113972-deb7-48a5-891d-a7e33010b999")

import os
import cv2
import numpy as np

MODEL_DIR = "deepface_scripts/model"

def load_res10_model():
    model_path = "/home/salah/doorLockGui/deepface_scripts/model/res10_300x300_ssd_iter_140000.caffemodel"
    config_path = "/home/salah/doorLockGui/deepface_scripts/model/deploy.prototxt"
    return cv2.dnn.readNetFromCaffe(config_path, model_path)

def detect_faces_from_frame(net, frame, conf_threshold=0.9):
    h, w = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), [104, 117, 123], False, False)
    net.setInput(blob)
    detections = net.forward()
    faces = []
    for i in range(detections.shape[2]):
        if detections[0, 0, i, 2] > conf_threshold:
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (x1, y1, x2, y2) = box.astype("int")
            faces.append({"box": (x1, y1, x2 - x1, y2 - y1)})
    return faces

def face_cropped(img, detector):
    faces = detect_faces_from_frame(detector, img)
    if not faces:
        return None
    x, y, w, h = faces[0]["box"]
    return img[y:y+h, x:x+w]
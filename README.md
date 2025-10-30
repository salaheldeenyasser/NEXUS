# Secure Computerized Control System Based on AI with IoT Compatibility

![MUST Logo](https://smartlearning.must.edu.eg/pluginfile.php/1/core_admin/logocompact/300x300/1715171530/logo.png)  
**Misr University for Science and Technology**  
**Faculty of Engineering – Department of Computer and Software**

---

## Project Title
**Secure computerized control system based on AI with IoT compatibility to identify users.**

### B.E. Final Project  
**Date:** 14/6/2025

---

## Presented By
| Name                |
|---------------------|
| Adham Ahmed         | 
| Salah Eldeen Yasser |
| Bassel Ahmed        | 
| Yousuf Ahmed        | 
| Amr Khaled          | 
| Ahmed Mostafa       | 

**Supervised by:** *Dr. Abdelhameed Sharaf*  
**Mentor:** *Eng. Nizar Hussein*

---

## Abstract

Traditional security systems rely on single-factor authentication (keys, NFC cards, keypads), making them vulnerable to spoofing. This project introduces a **versatile multi-factor authentication control unit** that enhances both **security and usability**.

### Key Features:
- Face detection & recognition
- Fingerprint scanning
- Keypad entry
- Smartphone remote access with live video
- Configurable authentication layers (1–3 factors)
- Role-based access: **Admin** and **Normal User**
- IoT integration via **Blynk** for remote control
- Intuitive GUI on Raspberry Pi touch screen

**Target Application:** Smart door lock  
**Use Cases:** Bank lockers, high-security labs, control rooms, offices

---

## Table of Contents
1. [Introduction](#introduction)  
2. [Features](#features)  
3. [Hardware](#hardware)  
4. [Software](#software)  
5. [Installation](#installation)  
6. [Usage](#usage)  
7. [Market Research](#market-research)  
8. [Limitations & Future Work](#limitations--future-work)  
9. [Contributors](#contributors)  
10. [Acknowledgements](#acknowledgements)  
11. [License](#license)

---

## Introduction

This repository contains the source code, documentation, and resources for our Bachelor of Engineering final project at Misr University for Science and Technology.

The system addresses vulnerabilities in traditional security by providing multi-factor authentication with AI and IoT integration, demonstrated via a smart door lock.

For detailed background, significance, challenges, objectives, and market research, refer to Chapter 1 in [`GradBookV3.pdf`](./GradBook/GradBookV3.pdf).

---

## Features

- **Multi-Factor Authentication** (Face + Fingerprint + Keypad + Phone)
- **Configurable Security Levels** (1 to 3 factors)
- **Remote Live Video Feed** for admin verification
- **Smartphone Control** via Blynk IoT app
- **User Role Management** (Admin / Normal)
- **AI-Powered Face Recognition** using **ArcFace**
- **Touchscreen GUI** for local interaction
- **Battery Backup & Power Management**

---

## Hardware

| Component | Description |
|---------|-----------|
| **Raspberry Pi 5** | Main processing unit |
| **MPI3201 Touch Screen** | 3.5" display for GUI |
| **NodeMCU ESP8266** | Wi-Fi & IoT communication |
| **Raspberry Pi Camera V1.3** | Face detection |
| **R301T Fingerprint Module** | Biometric authentication |
| **Solenoid Lock + 5V Relay** | Door control |
| **PIR Sensor (SR501)** | Motion detection |
| **18650 Li-ion Battery + BMS** | Backup power |
| **12V Power Supply + Step-Down** | Stable power delivery |

> Full circuit diagrams, block diagrams, and live photos are in [`GradBookV3.pdf`](./GradBook/GradBookV3.pdf) (Section 3.1).

---

## Software

- **OS:** Raspberry Pi OS
- **Language:** Python
- **AI Model:** ArcFace (Face Recognition)
- **GUI:** Custom Python-based touchscreen interface
- **IoT Platform:** Blynk (Remote access & video)
- **Libraries:** OpenCV, TensorFlow/Keras, PyFingerprint, BlynkLib

### GUI Screens
- Home Screen
- Admin Login
- Main Settings
- User Management
- Add User / Fingerprint Enrollment

For AI steps, dataset creation, and performance metrics, see Section 3.2 in the PDF.

---

##  Modules Overview

- `capture_faces.py`  
  Captures webcam images of a user's face and stores them under their unique ID for training.

- `extract_embeddings.py`  
  Extracts facial embeddings using ArcFace, removes outliers, and saves clean vectors to a `.pkl` file.

- `real_time_infer.py`  
  Performs real-time face recognition via webcam. Sends the result to a FastAPI backend for access evaluation.

- `face_utils.py`  
  Contains helper functions for loading the face detection model and extracting faces from images.

---

## Installation

### 1. Hardware Assembly
Follow the block diagrams in the PDF:
- Power System
- Main Unit
- ESP8266 Board
- Electric Lock Circuit

### 2. Software Setup

#### 1. Clone repository
```
git clone https://github.com/salaheldeenyasser/NEXUS.git
cd NEXUS
```
#### 2. Install Dependencies

Install required libraries using pip:

```bash
pip install opencv-python deepface requests scipy numpy
```

Make sure DeepFace also installs TensorFlow and related backends.

#### 3. Prepare Face Detection Model

Place the following files inside:
```
models/res10/
├── deploy.prototxt
└── res10_300x300_ssd_iter_140000.caffemodel
```

#### 4. Capture Faces

```bash
python capture_faces.py
```

#### 5. Extract Embeddings

```bash
python extract_embeddings.py
```

#### 6. Run Real-Time Recognition

```bash
python real_time_infer.py
```
#### 7. Configure Blynk (see config/blynk_config.md)

### 3. API Integration

The recognition script sends results to:

```
POST http://localhost:8000/access/
```

With JSON body:
```json
{
  "pin": null,
  "face_result": {
    "match": true,
    "name": "Ahmed"
  },
  "fingerprint_result": null
}
```

### 4. Project Structure

```
.
├── capture_faces.py
├── extract_embeddings.py
├── real_time_infer.py
├── face_utils.py
├── face_embeddings.pkl
├── models/
│   └── res10/
│       ├── deploy.prototxt
│       └── res10_300x300_ssd_iter_140000.caffemodel
├── data/
│   └── {user_id}/user.{user_id}.{n}.jpg
└── README.md
```

#### - Notes

- Set `pin_toggle`, `face_toggle`, and `finger_toggle` in backend settings.
- Works best with clean, evenly lit face images.
- Additional biometric inputs can be integrated later (e.g., fingerprint).

### 3. Blynk App Setup
1. Download **Blynk** app
2. Create new project
3. Scan QR code or enter Auth Token
4. Configure virtual pins for:
   - Door unlock
   - Live video stream
   - Notifications

Detailed software configuration in Section 3.3-3.4 of the PDF.

---

## Usage

### Local Access (Touchscreen)
1. Wake system via PIR or touch
2. Select authentication method(s)
3. Authenticate using face, fingerprint, or keypad
4. Door unlocks if all required factors pass

### Remote Access (Phone)
1. Receive push notification on motion
2. View live video
3. Approve/Deny access

### Admin Mode
- Log in with credentials
- Add/delete users
- Enroll fingerprints & faces
- Configure security level
- Promote users to admin

---

## Market Research

Analyzed 4 existing smart lock systems:
- **Device 1–4**: Outdoor/indoor views in PDF (Section 1.6)
- Common flaws: single-factor, no remote video, poor UI
- Our system addresses these with **multi-layer AI + IoT**

---

## Limitations & Future Work

| Limitations | Future Enhancements |
|-----------|---------------------|
| Limited face dataset size | Cloud-based face database |
| No encryption on video stream | End-to-end encrypted video |
| Battery life ~6–8 hours | Solar charging integration |
| Local processing only | Edge + Cloud hybrid AI |

See Chapter 4 in the PDF for more.

---

## Contributors

- **Adham Ahmed** – Hardware & Power Systems
- **Salah Eldeen Yasser** – AI & Face Recognition
- **Bassel Ahmed** – IoT & Blynk Integration
- **Yousuf Ahmed** – GUI & System Software
- **Amr Khaled** – Fingerprint & Sensors
- **Ahmed Mostafa** – Documentation & Testing

---

## Acknowledgements

We deeply thank:
- **Dr. Abdelhameed Sharaf** – Project Supervisor
- **Eng. Nizar Hussein** – Technical Mentor
- Our **team members** for dedication and collaboration
- Our **families** for unwavering support

---

## License

MIT License

Copyright (c) 2025 MUST Computer Engineering Team

Permission is hereby granted, free of charge, to any person obtaining a copy...

See [`LICENSE`](./LICENSE) for full details.

---

**Project Documentation:** [`GradBookV3.pdf`](./GradBook/GradBookV3.pdf)  
**Date:** June 14, 2025  
**Institution:** Misr University for Science and Technology

---

#!/usr/bin/python3
import time
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput
import io
import logging
import socketserver
from http import server
from threading import Condition

# Updated HTML page with clean styling
PAGE = """\
<html>
<head>
<title>Pi Camera Stream</title>
<style>
    body { margin: 0; padding: 0; background: #f0f0f0; }
    .video-container { 
        width: 236px; 
        height: 236px; 
        overflow: hidden;
        margin: 50px auto;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }
    img { 
        width: 236px;
        height: 236px;
        object-fit: cover;
        display: block;
    }
</style>
</head>
<body>
<div class="video-container">
    <img src="stream.mjpg" />
</div>
</body>
</html>
"""

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()
        return len(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.send_header('Connection', 'keep-alive')  # ✅ Ensure stream stays open
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning('Removed streaming client %s: %s', self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

# Initialize camera
picam2 = Picamera2()

# Create a configuration for a square video (236x236)
video_config = picam2.create_video_configuration(main={"size": (236, 236)})
picam2.configure(video_config)

# Manually set white balance to fix red/blue tint
picam2.set_controls({
    "AwbMode": 0,  # Manual mode
    "ColourGains": (1.8, 1.3)  # Red gain, Blue gain — tweak if needed
})

# Set up streaming
output = StreamingOutput()
encoder = JpegEncoder()
picam2.start_recording(encoder, FileOutput(output))

# Set framerate for smoother video
picam2.set_controls({"FrameRate": 30})

try:
    address = ('', 8080)
    server = StreamingServer(address, StreamingHandler)
    print("Server started at http://localhost:8080")
    server.serve_forever()
finally:
    picam2.stop_recording()

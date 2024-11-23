import cv2
import platform
import os

def initialize_camera():
    """Initialize camera with optimal settings for face detection"""
    if platform.system() == 'Darwin':  # macOS
        os.environ['OPENCV_AVFOUNDATION_SKIP_AUTH'] = '1'
        camera = cv2.VideoCapture(0)
    else:
        camera = cv2.VideoCapture(0)
    
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    camera.set(cv2.CAP_PROP_FPS, 30)
    
    return camera

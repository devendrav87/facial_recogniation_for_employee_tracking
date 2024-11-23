import cv2
import platform
import os

class CameraConfig:
    @staticmethod
    def get_camera():
        # Set environment variables for macOS
        if platform.system() == 'Darwin':  # macOS
            os.environ['OPENCV_AVFOUNDATION_SKIP_AUTH'] = '1'
            os.environ['OPENCV_AVFOUNDATION_PREFERRED_CAPTURE_API'] = 'AVCaptureSessionPresetHigh'
            
            # Try different camera indices and APIs
            camera_options = [
                (0, cv2.CAP_AVFOUNDATION),
                (1, cv2.CAP_AVFOUNDATION),
                (0, cv2.CAP_ANY),
                (1, cv2.CAP_ANY)
            ]
            
            for idx, api in camera_options:
                camera = cv2.VideoCapture(idx, api)
                if camera.isOpened():
                    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                    camera.set(cv2.CAP_PROP_FPS, 30)
                    return camera
                    
        # Default fallback for other systems
        return cv2.VideoCapture(0)

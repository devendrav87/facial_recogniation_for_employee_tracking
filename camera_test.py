import cv2
import numpy as np

def test_camera():
    print("Starting camera test...")
    cap = cv2.VideoCapture(0)
    
    # Set higher resolution for better face detection
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    
    while True:
        ret, frame = cap.read()
        if ret:
            # Add frame information overlay
            height, width = frame.shape[:2]
            cv2.putText(frame, f'Resolution: {width}x{height}', 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                       1, (0, 255, 0), 2)
            
            cv2.imshow('Camera Test', frame)
            
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_camera()

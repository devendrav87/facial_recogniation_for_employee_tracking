import cv2
import face_recognition
import numpy as np
from models.database import Session, Employee
import pickle
import time

def register_employee_face():
    print("Starting employee registration...")
    cap = cv2.VideoCapture(0)
    
    # Set camera properties for better quality
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    # Get employee details
    employee_id = input("Enter employee ID: ")
    name = input("Enter employee name: ")
    
    face_samples = []
    print("\nPlease look at the camera. Capturing 5 samples...")
    
    while len(face_samples) < 5:
        ret, frame = cap.read()
        if ret:
            # Display the frame
            cv2.imshow('Registration', frame)
            
            # Find faces in the frame
            face_locations = face_recognition.face_locations(frame)
            
            if face_locations:
                # Get face encoding
                face_encoding = face_recognition.face_encodings(frame, face_locations)[0]
                face_samples.append(face_encoding)
                print(f"Sample {len(face_samples)} captured!")
                
                # Draw rectangle around face
                top, right, bottom, left = face_locations[0]
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.imshow('Registration', frame)
                
                # Wait between samples
                time.sleep(1)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    if face_samples:
        # Calculate average encoding
        final_encoding = np.mean(face_samples, axis=0)
        
        # Save to database
        session = Session()
        employee = Employee(
            id=int(employee_id),
            name=name,
            face_encoding=pickle.dumps(final_encoding)
        )
        session.add(employee)
        session.commit()
        print(f"\nSuccessfully registered {name} with ID {employee_id}")
    else:
        print("No face samples captured. Please try again.")

if __name__ == "__main__":
    register_employee_face()

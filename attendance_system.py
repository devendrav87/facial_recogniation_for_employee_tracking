import cv2
import face_recognition
import numpy as np
from datetime import datetime, timedelta, time
from models.database import Session, Employee, Attendance, DailyReport
import pickle
import dlib
import os
from pathlib import Path
from sqlalchemy import func

class AttendanceSystem:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.face_detector = dlib.get_frontal_face_detector()
        
        base_path = Path(__file__).parent
        model_path = base_path / "models" / "data" / "shape_predictor_68_face_landmarks.dat"
        recognition_model_path = base_path / "models" / "data" / "dlib_face_recognition_resnet_model_v1.dat"
        
        if not model_path.exists():
            raise FileNotFoundError(f"Shape predictor model not found at {model_path}")
        if not recognition_model_path.exists():
            raise FileNotFoundError(f"Recognition model not found at {recognition_model_path}")
            
        self.shape_predictor = dlib.shape_predictor(str(model_path))
        self.face_encoder = dlib.face_recognition_model_v1(str(recognition_model_path))
        self.load_known_faces()
        
    def load_known_faces(self):
        session = Session()
        try:
            employees = session.query(Employee).all()
            for employee in employees:
                face_encoding = pickle.loads(employee.face_encoding)
                self.known_face_encodings.append(face_encoding)
                self.known_face_names.append(employee.name)
            print(f"Successfully loaded {len(employees)} employee faces")
        except Exception as e:
            print(f"Face loading error: {str(e)}")
        finally:
            session.close()
            
    def process_frame(self, frame):
        if frame is None:
            return None, []
            
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = self.face_detector(rgb_frame)
        detected_faces = []
        
        for face_location in face_locations:
            shape = self.shape_predictor(rgb_frame, face_location)
            face_encoding = np.array(self.face_encoder.compute_face_descriptor(rgb_frame, shape))
            
            if self.known_face_encodings:
                matches = face_recognition.compare_faces(
                    self.known_face_encodings, 
                    face_encoding,
                    tolerance=0.6
                )
                
                if True in matches:
                    first_match_index = matches.index(True)
                    name = self.known_face_names[first_match_index]
                    
                    status = self.get_current_attendance_status(name)
                    color = (0, 255, 0) if status.get('status') == 'entry' else (0, 0, 255)
                    
                    left = face_location.left()
                    top = face_location.top()
                    right = face_location.right()
                    bottom = face_location.bottom()
                    
                    detected_faces.append({
                        'name': name,
                        'location': (left, top, right, bottom),
                        'status': status.get('status', 'unknown')
                    })
                    
                    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                    status_text = f"{name} ({status.get('status', 'unknown')})"
                    cv2.putText(frame, status_text, (left, top - 10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)
                    
                    self.log_attendance(name)
        
        return frame, detected_faces
            
    def log_attendance(self, name):
        session = Session()
        try:
            employee = session.query(Employee).filter_by(name=name).first()
            if not employee:
                print(f"Employee {name} not found")
                return
                
            last_record = session.query(Attendance)\
                .filter_by(employee_id=employee.id)\
                .order_by(Attendance.timestamp.desc())\
                .first()
                
            current_time = datetime.now()
            
            if not last_record:
                event_type = 'entry'
            else:
                event_type = 'exit' if last_record.event_type == 'entry' else 'entry'
                time_diff = (current_time - last_record.timestamp).total_seconds()
                if time_diff < 30:
                    return
            
            attendance = Attendance(
                employee_id=employee.id,
                timestamp=current_time,
                event_type=event_type
            )
            session.add(attendance)
            session.commit()
            
            print(f"Successfully logged {event_type} for {name} at {current_time.strftime('%H:%M:%S')}")
            
        except Exception as e:
            print(f"Attendance logging error: {str(e)}")
            session.rollback()
        finally:
            session.close()

    def calculate_total_time_inside(self, employee_id, date):
        session = Session()
        try:
            start_date = datetime.strptime(date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            end_date = start_date.replace(hour=23, minute=59, second=59)
            
            attendance_records = session.query(Attendance)\
                .filter_by(employee_id=employee_id)\
                .filter(Attendance.timestamp.between(start_date, end_date))\
                .order_by(Attendance.timestamp).all()
            
            total_time_inside = timedelta()
            entry_time = None
            time_blocks = []
            
            for record in attendance_records:
                if record.event_type == 'entry':
                    entry_time = record.timestamp
                elif record.event_type == 'exit' and entry_time:
                    duration = record.timestamp - entry_time
                    total_time_inside += duration
                    time_blocks.append({
                        'entry': entry_time.strftime('%H:%M:%S'),
                        'exit': record.timestamp.strftime('%H:%M:%S'),
                        'duration': str(duration)
                    })
                    entry_time = None
            
            total_seconds = total_time_inside.total_seconds()
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            
            return {
                'total_hours': hours,
                'total_minutes': minutes,
                'formatted_time': f"{int(hours)}h {int(minutes)}m",
                'total_seconds': total_seconds,
                'time_blocks': time_blocks,
                'date': date
            }
            
        finally:
            session.close()
            
    def generate_daily_report(self, employee_id, date):
        session = Session()
        try:
            report_date = datetime.strptime(date, '%Y-%m-%d') if isinstance(date, str) else date
            start_date = report_date.replace(hour=0, minute=0, second=0)
            end_date = report_date.replace(hour=23, minute=59, second=59)
            
            attendance_records = session.query(Attendance)\
                .filter_by(employee_id=employee_id)\
                .filter(Attendance.timestamp.between(start_date, end_date))\
                .order_by(Attendance.timestamp).all()
            
            time_stats = self.calculate_total_time_inside(employee_id, date)
            attendance_details = time_stats['time_blocks']
            
            report = {
                'date': report_date.strftime('%Y-%m-%d'),
                'total_hours': time_stats['total_hours'],
                'total_minutes': time_stats['total_minutes'],
                'formatted_time': time_stats['formatted_time'],
                'details': attendance_details,
                'time_analysis': {
                    'total_time_inside': time_stats['formatted_time'],
                    'time_blocks': time_stats['time_blocks']
                }
            }
            
            return report
            
        except Exception as e:
            print(f"Daily report generation error: {str(e)}")
            return None
        finally:
            session.close()
        
    def generate_weekly_report(self, employee_id, start_date, end_date):
        session = Session()
        try:
            daily_reports = []
            current_date = start_date
            
            while current_date <= end_date:
                daily_stats = self.calculate_total_time_inside(employee_id, current_date.strftime('%Y-%m-%d'))
                daily_reports.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'hours': daily_stats['total_hours'],
                    'minutes': daily_stats['total_minutes'],
                    'formatted_time': daily_stats['formatted_time']
                })
                current_date += timedelta(days=1)
            
            total_seconds = sum(report['hours'] * 3600 + report['minutes'] * 60 for report in daily_reports)
            total_hours = total_seconds // 3600
            total_minutes = (total_seconds % 3600) // 60
            
            return {
                'total_time': f"{int(total_hours)}h {int(total_minutes)}m",
                'daily_breakdown': daily_reports
            }
            
        except Exception as e:
            print(f"Weekly report generation error: {str(e)}")
            return None
        finally:
            session.close()
        
    def get_current_attendance_status(self, name):
        session = Session()
        try:
            employee = session.query(Employee).filter_by(name=name).first()
            if not employee:
                return {'status': 'unknown', 'last_timestamp': None}
                
            last_record = session.query(Attendance)\
                .filter_by(employee_id=employee.id)\
                .order_by(Attendance.timestamp.desc())\
                .first()
                
            if last_record:
                return {
                    'status': last_record.event_type,
                    'last_timestamp': last_record.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                }
            return {
                'status': 'unknown',
                'last_timestamp': None
            }
            
        except Exception as e:
            print(f"Status check error: {str(e)}")
            return {'status': 'unknown', 'last_timestamp': None}
        finally:
            session.close()

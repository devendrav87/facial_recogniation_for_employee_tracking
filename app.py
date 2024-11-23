from flask import Flask, render_template, jsonify, request, Response, make_response
from flask_cors import CORS
from flask_cors import CORS
from attendance_system import AttendanceSystem
from camera_utils import initialize_camera
from datetime import datetime
from models.database import Session, Employee, Attendance, DailyReport
import cv2

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

attendance_system = AttendanceSystem()

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_camera')
def start_camera():
    camera = initialize_camera()
    if not camera.isOpened():
        return jsonify({'status': 'error', 'message': 'Camera initialization failed'})
    
    while True:
        ret, frame = camera.read()
        if not ret:
            break
            
        processed_frame, detected_faces = attendance_system.process_frame(frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    camera.release()
    return jsonify({'status': 'success'})

@app.route('/video_feed')
def video_feed():
    def generate_frames():
        camera = initialize_camera()
        try:
            while True:
                ret, frame = camera.read()
                if not ret:
                    break
                    
                processed_frame, _ = attendance_system.process_frame(frame)
                
                if processed_frame is not None:
                    ret, buffer = cv2.imencode('.jpg', processed_frame)
                    if ret:
                        frame_bytes = buffer.tobytes()
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        finally:
            camera.release()
    
    response = Response(generate_frames(),
                       mimetype='multipart/x-mixed-replace; boundary=frame')
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/users')
def get_users():
    session = Session()
    try:
        employees = session.query(Employee).all()
        users_list = [{
            'id': emp.id,
            'name': emp.name,
            'status': attendance_system.get_current_attendance_status(emp.id)
        } for emp in employees]
        return jsonify({
            'status': 'success',
            'users': users_list
        })
    finally:
        session.close()

@app.route('/users/delete-all', methods=['POST'])
def delete_all_users():
    session = Session()
    try:
        session.query(Employee).delete()
        session.query(Attendance).delete()
        session.query(DailyReport).delete()
        session.commit()
        return jsonify({
            'status': 'success',
            'message': 'All users and related data deleted successfully'
        })
    finally:
        session.close()

@app.route('/register', methods=['POST'])
def register_employee():
    data = request.get_json()
    name = data.get('name')
    employee_id = data.get('employee_id')
    
    if not name or not employee_id:
        return jsonify({
            'status': 'error',
            'message': 'Name and employee ID are required'
        })
    
    success = attendance_system.register_employee(name, employee_id)
    
    if success:
        return jsonify({
            'status': 'success',
            'message': f'Employee {name} registered successfully'
        })
    return jsonify({
        'status': 'error',
        'message': 'Registration failed'
    })

@app.route('/reports/daily/<employee_id>')
def get_daily_report(employee_id):
    date_str = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    report = attendance_system.generate_daily_report(int(employee_id), date_str)
    
    if report:
        return jsonify({
            'status': 'success',
            'data': report
        })
    return jsonify({
        'status': 'error',
        'message': 'Report generation failed'
    })

@app.route('/reports/weekly/<employee_id>')
def get_weekly_report(employee_id):
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date or not end_date:
        return jsonify({
            'status': 'error',
            'message': 'Start and end dates are required'
        })
    
    report = attendance_system.generate_weekly_report(
        int(employee_id),
        datetime.strptime(start_date, '%Y-%m-%d'),
        datetime.strptime(end_date, '%Y-%m-%d')
    )
    
    if report:
        return jsonify({
            'status': 'success',
            'data': report
        })
    return jsonify({
        'status': 'error',
        'message': 'Weekly report generation failed'
    })

@app.route('/status/<employee_id>')
def get_status(employee_id):
    status = attendance_system.get_current_attendance_status(int(employee_id))
    if status:
        return jsonify({
            'status': 'success',
            'data': status
        })
    return jsonify({
        'status': 'error',
        'message': 'Status check failed'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010, debug=True)

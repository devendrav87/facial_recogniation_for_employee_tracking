# Employee Attendance System

A modern facial recognition-based attendance tracking system that provides real-time monitoring and comprehensive reporting.

## Features

- Real-time face detection and recognition
- Automated attendance logging
- Daily and weekly attendance reports
- Time tracking analysis
- User-friendly web interface
- Responsive design

## Prerequisites

- Python 3.8+
- OpenCV
- dlib
- SQLAlchemy
- Face Recognition library
- Webcam access

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/employee_attendance_system.git
cd employee_attendance_system

2. Create and activate virtual environment:
python -m venv venv
source venv/bin/activate  # For Linux/Mac
venv\Scripts\activate     # For Windows

3.Install required packages:
pip install -r requirements.txt

4. Download dlib models:
mkdir -p models/data
# Download shape_predictor_68_face_landmarks.dat and dlib_face_recognition_resnet_model_v1.dat
# Place them in models/data directory

5. Initialize the database:
python models/database.py

Usage
1. Start the application:
python app.py

2. Access the web interface:
Open browser and navigate to http://localhost:5000
Register employees using the registration form
Start tracking attendance automatically

Project Structure
employee_attendance_system/
├── app.py
├── attendance_system.py
├── models/
│   ├── database.py
│   └── data/
├── static/
│   ├── css/
│   └── js/
└── templates/

API Endpoints
/register - Register new employees
/users - List all registered users
/reports/daily/<id> - Get daily attendance report
/reports/weekly/<id> - Get weekly attendance report
/status/<id> - Check employee status

Development
1. Install development dependencies:
pip install -r requirements-dev.txt

2. Run tests:
python -m pytest tests/

python -m pytest tests/



from flask import Flask, render_template, request, jsonify, Response
from flask_socketio import SocketIO
import cv2

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/alert_page')
def alert_page():
    return render_template('alert_page.html')

@app.route('/detect')
def detect():
    return render_template('detect.html')

@app.route('/send_alert', methods=['POST'])
def send_alert():
    data = request.get_json()
    message = data.get("message", "🐅 Tiger Detected!")
    socketio.emit("new_alert", {"message": message})
    return jsonify({"status": "success"})

def detect_tiger(frame):
    # Optional: use actual model here if you want to display detection in feed
    return frame

def generate_frames():
    cap = cv2.VideoCapture(0)
    while True:
        success, frame = cap.read()
        if not success:
            break
        frame = detect_tiger(frame)
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    socketio.run(app, debug=True)

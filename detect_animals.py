import cv2
import time
import torch
import requests

model = torch.hub.load('ultralytics/yolov5', 'custom', path='best.pt') 

# ESP32 Server IP
ESP32_IP = "http://192.168.69.42"  

# Open laptop camera
cap = cv2.VideoCapture(0)

def send_alert_to_server():
    try:
        # Send alert to ESP32
        requests.get(f"{ESP32_IP}/alert")
        print("✅ Alert sent to ESP32!")

        # Send alert to Web Page (Flask)
        url = "http://127.0.0.1:5000/send_alert"
        data = {"message": "⚠️ Tiger Detected! LED & Buzzer ON!"}
        requests.post(url, json=data)
        print("✅ Alert sent to Web Page!")
    except Exception as e:
        print("❌ Failed to send alert:", e)

while True:
    ret, frame = cap.read()
    if not ret:
        break


    results = model(frame)
    detections = results.pandas().xyxy[0]   


    for _, row in detections.iterrows():
        if row['name'].lower() == 'tiger':  
            # Draw bounding box
            x1, y1, x2, y2 = int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax'])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"Tiger {row['confidence']:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            
            # Send alert
            send_alert_to_server()
            time.sleep(5)  # avoid spamming

    cv2.imshow("Tiger Detector", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

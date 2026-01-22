import cv2
from vision_distance import detect_and_angle
from serial_control import send_angle

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame, angle = detect_and_angle(frame)

    if angle is not None:
        angle = max(-45, min(45, angle))
        send_angle(angle)

        cv2.putText(frame, f"Steering: {angle:.1f} deg",
                    (20,40), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (255,0,0), 2)

    cv2.imshow("Autonomous Navigation", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()

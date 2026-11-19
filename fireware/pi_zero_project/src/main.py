import time
import cv2  # type: ignore[reportMissingImports]
import RPi.GPIO as GPIO  # type: ignore[reportMissingModuleSource]

LED_PIN = 21
BUZZER_PIN = 5
SERVO_PAN_PIN = 12
SERVO_TILT_PIN = 13

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.setup(SERVO_PAN_PIN, GPIO.OUT)
GPIO.setup(SERVO_TILT_PIN, GPIO.OUT)

pan_pwm = GPIO.PWM(SERVO_PAN_PIN, 50)
tilt_pwm = GPIO.PWM(SERVO_TILT_PIN, 50)
pan_pwm.start(7.5)
tilt_pwm.start(7.5)


def set_servo_angle(pwm_obj, angle):
    duty = 2.5 + (angle / 18.0)
    pwm_obj.ChangeDutyCycle(duty)
    time.sleep(0.1)


def trigger_alert(enable=True):
    if enable:
        GPIO.output(LED_PIN, GPIO.HIGH)
        GPIO.output(BUZZER_PIN, GPIO.HIGH)
    else:
        GPIO.output(LED_PIN, GPIO.LOW)
        GPIO.output(BUZZER_PIN, GPIO.LOW)


def main_study_loop():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    print("Система мониторинга учебы запущенна...")

    current_pan = 90
    not_focused_counter = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Ошибка получения кадра с камеры")
                time.sleep(1)
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(50, 50),
            )

            if len(faces) > 0:
                x, _, w, _ = faces[0]

                face_center_x = x + w // 2
                frame_center_x = frame.shape[1] // 2

                if abs(face_center_x - frame_center_x) > 50:
                    if face_center_x > frame_center_x and current_pan > 10:
                        current_pan -= 2
                    elif face_center_x < frame_center_x and current_pan < 170:
                        current_pan += 2
                    set_servo_angle(pan_pwm, current_pan)

                not_focused_counter = 0
                trigger_alert(False)
                print("Статус: Ученик учится [OK]")

            else:
                not_focused_counter += 1
                print(f"Внимание: Ученик не в фокусе ({not_focused_counter})")

                if not_focused_counter > 15:
                    trigger_alert(True)

            time.sleep(0.3)

    except KeyboardInterrupt:
        print("Остановка программы...")
    finally:
        trigger_alert(False)
        pan_pwm.stop()
        tilt_pwm.stop()
        cap.release()
        GPIO.cleanup()


if __name__ == "__main__":
    main_study_loop()

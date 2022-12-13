import cv2
from gas_analysis.gas_detection import motion_detector



video = cv2.VideoCapture() ### add path to file

while True:
    cap = video
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    if (motion_detector(cap) == 0):
        cap.release()
        break
    
import cv2
import os
import numpy as np


def motion_detector(videofile, record_result=False):
    window_raw = "Raw video"
    cv2.namedWindow(window_raw)
    cv2.moveWindow(window_raw, 0, 0)

    # Load video file
    if videofile is None:
        print("Could not find video file")
        return

    previous_frame = None

    frame_width = int(videofile.get(3))
    frame_height = int(videofile.get(4))
    size = (frame_width, frame_height)

    if record_result:
        result = cv2.VideoWriter(
            os.path.join(
                os.path.dirname(__file__), "../../videos/results/Gas_detection.mp4"
            ),
            cv2.VideoWriter_fourcc(*"MP4V"),
            18,
            size,
        )

    while True:
        # 1. Load image
        ret, frame = videofile.read()

        if ret:
            cv2.imshow(window_raw, frame)

            # 2. Prepare image; grayscale and blur
            prepared_frame = preprocess_frame(frame)

            # Set previous frame and continue if there is None
            if previous_frame is None:
                previous_frame = prepared_frame
                continue

            thresh_frame = find_pixel_motion(prepared_frame, previous_frame)
            previous_frame = prepared_frame

            boxed_frame = draw_bounding_boxes(thresh_frame, frame)

            finished_frame = boxed_frame
            if record_result:
                result.write(finished_frame)
        else:
            break

        # press escape to exit
        if cv2.waitKey(30) == 27:
            return 0

    cv2.destroyAllWindows()
    # videofile.release()
    if record_result:
        result.release()
    return 1


def preprocess_frame(frame):
    window_preprocessed = "Preprocessed video"
    cv2.namedWindow(window_preprocessed)
    cv2.moveWindow(window_preprocessed, 320, 0)

    prepared_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    prepared_frame = cv2.GaussianBlur(src=prepared_frame, ksize=(5, 5), sigmaX=0)

    cv2.imshow(window_preprocessed, prepared_frame)
    return prepared_frame


def find_pixel_motion(frame, previous_frame):
    window_motion = "Video motion"
    cv2.namedWindow(window_motion)
    cv2.moveWindow(window_motion, 0, 265)

    # calculate difference and update previous frame
    diff_frame = cv2.absdiff(src1=previous_frame, src2=frame)
    diff_frame[np.where(previous_frame == 0)] = 0
    diff_frame[np.where(frame == 0)] = 0

    # Dilute the image a bit to make differences more seeable; more suitable for contour detection
    diff_frame = cv2.dilate(diff_frame, np.ones((1, 1)), 1)

    # Only take different areas that are different enough (>20 / 255)
    thresh_frame = cv2.threshold(
        src=diff_frame, thresh=3, maxval=255, type=cv2.THRESH_BINARY
    )[1]
    cv2.imshow(window_motion, thresh_frame)
    return thresh_frame


def draw_bounding_boxes(thresh_frame, frame):
    window_finished = "Thermal Video"
    cv2.namedWindow(window_finished)
    cv2.moveWindow(window_finished, 640, 265)

    boxed_frame = frame
    contours, _ = cv2.findContours(
        image=thresh_frame, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE
    )
    for contour in contours:
        if cv2.contourArea(contour) < 25:
            # too small: skip!
            continue
        (x, y, w, h) = cv2.boundingRect(contour)
        cv2.rectangle(
            img=boxed_frame,
            pt1=(x, y),
            pt2=(x + w, y + h),
            color=(0, 255, 0),
            thickness=2,
        )

    cv2.imshow(window_finished, boxed_frame)
    return boxed_frame

import cv2
import os
import numpy as np


def motion_detector(videofile, record_result=False):
    window_raw = "Raw video"
    window_test1 = "Test1"
    cv2.namedWindow(window_raw)
    cv2.namedWindow(window_test1)
    cv2.moveWindow(window_raw, 0, 0)
    cv2.moveWindow(window_test1, 640, 0)

    # Load video file
    if videofile is None:
        print("Could not find video file")
        return

    previous_frame = None
    saturated_pixels = None
    frame_number = 0

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
            prepared_frame = preprocess_frame(frame)
            if(frame_number == 0):
                saturated_pixels = find_saturated_pixels(prepared_frame)
            
            # # 2. Prepare image; grayscale and blur
            denoised_frame = denoise_frame(videofile, prepared_frame, frame_number, saturated_pixels)

            # Set previous frame and continue if there is None
            if previous_frame is None:
                previous_frame = denoised_frame
                continue

            thresh_frame = find_pixel_motion(denoised_frame, previous_frame)
            previous_frame = denoised_frame

            boxed_frame = draw_bounding_boxes(thresh_frame, frame)

            finished_frame = boxed_frame
            if record_result:
                result.write(finished_frame)
        else:
            break

        print(frame_number)
        frame_number+=1

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

    # diluted_frame = cv2.dilate(prepared_frame, np.ones((5, 5)), 1)
    # blurred_frame = cv2.GaussianBlur(src=diluted_frame, ksize=(25, 25), sigmaX=0)
    # blurred_frame = diluted_frame
    # test_frame = cv2.cvtColor(prepared_frame, cv2.COLOR_GRAY2BGR)

    #remove hot areas
    # hot_area_frame = cv2.threshold(src=blurred_frame, thresh=230, maxval=255, type=cv2.THRESH_TOZERO_INV)[1]

    # hot_area_frame = cv2.threshold(src=blurred_frame, thresh=np.percentile(frame, 95), maxval=255, type=cv2.THRESH_BINARY)[1]
    # cold_area_frame = cv2.threshold(src=blurred_frame, thresh=np.percentile(frame, 5), maxval=255, type=cv2.THRESH_BINARY_INV)[1]
    # prepared_frame = cv2.subtract(prepared_frame, hot_area_frame)
    # prepared_frame = cv2.subtract(prepared_frame, cold_area_frame)

    # prepared_frame = cv2.GaussianBlur(src=prepared_frame, ksize=(5, 5), sigmaX=0)

    # for i in range(0, 8):
    #     indexes = np.where(prepared_frame == i)
    #     frame[indexes]=[0, 0, 100+30*i]

    cv2.imshow(window_preprocessed, prepared_frame)
    cv2.imwrite('test2.jpg', prepared_frame)
    return prepared_frame

def find_saturated_pixels(frame):
    diluted_frame = cv2.dilate(frame, np.ones((5, 5)), 1)
    blurred_frame = cv2.GaussianBlur(src=diluted_frame, ksize=(25, 25), sigmaX=0)
    hot_area_frame = cv2.threshold(src=blurred_frame, thresh=np.percentile(blurred_frame, 95), maxval=255, type=cv2.THRESH_BINARY)[1]
    return hot_area_frame

def denoise_frame(videofile, frame, frame_number, saturated_pixels):
    window_denoised = "denoised video"
    cv2.namedWindow(window_denoised)
    cv2.moveWindow(window_denoised, 320, 265)
    window_size = 5

    if (frame_number < window_size//2 or frame_number > videofile.get(cv2.CAP_PROP_FRAME_COUNT)-window_size//2):
        denoised_frame = frame
        
    else:
        videofile.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        frames = [videofile.read()[1] for i in range(window_size)]
        for i, frame in enumerate(frames):
            frames[i] = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        frame_number_in_window = window_size//2
        denoised_frame = cv2.fastNlMeansDenoisingMulti(
            srcImgs=frames,
            imgToDenoiseIndex=frame_number_in_window,
            temporalWindowSize=window_size,
            h=2
        )
        cv2.imwrite('test.jpg', denoised_frame)
    denoised_frame= cv2.subtract(denoised_frame, saturated_pixels)
    cv2.imshow(window_denoised, denoised_frame)
    print(denoised_frame)
    return denoised_frame

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
        src=diff_frame, thresh=1, maxval=255, type=cv2.THRESH_BINARY
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

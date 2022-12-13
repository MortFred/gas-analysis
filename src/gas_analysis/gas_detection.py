import cv2
import numpy as np
  

def motion_detector(videofile):
    window_raw = "Raw video"
    window_preprocessed = "Preprocessed video"
    window_motion = "Video motion"
    window_finished = "Thermal Video"
    window_test1 = "Test1"
    cv2.namedWindow(window_raw)
    cv2.namedWindow(window_preprocessed)
    cv2.namedWindow(window_motion)
    cv2.namedWindow(window_finished)
    cv2.namedWindow(window_test1)
    cv2.moveWindow(window_raw, 0, 0)
    cv2.moveWindow(window_preprocessed, 320, 0)
    cv2.moveWindow(window_motion, 0, 265)
    cv2.moveWindow(window_finished, 320, 265)
    cv2.moveWindow(window_test1, 640, 0)

    # Setup video windows so that they don't overlap

    # Load video file
    if videofile is None:
        print("Could not find video file")
        return
    
    previous_frame = None

    frame_width = int(videofile.get(3))
    frame_height = int(videofile.get(4))
    size = (frame_width, frame_height)
    outer_bounds = [frame_width, 0, frame_height, 0] #[xmin, xmax, ymin, ymax]
    result = cv2.VideoWriter('Results/Gas_detection.mp4',cv2.VideoWriter_fourcc(*'MP4V'), 18, size)



    high_activity_areas = [outer_bounds]
    activity_percentage = 0.8
    activity_area_pixel_margin = 50

    
    while True:
        # 1. Load image
        ret, frame = videofile.read()

        if ret:
            cv2.imshow(window_raw, frame)

            # # 2. Prepare image; grayscale and blur
            prepared_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            prepared_frame = cv2.GaussianBlur(src=prepared_frame, ksize=(7,7), sigmaX=0)
            cv2.imshow(window_preprocessed, prepared_frame)

            # 3. Set previous frame and continue if there is None
            if (previous_frame is None):
                previous_frame = prepared_frame
                continue

            # calculate difference and update previous frame
            diff_frame = cv2.absdiff(src1=previous_frame, src2=prepared_frame)
            previous_frame = prepared_frame
            
            # 4. Dilute the image a bit to make differences more seeable; more suitable for contour detection
            kernel = np.ones((1, 1))
            diff_frame = cv2.dilate(diff_frame, kernel, 1)

            # 5. Only take different areas that are different enough (>20 / 255)
            thresh_frame = cv2.threshold(src=diff_frame, thresh=3, maxval=255, type=cv2.THRESH_BINARY)[1]
            cv2.imshow(window_motion, thresh_frame)

            finished_frame = frame
            contours, _ = cv2.findContours(image=thresh_frame, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                if cv2.contourArea(contour) < 5:
                    # too small: skip!
                    continue
                (x, y, w, h) = cv2.boundingRect(contour)
                cv2.rectangle(img=finished_frame, pt1=(x, y), pt2=(x + w, y + h), color=(0, 255, 0), thickness=2)

            cv2.imshow(window_finished, finished_frame)
            result.write(finished_frame)



#----------------------------------------------------------------------------
            # for contour in contours:
            #     contour_placed_in_area = False
            #     if cv2.contourArea(contour) < 5:
            #         # too small: skip!
            #         continue
            #     [x, y, w, h] = cv2.boundingRect(contour)
            #     contour_border = [x, x+w, y, y+h]
            #     for area_border in high_activity_areas:
            #         # for i in range(0, 4):
            #         #     if(abs(contour_border[i]-area_border[i])>activity_area_pixel_margin):
            #         #         continue
            #         cont = cv2.drawContours(frame, area_border, -1, (255,0,0), 1)
            #         if(cv2.pointPolygonTest(cont, (x,y), True)):
            #             continue
            #         area_border = [min(area_border[0], contour_border[0]), max(area_border[1], contour_border[1]), min(area_border[2], contour_border[2]), max(area_border[3], contour_border[3])]






            # cv2.rectangle(img=frame, pt1=(outer_bounds[0], outer_bounds[2]), pt2=(outer_bounds[1], outer_bounds[3]), color=(0, 0, 255), thickness=2)
            
            # cv2.imshow(window_test1, frame)
#----------------------------------------------------------------------------

        
        else:
            break

        # press escape to exit
        if (cv2.waitKey(30) == 27):
            return 0

    cv2.destroyAllWindows()
    # videofile.release()
    # result.release()
    return 1


# def main():
#     cap = cv2.VideoCapture('/Users/MORFRE/Pictures/Mongstad/Flir dataset nov 2022/112ppm hydrogen/Leak/MOV_1669.mp4')
#     motion_detector(cap)

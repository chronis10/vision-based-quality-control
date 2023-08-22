import cv2
import numpy as np
from datetime import datetime, timedelta
import os
import subprocess
import time

def generate_frames(number,bgr_frame,draw_number,delay,fps=30):
    
    font = cv2.FONT_HERSHEY_SIMPLEX    
    frame_time_interval = 1.0 / fps

    while True:
        
        frame = bgr_frame.copy()      
        
        if draw_number:
            # Put the number in the middle        
            (w, h), _ = cv2.getTextSize(str(number), font, 2, 2)
            cv2.putText(frame, str(number), ((640 - w) // 2, (480 + h) // 2), font, 2, (0, 0, 0), 2, cv2.LINE_AA)
        
        # Get the current datetime
        curr_datetime = (datetime.now() - timedelta(seconds=delay)).strftime('%d-%m-%Y %H:%M:%S')
        
        # Put a black rectangle for the datetime background
        cv2.rectangle(frame, (10, 440), (390, 470), (0, 0, 0), -1)
        
        # Put the datetime text
        cv2.putText(frame, curr_datetime, (20, 460), font, 0.6, (255, 255, 255), 1, cv2.LINE_AA)

        # Return the frame
        yield frame

        time.sleep(frame_time_interval)

def main():
    number = os.getenv("VIDEO_NUMBER", "1")
    host  = os.getenv("RTSP_SERVER", "localhost")
    stream_name = os.getenv("STREAM_NAME", "stream")
    delay = float(os.getenv("STREAM_DELAY", "0.1").strip())
    # Start the FFmpeg process
    cmd = [
        'ffmpeg',
        '-y',
        '-f', 'rawvideo',
        '-vcodec', 'rawvideo',
        '-pix_fmt', 'bgr24',
        '-s', '640x480',
        '-i', '-',
        '-c:v', 'libx264',
        '-f', 'rtsp',
        f'rtsp://{host}:8554/{stream_name}'
    ]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    background_image_path = os.getenv("BACKGROUND_IMAGE", None)
    if background_image_path and os.path.exists(background_image_path):
        bgr_frame = cv2.imread(background_image_path)
        bgr_frame = cv2.resize(bgr_frame, (640, 480))
        draw_number= False
    else:
        draw_number= True
        bgr_frame = np.ones((480, 640, 3),dtype=np.uint8) * 255

    for frame in generate_frames(number,bgr_frame,draw_number,delay):
        p.stdin.write(frame.tobytes())
        
    p.stdin.close()
    p.wait()

if __name__ == '__main__':
    main()

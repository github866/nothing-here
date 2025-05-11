import cv2
import numpy as np
from moviepy.editor import VideoFileClip

def detect_black_bar_width(frame, threshold=10):
    height, width, _ = frame.shape
    # Detect left black bar
    left = 0
    for x in range(width):
        if np.mean(frame[:, x, :]) > threshold:
            left = x
            break
    # Detect right black bar
    right = 0
    for x in range(width-1, -1, -1):
        if np.mean(frame[:, x, :]) > threshold:
            right = width - 1 - x
            break
    return left, right

def center_video(input_path, output_path, target_width=1920):
    cap = cv2.VideoCapture(input_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    temp_video = 'temp_no_audio.mp4'
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(temp_video, fourcc, fps, (target_width, height))

    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        left_black, right_black = detect_black_bar_width(frame)
        diff = left_black - right_black
        crop_left = max(diff // 2, 0)
        cropped = frame[:, crop_left:width, :]
        pad_right = target_width - cropped.shape[1]
        if pad_right < 0:
            cropped = cropped[:, :target_width, :]
            pad_right = 0
        right_pad = np.zeros((height, pad_right, 3), dtype=np.uint8)
        centered_frame = np.hstack((cropped, right_pad))
        centered_frame = centered_frame[:, :target_width, :]
        out.write(centered_frame)

        frame_count += 1
        if frame_count % 30 == 0:
            progress = (frame_count / total_frames) * 100
            print(f"Processing: {progress:.1f}%")

    cap.release()
    out.release()
    print("Video processing completed!")

    # Add audio back using moviepy
    print("Adding audio back to the video...")
    original = VideoFileClip(input_path)
    processed = VideoFileClip(temp_video)
    processed = processed.set_audio(original.audio)
    processed.write_videofile(output_path, codec='libx264', audio_codec='aac', fps=fps)
    print("Audio added. Final video saved.")

if __name__ == "__main__":
    input_video = "a9.mp4"  # Replace with your input video path
    output_video = "a9 out.mp4"  # Replace with your desired output path
    center_video(input_video, output_video) 
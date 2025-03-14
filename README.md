# Video Clipper

A simple GUI application for clipping videos based on timestamps with frame preview.

## Features

- Load video files (MP4, AVI, MOV, MKV)
- View video duration
- Display video frames at specific timestamps
- Play/pause video with adjustable playback speed
- Interactive timeline slider for quick navigation
- Navigate through video with frame-by-frame precision
- Set start and end timestamps for clipping
- Export clipped video segments with high quality preservation
- Maintains original video bitrate and frame rate (FPS)

## Requirements

- Python 3.6+
- MoviePy
- Pillow (PIL)
- NumPy
- Tkinter (usually comes with Python)

## Installation

1. Clone or download this repository

2. Install tkinter (if not already installed):
   
   **On Ubuntu/Debian/WSL:**
   ```bash
   sudo apt-get update
   sudo apt-get install python3-tk
   ```
   
   **On Fedora/RHEL:**
   ```bash
   sudo dnf install python3-tkinter
   ```
   
   **On macOS (with Homebrew):**
   ```bash
   brew install python-tk
   ```
   
   **On Windows:**
   Tkinter is included with the standard Python installation.

3. Install the required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:

```bash
python3 clip.py
```

2. Click "Browse" to select a video file
3. Use the playback controls to navigate through the video:
   - Click "Play/Pause" to start/stop playback
   - Use the timeline slider to quickly jump to any position
   - Adjust playback speed (0.25x to 2.0x)
   - Use frame navigation buttons for precise control
4. Set the start and end timestamps for your clip:
   - Navigate to the desired start frame and click "Set Current" under Start Time
   - Navigate to the desired end frame and click "Set Current" under End Time
5. Click "Clip Video" to create a clip
6. Choose a location to save the clipped video

## Video Navigation

### Playback Controls
- Play/Pause button to start/stop video playback
- Timeline slider for quick navigation through the video
- Playback speed control (0.25x, 0.5x, 0.75x, 1.0x, 1.5x, 2.0x)

### Frame Navigation Buttons
- Use the navigation buttons for precise control:
  - ◀◀ -10s: Move back 10 seconds
  - ◀ -1s: Move back 1 second
  - ◀ -0.1s: Move back 0.1 seconds (frame-by-frame)
  - ▶ +0.1s: Move forward 0.1 seconds (frame-by-frame)
  - ▶ +1s: Move forward 1 second
  - ▶▶ +10s: Move forward 10 seconds
- Or enter a specific timestamp and click "Show Frame"

## WSL/X11 Display Setup

If you're using WSL (Windows Subsystem for Linux), you'll need to set up X11 forwarding to display the GUI:

1. Install an X server on Windows (like VcXsrv, Xming, or X410)
2. Start the X server
3. In WSL, set the DISPLAY environment variable:
   ```bash
   export DISPLAY=:0
   ```
   You can add this to your ~/.bashrc file to make it permanent.

## Timestamp Format

Timestamps are in the format: `minutes:seconds:milliseconds`

Example: `01:30:500` represents 1 minute, 30 seconds, and 500 milliseconds.

## Video Quality

The application prioritizes quality preservation when clipping videos:
- Maintains the original video's frame rate (FPS)
- Attempts to maintain the original video's bitrate
- Uses high quality H.264 encoding settings:
  - Very slow preset for maximum quality
  - CRF (Constant Rate Factor) of 17 for visually lossless quality
  - High profile encoding
  - Level 4.2 for wide device compatibility
- If original bitrate cannot be detected, uses a high quality default (20 Mbps)

## Playback

- Preview playback uses the video's original frame rate
- Playback speed can be adjusted (0.25x to 2.0x) while maintaining frame accuracy
- Frame-by-frame navigation respects the video's original frame intervals
- The status bar shows the video's FPS when loaded

## Notes

- The application uses MoviePy for video processing
- Video encoding uses H.264 (libx264) for video and AAC for audio
- Default bitrate is set to 5000k
- Frame display uses PIL/Pillow for image processing 
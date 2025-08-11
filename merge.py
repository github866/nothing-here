from moviepy.editor import VideoFileClip, concatenate_videoclips
import os

start = 1
end = 6
text = "it"
num = 11
output_video_path = "neon"+str(num)+".mp4" 

def get_video_info(video_path):
    """Get video information to use as reference"""
    with VideoFileClip(video_path) as clip:
        return {
            'fps': clip.fps,
            'size': clip.size,
            'duration': clip.duration,
            'bitrate': getattr(clip.reader, 'infos', {}).get('video_bitrate', 20000000)  # Default to 20Mbps if not found
        }

 # Changed output filename to be more descriptive

# List of video files to merge
video_files = [f"{text}{i}.mp4" for i in range(start, end + 1)]  # Changed to match your file naming pattern

# Verify all files exist before starting
missing_files = [f for f in video_files if not os.path.exists(f)]
if missing_files:
    print("Error: The following files are missing:")
    for f in missing_files:
        print(f"- {f}")
    exit(1)

# Get reference video info from first video
reference_info = get_video_info(video_files[0])

# Verify all videos have matching properties
for video_file in video_files[1:]:
    info = get_video_info(video_file)
    if info['size'] != reference_info['size']:
        print(f"Warning: {video_file} has different dimensions: {info['size']} vs {reference_info['size']}")
    if abs(info['fps'] - reference_info['fps']) > 0.1:  # Allow small FPS differences
        print(f"Warning: {video_file} has different FPS: {info['fps']} vs {reference_info['fps']}")

# Load all video clips
video_clips = [VideoFileClip(video_file) for video_file in video_files]

# Concatenate video clips
merged_video = concatenate_videoclips(video_clips, method="compose")

# Output file name

# Calculate target bitrate (use highest bitrate from input videos)
target_bitrate = str(int(reference_info['bitrate'])) + 'k'

print("Starting video merge with the following settings:")
print(f"- Number of clips: {len(video_clips)}")
print(f"- Resolution: {reference_info['size']}")
print(f"- FPS: {reference_info['fps']}")
print(f"- Target bitrate: {target_bitrate}")

# Write the merged video to a file with high quality settings
merged_video.write_videofile(
    output_video_path, 
    codec="libx264", 
    audio_codec="aac",
    preset="veryslow",  # Highest quality compression
    bitrate=target_bitrate,
    fps=reference_info['fps'],  # Use original FPS
    ffmpeg_params=[
        "-crf", "17",  # Lower CRF = higher quality (17-18 is visually lossless)
        "-movflags", "+faststart",  # Optimize for web playback
        "-profile:v", "high",  # Use high profile for better quality
        "-level", "4.2"  # Compatibility level
    ]
)

# Clean up
for clip in video_clips:
    clip.close()

print(f"\nMerge completed successfully!")
print(f"Merged video saved to: {output_video_path}")
print(f"Output video settings:")

# Report final video info without enforcing 1080p
reference_info = get_video_info(output_video_path)
print(f"- Resolution: {tuple(reference_info['size'])}")
print(f"- FPS: {reference_info['fps']}")
print(f"- Bitrate: {target_bitrate}")
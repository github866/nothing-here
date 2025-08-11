import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
from moviepy.editor import VideoFileClip
import re
from PIL import Image, ImageTk
import numpy as np
import tempfile
import time
import threading

class VideoClipperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Clipper")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        self.video_path = None
        self.current_video = None
        self.temp_dir = tempfile.TemporaryDirectory()
        self.current_number = 1  # Initialize counter for file naming
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # File selection
        file_frame = ttk.LabelFrame(main_frame, text="Video File", padding="10")
        file_frame.pack(fill=tk.X, pady=10)
        
        self.file_path_var = tk.StringVar()
        ttk.Label(file_frame, textvariable=self.file_path_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(file_frame, text="Browse", command=self.browse_file).pack(side=tk.RIGHT)
        
        # Frame display
        frame_frame = ttk.LabelFrame(main_frame, text="Current Frame", padding="10")
        frame_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.frame_canvas = tk.Canvas(frame_frame, bg="black")
        self.frame_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Playback controls
        playback_frame = ttk.Frame(main_frame)
        playback_frame.pack(fill=tk.X, pady=5)
        
        # Timeline slider
        self.timeline_var = tk.DoubleVar(value=0)
        self.timeline_slider = ttk.Scale(
            playback_frame, 
            from_=0, 
            to=100,  # Will be updated when video is loaded
            orient=tk.HORIZONTAL,
            variable=self.timeline_var,
            command=self.on_timeline_change
        )
        self.timeline_slider.pack(fill=tk.X, padx=10, pady=5)
        
        # Playback control buttons
        btn_frame = ttk.Frame(playback_frame)
        btn_frame.pack(fill=tk.X, padx=10)
        
        self.play_button = ttk.Button(
            btn_frame, 
            text="▶ Play",
            command=self.toggle_playback
        )
        self.play_button.pack(side=tk.LEFT, padx=5)
        
        # Add playback speed control
        speed_frame = ttk.Frame(btn_frame)
        speed_frame.pack(side=tk.LEFT, padx=20)
        ttk.Label(speed_frame, text="Speed:").pack(side=tk.LEFT)
        self.speed_var = tk.StringVar(value="1.0x")
        speed_menu = ttk.OptionMenu(
            speed_frame,
            self.speed_var,
            "1.0x",
            "0.25x", "0.5x", "0.75x", "1.0x", "1.5x", "2.0x",
            command=self.on_speed_change
        )
        speed_menu.pack(side=tk.LEFT, padx=5)
        
        # Add member variables for playback control
        self.is_playing = False
        self.playback_thread = None
        self.playback_speed = 1.0
        
        # Timestamp inputs
        time_frame = ttk.LabelFrame(main_frame, text="Timestamps", padding="10")
        time_frame.pack(fill=tk.X, pady=10)
        
        # Current timestamp display and seek
        current_frame = ttk.Frame(time_frame)
        current_frame.pack(fill=tk.X, pady=5)
        ttk.Label(current_frame, text="Current Position:").pack(side=tk.LEFT, padx=5)
        
        self.current_min_var = tk.StringVar(value="00")
        self.current_sec_var = tk.StringVar(value="00")
        self.current_ms_var = tk.StringVar(value="000")
        
        ttk.Entry(current_frame, textvariable=self.current_min_var, width=3).pack(side=tk.LEFT)
        ttk.Label(current_frame, text=":").pack(side=tk.LEFT)
        ttk.Entry(current_frame, textvariable=self.current_sec_var, width=3).pack(side=tk.LEFT)
        ttk.Label(current_frame, text=":").pack(side=tk.LEFT)
        ttk.Entry(current_frame, textvariable=self.current_ms_var, width=4).pack(side=tk.LEFT)
        
        ttk.Button(current_frame, text="Show Frame", 
                  command=self.show_current_frame).pack(side=tk.LEFT, padx=10)
        
        # Start time input
        start_frame = ttk.Frame(time_frame)
        start_frame.pack(fill=tk.X, pady=5)
        ttk.Label(start_frame, text="Start Time:").pack(side=tk.LEFT, padx=5)
        
        self.start_min_var = tk.StringVar(value="00")
        self.start_sec_var = tk.StringVar(value="00")
        self.start_ms_var = tk.StringVar(value="000")
        
        ttk.Entry(start_frame, textvariable=self.start_min_var, width=3).pack(side=tk.LEFT)
        ttk.Label(start_frame, text=":").pack(side=tk.LEFT)
        ttk.Entry(start_frame, textvariable=self.start_sec_var, width=3).pack(side=tk.LEFT)
        ttk.Label(start_frame, text=":").pack(side=tk.LEFT)
        ttk.Entry(start_frame, textvariable=self.start_ms_var, width=4).pack(side=tk.LEFT)
        
        ttk.Button(start_frame, text="Set Current", 
                  command=lambda: self.set_timestamp("start")).pack(side=tk.LEFT, padx=10)
        
        # End time input
        end_frame = ttk.Frame(time_frame)
        end_frame.pack(fill=tk.X, pady=5)
        ttk.Label(end_frame, text="End Time:  ").pack(side=tk.LEFT, padx=5)
        
        self.end_min_var = tk.StringVar(value="00")
        self.end_sec_var = tk.StringVar(value="00")
        self.end_ms_var = tk.StringVar(value="000")
        
        ttk.Entry(end_frame, textvariable=self.end_min_var, width=3).pack(side=tk.LEFT)
        ttk.Label(end_frame, text=":").pack(side=tk.LEFT)
        ttk.Entry(end_frame, textvariable=self.end_sec_var, width=3).pack(side=tk.LEFT)
        ttk.Label(end_frame, text=":").pack(side=tk.LEFT)
        ttk.Entry(end_frame, textvariable=self.end_ms_var, width=4).pack(side=tk.LEFT)
        
        ttk.Button(end_frame, text="Set Current", 
                  command=lambda: self.set_timestamp("end")).pack(side=tk.LEFT, padx=10)
        
        # Video duration display
        duration_frame = ttk.Frame(time_frame)
        duration_frame.pack(fill=tk.X, pady=5)
        ttk.Label(duration_frame, text="Video Duration:").pack(side=tk.LEFT, padx=5)
        self.duration_var = tk.StringVar(value="00:00:000")
        ttk.Label(duration_frame, textvariable=self.duration_var).pack(side=tk.LEFT, padx=5)
        
        # Navigation buttons
        nav_frame = ttk.Frame(time_frame)
        nav_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(nav_frame, text="◀◀ -10s", command=lambda: self.seek_relative(-10)).pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text="◀ -1s", command=lambda: self.seek_relative(-1)).pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text="◀ -0.1s", command=lambda: self.seek_relative(-0.1)).pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text="▶ +0.1s", command=lambda: self.seek_relative(0.1)).pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text="▶ +1s", command=lambda: self.seek_relative(1)).pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text="▶▶ +10s", command=lambda: self.seek_relative(10)).pack(side=tk.LEFT, padx=5)
        
        # Clip controls
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        # Progress bar
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(control_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=10)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Add naming controls
        name_frame = ttk.Frame(button_frame)
        name_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(name_frame, text="Base filename:").pack(side=tk.LEFT, padx=5)
        self.base_name_var = tk.StringVar(value="clip")
        ttk.Entry(name_frame, textvariable=self.base_name_var, width=15).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(name_frame, text="Start number:").pack(side=tk.LEFT, padx=5)
        self.number_var = tk.StringVar(value="1")
        ttk.Entry(name_frame, textvariable=self.number_var, width=5).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Clip Video", command=self.clip_video).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Exit", command=self.on_exit).pack(side=tk.RIGHT, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Keep reference to photo to prevent garbage collection
        self.photo = None
    
    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv"), ("All files", "*.*")]
        )
        
        if file_path:
            self.video_path = file_path
            self.file_path_var.set(os.path.basename(file_path))
            self.load_video_info()
    
    def load_video_info(self):
        try:
            self.status_var.set("Loading video information...")
            self.root.update()
            
            # Load video and get duration
            self.current_video = VideoFileClip(self.video_path)
            duration_seconds = self.current_video.duration
            
            # Store original FPS
            self.original_fps = self.current_video.fps
            
            # Store original resolution
            self.original_width, self.original_height = self.current_video.size
            
            # Update timeline slider range
            self.timeline_slider.configure(to=duration_seconds)
            
            # Convert duration to min:sec:ms format
            minutes = int(duration_seconds // 60)
            seconds = int(duration_seconds % 60)
            milliseconds = int((duration_seconds % 1) * 1000)
            
            duration_str = f"{minutes:02d}:{seconds:02d}:{milliseconds:03d}"
            self.duration_var.set(duration_str)
            
            # Set end time to video duration by default
            self.end_min_var.set(f"{minutes:02d}")
            self.end_sec_var.set(f"{seconds:02d}")
            self.end_ms_var.set(f"{milliseconds:03d}")
            
            # Set current time to 0 and show first frame
            self.current_min_var.set("00")
            self.current_sec_var.set("00")
            self.current_ms_var.set("000")
            self.show_current_frame()
            
            self.status_var.set(f"Video loaded: {os.path.basename(self.video_path)} ({self.original_fps:.2f} FPS, {self.original_width}x{self.original_height})")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load video: {str(e)}")
            self.status_var.set("Error loading video")
    
    def show_current_frame(self):
        if not self.current_video:
            messagebox.showwarning("Warning", "Please load a video first")
            return
        
        try:
            # Get current timestamp
            current_time = self.parse_timestamp(
                self.current_min_var, 
                self.current_sec_var, 
                self.current_ms_var
            )
            
            if current_time is None:
                messagebox.showerror("Error", "Invalid timestamp format")
                return
            
            if current_time > self.current_video.duration:
                messagebox.showerror("Error", "Timestamp exceeds video duration")
                return
            
            # Get frame at current time
            frame = self.current_video.get_frame(current_time)
            
            # Convert frame to PIL Image
            img = Image.fromarray(frame)
            
            # Resize image to fit canvas while maintaining aspect ratio
            canvas_width = self.frame_canvas.winfo_width()
            canvas_height = self.frame_canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:  # Ensure canvas has been drawn
                img_width, img_height = img.size
                ratio = min(canvas_width / img_width, canvas_height / img_height)
                new_size = (int(img_width * ratio), int(img_height * ratio))
                img = img.resize(new_size, Image.LANCZOS)
            
            # Convert to PhotoImage and display
            self.photo = ImageTk.PhotoImage(img)
            
            # Clear canvas and display new image
            self.frame_canvas.delete("all")
            self.frame_canvas.create_image(
                self.frame_canvas.winfo_width() // 2,
                self.frame_canvas.winfo_height() // 2,
                image=self.photo, anchor=tk.CENTER
            )
            
            self.status_var.set(f"Showing frame at {self.format_timestamp(current_time)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show frame: {str(e)}")
            self.status_var.set("Error showing frame")
    
    def format_timestamp(self, seconds):
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        return f"{minutes:02d}:{secs:02d}:{milliseconds:03d}"
    
    def seek_relative(self, offset):
        if not self.current_video:
            messagebox.showwarning("Warning", "Please load a video first")
            return
        
        # Get current timestamp
        current_time = self.parse_timestamp(
            self.current_min_var, 
            self.current_sec_var, 
            self.current_ms_var
        )
        
        if current_time is None:
            messagebox.showerror("Error", "Invalid timestamp format")
            return
        
        # Calculate new time with offset
        new_time = max(0, min(current_time + offset, self.current_video.duration))
        
        # Update timestamp variables
        minutes = int(new_time // 60)
        seconds = int(new_time % 60)
        milliseconds = int((new_time % 1) * 1000)
        
        self.current_min_var.set(f"{minutes:02d}")
        self.current_sec_var.set(f"{seconds:02d}")
        self.current_ms_var.set(f"{milliseconds:03d}")
        
        # Show frame at new position
        self.show_current_frame()
    
    def set_timestamp(self, target):
        if not self.current_video:
            messagebox.showwarning("Warning", "Please load a video first")
            return
        
        # Get current timestamp
        current_time = self.parse_timestamp(
            self.current_min_var, 
            self.current_sec_var, 
            self.current_ms_var
        )
        
        if current_time is None:
            messagebox.showerror("Error", "Invalid timestamp format")
            return
        
        # Update the appropriate timestamp variables
        minutes = int(current_time // 60)
        seconds = int(current_time % 60)
        milliseconds = int((current_time % 1) * 1000)
        
        if target == "start":
            self.start_min_var.set(f"{minutes:02d}")
            self.start_sec_var.set(f"{seconds:02d}")
            self.start_ms_var.set(f"{milliseconds:03d}")
            self.status_var.set(f"Start time set to {self.format_timestamp(current_time)}")
        else:
            self.end_min_var.set(f"{minutes:02d}")
            self.end_sec_var.set(f"{seconds:02d}")
            self.end_ms_var.set(f"{milliseconds:03d}")
            self.status_var.set(f"End time set to {self.format_timestamp(current_time)}")
    
    def parse_timestamp(self, min_var, sec_var, ms_var):
        try:
            minutes = int(min_var.get())
            seconds = int(sec_var.get())
            milliseconds = int(ms_var.get())
            
            # Convert to seconds
            return minutes * 60 + seconds + milliseconds / 1000
        except ValueError:
            return None
    
    def clip_video(self):
        if not self.video_path or not self.current_video:
            messagebox.showwarning("Warning", "Please load a video first")
            return
        
        try:
            # Get and validate the starting number
            self.current_number = int(self.number_var.get())
            if self.current_number < 0:
                raise ValueError("Number must be positive")
        except ValueError as e:
            messagebox.showerror("Error", "Invalid starting number. Please enter a positive integer.")
            return
        
        # Get start and end times
        start_time = self.parse_timestamp(self.start_min_var, self.start_sec_var, self.start_ms_var)
        end_time = self.parse_timestamp(self.end_min_var, self.end_sec_var, self.end_ms_var)
        
        if start_time is None or end_time is None:
            messagebox.showerror("Error", "Invalid timestamp format")
            return
        
        if start_time >= end_time:
            messagebox.showerror("Error", "Start time must be before end time")
            return
        
        if end_time > self.current_video.duration:
            messagebox.showerror("Error", "End time exceeds video duration")
            return
        
        # Generate output filename with current number
        base_name = self.base_name_var.get().strip()
        if not base_name:
            base_name = "clip"  # Default name if empty
        
        output_filename = f"{base_name}{self.current_number}.mp4"
        
        # Ask for output file location
        output_path = filedialog.asksaveasfilename(
            title="Save Clipped Video",
            defaultextension=".mp4",
            filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")],
            initialdir=os.path.dirname(self.video_path),
            initialfile=output_filename
        )
        
        if not output_path:
            return
        
        try:
            self.status_var.set("Clipping video...")
            self.root.update()
            
            # Create subclip
            subclip = self.current_video.subclip(start_time, end_time)
            
            # Get original video bitrate (if available)
            original_bitrate = None
            try:
                # Try to get original video bitrate from ffmpeg-python
                original_bitrate = str(int(self.current_video.reader.infos['video_bitrate'])) + 'k'
            except (AttributeError, KeyError):
                # If we can't get the original bitrate, use a high quality default
                original_bitrate = '20000k'
            
            # Keep the original clip size without resizing
            
            # Write output file with high quality settings
            subclip.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac",
                preset="veryslow",  # Highest quality compression
                bitrate=original_bitrate,
                fps=self.original_fps,  # Use original FPS
                logger=None,
                verbose=False,
                ffmpeg_params=[
                    "-crf", "17",  # Lower CRF = higher quality (range 0-51, 17-18 is visually lossless)
                    "-movflags", "+faststart",  # Optimize for web playback
                    "-profile:v", "high",  # Use high profile for better quality
                    "-level", "4.2"  # Compatibility level
                ]
            )
            
            # Increment the number for next clip
            self.current_number += 1
            self.number_var.set(str(self.current_number))
            
            # Get the resolution of the created clip from the subclip object
            clip_width, clip_height = subclip.size
            
            self.status_var.set(f"Video clipped successfully: {os.path.basename(output_path)} ({clip_width}x{clip_height})")
            messagebox.showinfo("Success", f"Video clipped successfully!\nSaved to: {output_path}\nResolution: {clip_width}x{clip_height}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clip video: {str(e)}")
            self.status_var.set("Error clipping video")
    
    def toggle_playback(self):
        if not self.current_video:
            messagebox.showwarning("Warning", "Please load a video first")
            return
        
        if self.is_playing:
            self.is_playing = False
            self.play_button.configure(text="▶ Play")
        else:
            self.is_playing = True
            self.play_button.configure(text="⏸ Pause")
            
            # Start playback in a separate thread
            if not self.playback_thread or not self.playback_thread.is_alive():
                self.playback_thread = threading.Thread(target=self.playback_loop)
                self.playback_thread.daemon = True
                self.playback_thread.start()
    
    def playback_loop(self):
        while self.is_playing and self.current_video:
            try:
                # Get current timestamp
                current_time = self.parse_timestamp(
                    self.current_min_var, 
                    self.current_sec_var, 
                    self.current_ms_var
                )
                
                if current_time is None:
                    self.is_playing = False
                    break
                
                # Calculate next frame time based on original FPS
                frame_time = 1.0 / (self.original_fps * self.playback_speed)
                next_time = current_time + frame_time
                
                # Check if we've reached the end
                if next_time >= self.current_video.duration:
                    self.is_playing = False
                    self.play_button.configure(text="▶ Play")
                    break
                
                # Update timestamp and show frame
                minutes = int(next_time // 60)
                seconds = int(next_time % 60)
                milliseconds = int((next_time % 1) * 1000)
                
                self.current_min_var.set(f"{minutes:02d}")
                self.current_sec_var.set(f"{seconds:02d}")
                self.current_ms_var.set(f"{milliseconds:03d}")
                
                # Update timeline slider
                self.timeline_var.set(next_time)
                
                # Show the frame
                self.show_current_frame()
                
                # Sleep for frame duration
                time.sleep(frame_time)
                
            except Exception as e:
                print(f"Playback error: {str(e)}")
                self.is_playing = False
                break
    
    def on_timeline_change(self, value):
        if not self.current_video:
            return
            
        try:
            # Convert slider value to float
            current_time = float(value)
            
            # Update timestamp variables
            minutes = int(current_time // 60)
            seconds = int(current_time % 60)
            milliseconds = int((current_time % 1) * 1000)
            
            self.current_min_var.set(f"{minutes:02d}")
            self.current_sec_var.set(f"{seconds:02d}")
            self.current_ms_var.set(f"{milliseconds:03d}")
            
            # Show frame at new position
            self.show_current_frame()
        except ValueError:
            pass
    
    def on_speed_change(self, *args):
        speed_text = self.speed_var.get()
        self.playback_speed = float(speed_text.replace('x', ''))
    
    def on_exit(self):
        self.is_playing = False  # Stop playback
        if self.playback_thread and self.playback_thread.is_alive():
            self.playback_thread.join(timeout=1.0)
        if self.current_video:
            self.current_video.close()
        self.temp_dir.cleanup()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoClipperApp(root)
    root.mainloop()

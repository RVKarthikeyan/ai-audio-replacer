import os
import sys
from pydub import AudioSegment, silence
from moviepy.editor import VideoFileClip, AudioFileClip

# Set the FFmpeg path (replace with the actual path where you installed FFmpeg)
ffmpeg_path = r"C:\ffmpeg\ffmpeg-2024-10-17-git-e1d1ba4cbc-full_build\bin\ffmpeg.exe"
os.environ["PATH"] += os.pathsep + os.path.dirname(ffmpeg_path)

def add_pauses_to_audio(audio_path, video_duration, output_audio_path):
    # Load the original audio
    audio = AudioSegment.from_file(audio_path)
    
    # Detect silent periods in the audio
    silent_ranges = silence.detect_silence(audio, min_silence_len=500, silence_thresh=-50)
    
    # Calculate how much silence we need to add
    audio_duration = len(audio) / 1000.0  # Audio duration in seconds
    total_silence_duration = video_duration - audio_duration  # Extra silence we need to add

    # If audio is longer than the video, no pauses are added
    if total_silence_duration <= 0:
        print("The audio is longer than the video. No changes made.")
        audio.export(output_audio_path, format="mp3")
        return
    
    # Calculate the number of pauses and the duration of each pause
    num_silences = len(silent_ranges)
    if num_silences == 0:
        print("No silence detected. Exporting original audio.")
        audio.export(output_audio_path, format="mp3")
        return
    
    silence_duration_per_pause = total_silence_duration / num_silences  # Evenly distribute silence

    # Create a new audio segment with pauses added
    extended_audio = AudioSegment.empty()
    prev_end = 0
    
    for start, end in silent_ranges:
        # Add the non-silent part
        extended_audio += audio[prev_end:start]
        
        # Add the original silent part and the new silence
        silence_segment = audio[start:end]
        extended_audio += silence_segment
        
        # Add calculated silence after this segment
        extended_audio += AudioSegment.silent(duration=silence_duration_per_pause * 1000)  # Convert to milliseconds
        
        prev_end = end
    
    # Add the final non-silent part after the last detected silence
    extended_audio += audio[prev_end:]
    
    # Export the extended audio with pauses
    extended_audio.export(output_audio_path, format="mp3")
    print(f"Extended audio with pauses saved to {output_audio_path}.")

def sync_audio_with_video(video_path, audio_path, output_video_path):
    # Load the video and extended audio files
    video_clip = VideoFileClip(video_path).without_audio()
    audio_clip = AudioFileClip(audio_path)
    
    # Set the new audio to the video
    final_clip = video_clip.set_audio(audio_clip)
    
    # Write the final video file with synced audio
    final_clip.write_videofile(output_video_path, codec="libx264", audio_codec="aac")
    print(f"Final video with synced audio saved to {output_video_path}.")

if __name__ == "__main__":
    # Retrieve the folder name from the command line arguments
    folder_name = sys.argv[1]

    # Paths to your video and audio files
    video_file_path = os.path.join(folder_name, "uploaded_video.mp4")  # Replace with your video file path
    audio_file_path = os.path.join(folder_name, "output.mp3")  # Replace with your audio file path
    extended_audio_path = os.path.join(folder_name, "extended_audio_with_silence.mp3")  # Path to save the extended audio
    output_video_path = os.path.join(folder_name, "final_video.mp4")  # Path to save the final video

    # Load the video to get its duration
    video_clip = VideoFileClip(video_file_path)
    video_duration = video_clip.duration  # Get video duration in seconds
    
    # Add pauses to the audio to match the video duration
    add_pauses_to_audio(audio_file_path, video_duration, extended_audio_path)
    
    # Sync the extended audio with the video
    sync_audio_with_video(video_file_path, extended_audio_path, output_video_path)

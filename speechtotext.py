import sys
from google.oauth2 import service_account
from google.cloud import storage, speech
import os
from dotenv import load_dotenv
from moviepy.editor import VideoFileClip

# Load environment variables from .env file
load_dotenv()

# Set up Google Cloud credentials
CREDENTIALS_FILE = 'key.json'  # Path to your service account key file
credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_FILE)

# Constants
BUCKET_NAME = os.getenv('BUCKET_NAME')  # Bucket name from .env
VIDEO_LOCAL_PATH = os.path.join(sys.argv[1], "uploaded_video.mp4")
AUDIO_LOCAL_PATH = os.path.join(sys.argv[1], "extracted_audio.mp3")
TRANSCRIPT_OUTPUT_FILE = os.path.join(sys.argv[1], "transcript.txt")

# Function to extract audio from video and save as MP3 using moviepy
def extract_audio_from_video(video_path, audio_output_path):
    video = VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile(audio_output_path, codec='mp3')  # Save as MP3
    video.close()  # Close video file
    print(f"Extracted audio to {audio_output_path}")

# Function to transcribe audio using Google Speech-to-Text
def transcribe_audio(gcs_uri):
    client = speech.SpeechClient(credentials=credentials)
    audio = speech.RecognitionAudio(uri=gcs_uri)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,
        enable_automatic_punctuation=True,
        sample_rate_hertz=44100,
        language_code='en-US'
    )

    operation = client.long_running_recognize(config=config, audio=audio)
    print("Waiting for transcription to complete...")
    response = operation.result(timeout=600)

    transcript = "\n".join([result.alternatives[0].transcript for result in response.results])
    return transcript

# Function to save transcript to a text file
def save_transcript_to_file(transcript, output_file):
    with open(output_file, 'w') as f:
        f.write(transcript)
    print(f"Transcript saved to {output_file}")

# Function to upload audio file back to GCS
def upload_blob(bucket_name, destination_blob_name, source_file_name):
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    print(f"Uploaded {source_file_name} to bucket {bucket_name} as {destination_blob_name}.")

# Main process
def main(folder_name):
    extract_audio_from_video(VIDEO_LOCAL_PATH, AUDIO_LOCAL_PATH)
    upload_blob(BUCKET_NAME, f"{folder_name}/extracted_audio.mp3", AUDIO_LOCAL_PATH)
    
    gcs_audio_uri = f"gs://{BUCKET_NAME}/{folder_name}/extracted_audio.mp3"
    transcript = transcribe_audio(gcs_audio_uri)
    save_transcript_to_file(transcript, TRANSCRIPT_OUTPUT_FILE)

if __name__ == "__main__":
    main(sys.argv[1])

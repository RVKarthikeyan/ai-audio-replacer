import streamlit as st
from google.cloud import storage
import os
import subprocess
import uuid  # For generating a unique folder name
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create key.json from environment variable
key_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
if key_json:
    with open('key.json', 'w') as f:
        f.write(key_json)

# Get environment variables
gcs_bucket_name = os.getenv('BUCKET_NAME')

# Set up Google Cloud Storage client using the key.json file
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'key.json'
gcs_client = storage.Client()
bucket = gcs_client.get_bucket(gcs_bucket_name)

# Function to upload video to GCS
def upload_to_gcs(blob_name, file_path):
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(file_path, timeout=600)
    st.success(f"Uploaded {file_path} to GCS as {blob_name}")

# Streamlit app UI
st.title("Video Processing App")

# Initialize session state
if 'processed' not in st.session_state:
    st.session_state.processed = False
    st.session_state.folder_name = None

uploaded_file = st.file_uploader("Upload a video", type=["mp4"])

if uploaded_file is not None and not st.session_state.processed:
    # Create a unique folder for this client
    st.session_state.folder_name = str(uuid.uuid4())  # Unique folder name
    os.makedirs(st.session_state.folder_name, exist_ok=True)

    # Save uploaded file to local storage
    local_video_path = os.path.join(st.session_state.folder_name, "uploaded_video.mp4")
    with open(local_video_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Upload video to GCS
    upload_to_gcs(f"{st.session_state.folder_name}/uploaded_video.mp4", local_video_path)
    
    # Process the uploaded video
    try:
        # Run the speech-to-text script
        subprocess.run(["python", "speechtotext.py", st.session_state.folder_name], check=True)

        # Run the new transcript correction script
        subprocess.run(["python", "newtranscript.py", st.session_state.folder_name], check=True)

        # Run the text-to-speech script
        subprocess.run(["python", "texttospeech.py", st.session_state.folder_name], check=True)

        # Add the new audio to the video
        subprocess.run(["python", "audioreplacer.py", st.session_state.folder_name], check=True)

        st.success("Video processing completed successfully!")

        # Prepare the final video for download
        final_video_path = os.path.join(st.session_state.folder_name, "final_video.mp4")
        with open(final_video_path, "rb") as final_video_file:
            st.download_button(
                label="Download Processed Video",
                data=final_video_file,
                file_name="processed_video.mp4",
                mime="video/mp4"
            )
        
        # Mark the processing as done
        st.session_state.processed = True

    except subprocess.CalledProcessError as e:
        st.error(f"An error occurred during processing: {e}")

# Add an option to reset the app
if st.session_state.processed:
    if st.button("Upload New Video"):
        st.session_state.processed = False

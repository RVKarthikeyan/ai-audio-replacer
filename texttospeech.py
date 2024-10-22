import sys
import os
from google.cloud import texttospeech
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set the environment variable for Google Cloud credentials
GOOGLE_CREDENTIALS_FILE = 'key.json'  # Load credentials from .env
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = GOOGLE_CREDENTIALS_FILE

# Create a Text-to-Speech client
client = texttospeech.TextToSpeechClient()

# Read the text from the transcript.txt file
TRANSCRIPT_FILE = os.path.join(sys.argv[1], "transcript.txt")
with open(TRANSCRIPT_FILE, 'r') as file:
    text_block = file.read()

# Prepare the text input for the speech synthesis
synthesis_input = texttospeech.SynthesisInput(text=text_block)

# Select the voice parameters
voice = texttospeech.VoiceSelectionParams(
    language_code="en-US",
    name='en-US-Journey-F'  # You can choose any other voice name as per your requirement
)

# Set the audio configuration
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3,
    effects_profile_id=['small-bluetooth-speaker-class-device'],
)

# Call the synthesize_speech method to convert text to speech
response = client.synthesize_speech(
    input=synthesis_input, voice=voice, audio_config=audio_config
)

# Save the audio content to an MP3 file
OUTPUT_AUDIO_FILE = os.path.join(sys.argv[1], "output.mp3")
with open(OUTPUT_AUDIO_FILE, 'wb') as output:
    output.write(response.audio_content)
    print('Audio content written to file "output.mp3"')

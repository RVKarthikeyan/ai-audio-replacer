import os
import sys
import requests
from dotenv import load_dotenv

def connect_to_azure_openai(api_key, endpoint, text):
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }
    
    # Define the data to be sent to Azure OpenAI
    data = {
        "messages": [{"role": "user", "content": f"Please correct the following transcript if there are any grammatical errors and don't give anything else except the content as output not even your words like here is the response\n\n{text}"}],
        "max_tokens": 1000  # Adjust as needed based on expected response length
    }

    # Making the POST request to the Azure OpenAI endpoint
    response = requests.post(endpoint, headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()
        # Extract and return the corrected transcript
        return result['choices'][0]['message']['content']
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

# Main process
def main(folder_name):
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('AZURE_OPENAI_KEY')
    endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
    
    # Define the path for the transcript file
    transcript_file_path = os.path.join(folder_name, "transcript.txt")
    
    # Read the original transcript
    with open(transcript_file_path, 'r') as file:
        original_transcript = file.read()

    # Correct the transcript
    corrected_transcript = connect_to_azure_openai(api_key, endpoint, original_transcript)

    if corrected_transcript:
        # Save the corrected transcript back to the file
        with open(transcript_file_path, 'w') as file:
            file.write(corrected_transcript)
        print(f"Corrected transcript saved to {transcript_file_path}")

if __name__ == "__main__":
    main(sys.argv[1])


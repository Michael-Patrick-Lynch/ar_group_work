import requests
import os

AZURE_SPEECH_KEY = os.environ.get("AZURE_SPEECH_KEY")
AZURE_REGION = os.environ.get("AZURE_REGION")
AZURE_ENDPOINT = "https://eastus.tts.speech.microsoft.com/cognitiveservices/v1"
AZURE_VOICE = "en-US-AshleyNeural"

def synthesize_speech_azure(text: str, output_file: str) -> None:
    ssml_template = f"""
    <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" 
           xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="en-US">
      <voice name="{AZURE_VOICE}">
        <mstts:express-as style="cheerful" styledegree="10">
            <prosody pitch="+1.25st" rate="+40.00%">{text}</prosody>
        </mstts:express-as>
      </voice>
    </speak>
    """

    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_SPEECH_KEY,
        "Content-Type": "application/ssml+xml",
        "X-Microsoft-OutputFormat": "riff-24khz-16bit-mono-pcm",
    }
    
    response = requests.post(
        AZURE_ENDPOINT,
        headers=headers,
        data=ssml_template.encode("utf-8")
    )

    if response.status_code == 200:
        with open(output_file, "wb") as f:
            f.write(response.content)
        print(f"Audio saved to {output_file}")
    else:
        print("Error code:", response.status_code)
        print("Error message:", response.text)
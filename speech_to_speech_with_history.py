import os
import time
import speech_recognition as sr
from groq import Groq
from gtts import gTTS
from playsound import playsound

# Set API Key
os.environ["GROQ_API_KEY"] = "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"

# Initialize Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Conversation history storage
conversation_history = []

# Rate Limits (Free Tier)
NLP_RPM, NLP_TPM = 30, 6000  # NLP model limits
ASR_RPM, ASR_ASH = 20, 7200  # ASR model limits


def handle_rate_limit(response):
    """Handles 429 errors with exponential backoff"""
    if response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", 5))  # Default to 5 sec
        print(f"Rate limit exceeded. Retrying after {retry_after} seconds...")
        time.sleep(retry_after)
        return True
    return False


def request_with_retry(api_call, max_retries=5):
    """Generic function to handle API calls with retry on failure"""
    retries = 0
    while retries < max_retries:
        try:
            response = api_call()
            return response  # Return response if successful

        except Exception as e:
            if "429" in str(e):  # Detect rate limit error
                wait_time = 2 ** retries  # Exponential backoff
                print(f"Rate limit reached. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                retries += 1
            else:
                print(f"API error: {e}")
                break
    return None  # Return None if all retries fail


def summarize_history():
    """Summarizes conversation history when it gets too long."""
    global conversation_history
    if len(conversation_history) < 5:  # Only summarize when there are 5+ exchanges
        return

    print("Summarizing conversation history...")

    def api_call():
        return client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": "Summarize this conversation history briefly:"},
                {"role": "assistant", "content": "\n".join(conversation_history)}
            ],
            temperature=0.7,
            max_tokens=512
        )

    summary = request_with_retry(api_call)
    if summary:
        conversation_history = [summary.choices[0].message.content]  # Keep only summary
        print("Conversation history summarized.")


def text_to_text(input_text):
    """Processes text using the NLP model with conversation history."""
    global conversation_history

    # Add input to history
    conversation_history.append(f"User: {input_text}")

    # Summarize if history is too long
    summarize_history()

    def api_call():
        return client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": "You are a friendly and fluent communicator in Hindi"},
                {"role": "assistant", "content": "\n".join(conversation_history)}
            ],
            temperature=1,
            max_tokens=512,
            top_p=1,
            stream=True
        )

    completion = request_with_retry(api_call)
    if not completion:
        return ""

    full_response = []
    for chunk in completion:
        chunk_text = chunk.choices[0].delta.content or ""
        full_response.append(chunk_text)
        print(chunk_text, end="")

    complete_text = "".join(full_response)

    # Add response to history
    conversation_history.append(f"Assistant: {complete_text}")

    return complete_text


# Function to capture and transcribe audio from microphone
def transcribe_from_microphone():
    """Captures speech from microphone and transcribes it."""
    recognizer = sr.Recognizer()
    print("Listening... Speak into your microphone.")

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio_data = recognizer.listen(source)
            print("Processing audio...")

            # Convert audio to byte data for API
            audio_bytes = audio_data.get_wav_data()

            def api_call():
                return client.audio.transcriptions.create(
                    file=("microphone_input.wav", audio_bytes),  # Simulated file upload
                    model="whisper-large-v3",
                    prompt="You are a genius in communication with humans",
                    response_format="json",
                    language="hi"
                )

            transcription = request_with_retry(api_call)
            if transcription:
                print("Transcription:", transcription.text)
                return transcription.text
            else:
                print("Failed to transcribe.")
                return ""

        except sr.UnknownValueError:
            print("Sorry, I couldn't understand what you said.")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")


def text_to_speech(text):
    """Converts text to speech and plays it."""
    import pygame

    def play_audio(file):
        pygame.mixer.init()
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():  # Wait until the audio finishes playing
            pygame.time.Clock().tick(10)
    print("Generating speech...")
    try:
        tts = gTTS(text=text, lang="hi")
        tts.save("output.mp3")
        play_audio("output.mp3")
        #playsound("output.mp3")
    except Exception as e:
        print(f"TTS Error: {e}")


# Start the ASR-NLP-TTS pipeline
if __name__ == "__main__":
    while True:
        transcription_text = transcribe_from_microphone()

        if transcription_text.lower() in ["exit", "quit", "बंद करो"]:  # Supports both English & Hindi exit commands
            print("Exiting conversation. Goodbye!")
            break

        response = text_to_text(transcription_text)
        text_to_speech(response)



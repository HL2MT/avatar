import os
import time
import speech_recognition as sr
from groq import Groq
from gtts import gTTS
from playsound import playsound
import tempfile
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

# Set API Key
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY") #"Your groq api"  #https://console.groq.com/docs/quickstart

# Initialize Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Initialize conversation history
conversation_history = []


def summarize_history():
    """Summarizes conversation history every time before sending to the model."""
    global conversation_history

    def api_call():
        return client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": "Summarize this conversation briefly:".join(conversation_history)},
            ],
            temperature=0.7,
            max_tokens=300
        )

    summary = api_call()
    return summary.choices[0].message.content if summary else ""


def text_to_text(input_text):
    """Processes text using the NLP model with summarized history."""
    global conversation_history
    conversation_history.append(f"User: {input_text}")
    summarized_history = summarize_history()

    def api_call():
        return client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": f"You are a friendly assistant fluent in Hindi,this is our previous conversation{summarized_history}"},
            ],
            temperature=1,
            max_tokens=512,
            top_p=1
        )

    completion = api_call()
    response = completion.choices[0].message.content if completion else ""
    conversation_history.append(f"Assistant: {response}")
    return response


def transcribe_from_microphone():
    """Captures speech and transcribes it."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        st.write("Listening... Speak now!")
        try:
            audio_data = recognizer.listen(source)
            text = recognizer.recognize_google(audio_data, language="hi")
            return text
        except sr.UnknownValueError:
            return "Sorry, I couldn't understand."
        except sr.RequestError:
            return "Speech recognition service error."


import os


def text_to_speech(text):
    """Converts text to speech and plays it."""
    file_path = "response.mp3"

    if os.path.exists(file_path):  # Ensure file is not locked
        try:
            os.remove(file_path)  # Delete previous file
        except PermissionError:
            print("File is in use, retrying...")
            pygame.mixer.quit()  # Force close pygame
            os.remove(file_path)

    tts = gTTS(text=text, lang="hi")
    tts.save(file_path)

    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

# Sidebar for conversation summary
st.sidebar.title("Conversation Summary")
summary_text = summarize_history()
st.sidebar.write(summary_text if summary_text else "No summary available yet.")


# Streamlit UI
st.title("Hindi AI Chatbot")
user_input = ""

if st.button("🎤 Speak"):
    user_input = transcribe_from_microphone()
    st.write("You: ", user_input)

if user_input:
    bot_response = text_to_text(user_input)
    st.write("Bot: ", bot_response)
    text_to_speech(bot_response)

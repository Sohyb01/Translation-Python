from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from io import BytesIO
import speech_recognition as sr
from translate import Translator
import threading
from gtts import gTTS
import pygame
import os
import time
from flask_socketio import SocketIO


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*", "allow_headers": "*", "methods": "*"}})
# socketio = SocketIO(app, cors_allowed_origins="*")  # Set CORS to allow connections from any domain


running = False  # Start with the program not running
listen_thread = None  # Placeholder for the listen thread
source = None
text = None # Placeholder for the text

# Target language and From Language variables
tl = "en" #Translation (Text)
fl = "ar" #Translation (Text)
speech_fl = "ar-EG" # Speech Recognition

def toggle_running():
    global running, listen_thread, source
    running = not running  # Toggle the running state

    if running:
        print("Program started...")
        if listen_thread is None or not listen_thread.is_alive():
            listen_thread = threading.Thread(target=listen_and_translate, daemon=False)
            # listen_thread.daemon = True
            listen_thread.start()
    else:
        print("Program stopped...")
        # Do not assign None to source here, as it is managed by the background listener
        # if source is not None:
        #     source = None

# Initialize the pygame mixer
pygame.mixer.init()

def run_audio(audio):
    try:
        # Initialize the mixer if it's not already initialized
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        # Load the MP3 file
        sound = pygame.mixer.Sound(audio)

        # Play the audio
        sound.play()

        # Wait for the audio to finish playing
        pygame.time.wait(int(sound.get_length() * 1000))
    except Exception as e:
        print(f"An error occurred while playing audio: {e}")

def write_text():
    global text
    print(f"Recognized text: {text}")
    with open('output-transcription.txt', 'a', encoding='utf-8') as file:
        file.write(text + "\n")

def recognize_audio_thread(recognizer, audio_data):
    global text
    recognizer = sr.Recognizer()
    translator = Translator(to_lang=tl, from_lang=fl)

    try:
        text = recognizer.recognize_google(audio_data, language=speech_fl)


        # Check if text is not None before translating
        if text is not None:
            # socketio.emit('new_transcription', {'text': text})  # Emit the transcribed text
            # Add a Thread here
            threading.Thread(target=write_text).start()

            # # Translate the recognized text
            # translation = translator.translate(text)
            # with open('output-transcription.txt', 'a', encoding='utf-8') as file:
            #     file.write(translation + "\n")
            # print("Translated text: ", translation)
            # ###
            # tts = gTTS(translation, lang=tl, tld='com', slow=False)
            # # Use BytesIO instead of saving to a file
            # mp3_fp = BytesIO()
            # tts.write_to_fp(mp3_fp)
            # mp3_fp.seek(0)

            # # Play the audio using a separate thread
            # play_thread = threading.Thread(target=run_audio, args=(mp3_fp,))
            # play_thread.start()
        else:
            print("Speech not recognized.")
    except:
        pass

def listen_and_translate():
    global running, source
    recognizer = sr.Recognizer()

    # Open the microphone for listening only once
    if source is None:
        source = sr.Microphone()
        with source as s:
            recognizer.adjust_for_ambient_noise(s)


    print("Listening...")
    # Start listening in the background (non-blocking)
    stop_listening = recognizer.listen_in_background(source, recognize_audio_thread) # Specify Max Listening Duration (seconds) here

    try:
        while running:
            time.sleep(0.1)  # Sleep to prevent this loop from using 100% CPU
    finally:
        # If you want to stop the background listening, call stop_listening
        stop_listening(wait_for_stop=False)

def stop_listening():
    global running
    running = False  # Set the flag to False to stop the loop
    pygame.mixer.stop()  # Stop any currently playing sounds


# ... (include your existing functions here)
@app.route('/')
def index():
    return render_template('index.html')  # The HTML file to render


@app.route('/toggle', methods=['POST'], strict_slashes=False)
def toggle():
    # print(request.headers)  # Add this to log headers
    global running
    content = request.json
    
    try:
        if content and 'command' in content:
            if content['command'] == 'start' and not running:
                toggle_running()
                return jsonify({"message": "Program started"}), 200
            elif content['command'] == 'stop' and running:
                toggle_running()
                return jsonify({"message": "Program stopped"}), 200
            else:
                return jsonify({"message": "Invalid command or program already in desired state"}), 400
        else:
            return jsonify({"message": "No command provided"}), 400
    except Exception as e:
        print(f"An error occurred in the toggle route: {e}")
        return jsonify({"error": "An error occurred", "details": str(e)}), 500

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"message": "Internal Server Error", "error": str(error)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"message": "Not Found", "error": str(error)}), 404

if __name__ == "__main__":
    app.run(debug=True, threaded=True)

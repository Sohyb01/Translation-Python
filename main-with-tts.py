from io import BytesIO
import speech_recognition as sr
from translate import Translator
import threading
from gtts import gTTS
import pygame
import os
import time

# Initialize global flag
running = True

# Target language and From Language variables
tl = "en" #Translation (Text)
fl = "ar" #Translation (Text)
speech_fl = "ar-EG"

# Initialize the pygame mixer
pygame.mixer.init()

def run_audio(audio):
    try:
        # Load the MP3 file
        sound = pygame.mixer.Sound(audio)

        # Play the audio
        sound.play()

        # Wait for the audio to finish playing
        pygame.time.wait(int(sound.get_length() * 1000))
    except Exception as e:
        print(f"An error occurred while playing audio: {e}")

def recognize_audio_thread(audio_data):
    recognizer = sr.Recognizer()
    translator = Translator(to_lang=tl, from_lang=fl)

    try:
        text = recognizer.recognize_google(audio_data, language=speech_fl)

        # Check if text is not None before translating
        if text is not None:
            print(f"Recognized text: {text}")
            with open('output-transcription.txt', 'a', encoding='utf-8') as file:
                file.write(text + "\n")

            # Translate the recognized text
            translation = translator.translate(text)
            with open('output-transcription.txt', 'a', encoding='utf-8') as file:
                file.write(translation + "\n")
            print("Translated text: ", translation)
            ###
            tts = gTTS(translation, lang=tl, tld='com', slow=False)
            # Use BytesIO instead of saving to a file
            mp3_fp = BytesIO()
            tts.write_to_fp(mp3_fp)
            mp3_fp.seek(0)

            # Play the audio using a separate thread
            play_thread = threading.Thread(target=run_audio, args=(mp3_fp,))
            play_thread.start()
        else:
            print("Speech not recognized.")

    except:
        pass

def listen_and_translate():
    global running  # Use the global flag
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening...")
        try:
            while running:  # Check the global flag in the loop
                audio_data = recognizer.listen(source)

                # Stop the loop if the global flag is false
                if not running:
                    break

                # Create a new thread to recognize and translate audio
                audio_thread = threading.Thread(target=recognize_audio_thread, args=(audio_data,))
                audio_thread.start()
        except KeyboardInterrupt:
            print("Stopped listening.")
        finally:
            pygame.mixer.quit()  # Ensure that mixer is properly quit when stopping

def stop_listening():
    global running
    running = False  # Set the flag to False to stop the loop
    pygame.mixer.stop()  # Stop any currently playing sounds

# ... (the rest of your code for setting up threads)


# At the end of the program, you no longer need to join since the thread will exit the loop
# listen_thread.join()  # This is not needed anymore

if __name__ == "__main__":
    # Create and start the main thread for listening and translation
    listen_thread = threading.Thread(target=listen_and_translate)
    listen_thread.daemon = True  # Set the thread as a daemon
    listen_thread.start()

    print("Press CTRL+C to stop...")
    try:
        # The main thread waits here for the secondary thread to complete
        while running:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("CTRL+C pressed. Stopping...")
        stop_listening()  # Use the stop_listening function to handle cleanup
    finally:
        # Wait a moment for the daemon thread to realize it should stop
        time.sleep(0.5)
        print("Program exited cleanly")

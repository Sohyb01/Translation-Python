def listen_and_translate():
    global running, source  # Use the global flag and source
    recognizer = sr.Recognizer()
    # Ensure the source is initialized
    if source is None:
        source = sr.Microphone()
    # Open the microphone for listening
    with source as s:
        recognizer.adjust_for_ambient_noise(s)
        print("Listening...")
        while running:  # Check the global flag in the loop
            try:
                audio_data = recognizer.listen(s)
                # Stop the loop if the global flag is false
                if not running:
                    break
                # Create a new thread to recognize and translate audio
                audio_thread = threading.Thread(target=recognize_audio_thread, args=(audio_data,))
                audio_thread.start()
            except KeyboardInterrupt:
                print("Stopped listening.")
            except Exception as e:
                print(f"An error occurred: {e}")

from audio_handler import AudioHandler
from recognizer_vosk import SpeechRecognizer
import threading
import wave


class Controller:
    """
    Connects GUI, AudioHandler, and SpeechRecognizer.
    Handles live-streaming from mic and files.
    """

    def __init__(self):
        self.audio = AudioHandler()
        self.recognizer = SpeechRecognizer("vosk-model-small-ru-0.22")
        self.state = "idle"
        self.text = ""

    def start_recording(self):
        if self.state == "recording":
            return
        self.state = "recording"
        self.text = ""
        self.audio.start_recording()

        def update_text(new_text):
            self.text = new_text

        def on_done():
            self.state = "idle"
            print("Recording processed. Status idle.")

        threading.Thread(target=self.recognizer.recognize_stream,
                         args=(self.audio.audio_queue, update_text, on_done),
                         daemon=True).start()

    def pause_recording(self):
        if self.state == "recording":
            self.audio.pause()
            self.state = "paused"

    def resume_recording(self):
        if self.state == "paused":
            self.audio.resume()
            self.state = "recording"

    def stop_recording(self):
        if self.state in ["recording", "paused"]:
            self.audio.stop()
            self.state = "processing"

    def recognize_file(self, path: str):
        self.state = "processing"
        temp_wav = self.audio.load_audio_file(path)
        wf = wave.open(temp_wav, "rb")

        def update_text(new_text):
            self.text = new_text

        def on_done():
            self.state = "idle"
            print("File processed. Status idle.")

        # recognition thread
        threading.Thread(target=self.recognizer.recognize_stream,
                         args=(self.audio.audio_queue, update_text, on_done),
                         daemon=True).start()

        # feed WAV file in chunks
        def stream_file():
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                self.audio.audio_queue.put(data)
            self.audio.audio_queue.put("STOP")
            wf.close()

        threading.Thread(target=stream_file, daemon=True).start()

    def get_text(self):
        return self.text

    def clear_text(self):
        self.text = ""

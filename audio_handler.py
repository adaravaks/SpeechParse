import queue
import threading
import sounddevice as sd
import wave
from pydub import AudioSegment


class AudioHandler:
    """
    Handles microphone recording and reading/converting audio files.
    """

    def __init__(self, samplerate=16000):
        self.samplerate = samplerate
        self.channels = 1
        self.running = False
        self.paused = False
        self.thread = None
        self.audio_queue = queue.Queue()
        self.temp_file = "temp_record.wav"

    def _callback(self, indata, frames, time, status):
        if status:
            print(status)
        if not self.paused:
            self.audio_queue.put(bytes(indata))

    def start_recording(self):
        if self.running:
            return

        self.running = True
        self.paused = False

        def record_thread():
            with sd.RawInputStream(samplerate=self.samplerate, blocksize=8000,
                                   dtype='int16', channels=self.channels,
                                   callback=self._callback):
                with wave.open(self.temp_file, "wb") as wf:
                    wf.setnchannels(self.channels)
                    wf.setsampwidth(2)
                    wf.setframerate(self.samplerate)

                    print("Recording started...")
                    while self.running:
                        try:
                            data = self.audio_queue.get(timeout=0.1)
                            if data == "STOP":
                                break
                            wf.writeframes(data)
                        except queue.Empty:
                            continue
                print("Recording stopped. File saved:", self.temp_file)

        self.thread = threading.Thread(target=record_thread, daemon=True)
        self.thread.start()

    def pause(self):
        self.paused = True
        print("Recording paused.")

    def resume(self):
        self.paused = False
        print("Recording resumed.")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        self.audio_queue.put("STOP")  # signal recognizer to finish

    def load_audio_file(self, path: str) -> str:
        print(f"Loading file: {path}")
        sound = AudioSegment.from_file(path)
        sound = sound.set_frame_rate(self.samplerate).set_channels(1).set_sample_width(2)
        temp_path = "temp_converted.wav"
        sound.export(temp_path, format="wav")
        print("File converted:", temp_path)
        return temp_path

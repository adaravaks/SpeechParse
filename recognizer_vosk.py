import json
import wave
from vosk import Model, KaldiRecognizer


class SpeechRecognizer:
    """
    Uses Vosk ru model to recognize speech from WAV files or streaming audio.
    """

    def __init__(self, model_path="vosk-model-small-ru-0.22"):
        print("Loading Vosk model...")
        self.model = Model(model_path)
        print("Model loaded.")

    def recognize_stream(self, audio_queue, callback=None, done=None):
        """
        Recognizes audio chunks in real-time from audio_queue.
        callback(text) is called with each new partial text.
        done() is called when recognition finishes.
        """
        rec = KaldiRecognizer(self.model, 16000)
        text_buffer = []

        while True:
            data = audio_queue.get()
            if data == "STOP":
                break

            if rec.AcceptWaveform(data):
                res = json.loads(rec.Result())
                if res.get("text"):
                    text_buffer.append(res["text"])
                    if callback:
                        callback(" ".join(text_buffer))
            else:
                # partial result
                res = json.loads(rec.PartialResult())
                if callback:
                    callback(" ".join(text_buffer) + " " + res.get("partial", ""))

        # final result
        final_res = json.loads(rec.FinalResult())
        if final_res.get("text"):
            text_buffer.append(final_res["text"])
            if callback:
                callback(" ".join(text_buffer))

        if done:
            done()  # signal that recognition finished

    # ---------------- File recognition (single pass) ----------------
    def recognize_from_file(self, wav_path: str) -> str:
        wf = wave.open(wav_path, "rb")
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
            raise ValueError("File must be WAV (mono, 16-bit, 16kHz).")

        rec = KaldiRecognizer(self.model, wf.getframerate())
        result_text = []

        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                res = json.loads(rec.Result())
                if res.get("text"):
                    result_text.append(res["text"])

        final = json.loads(rec.FinalResult())
        if final.get("text"):
            result_text.append(final["text"])

        wf.close()
        return " ".join(result_text)
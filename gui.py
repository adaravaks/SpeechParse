import tkinter as tk
from tkinter import filedialog, messagebox
from controller import Controller
import pyperclip


class SpeechParser:
    def __init__(self, root):
        self.root = root
        self.root.title("SpeechParse")
        self.root.geometry("700x500")

        self.controller = Controller()

        self.text_box = tk.Text(root, wrap=tk.WORD, height=20)
        self.text_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.status_label = tk.Label(root, text="Status: Idle")
        self.status_label.pack(pady=5)

        # buttons frame
        frame = tk.Frame(root)
        frame.pack(pady=5)

        tk.Button(frame, text="🎙 Record", width=12, command=self.start_recording).grid(row=0, column=0, padx=5)
        tk.Button(frame, text="⏸ Pause", width=12, command=self.pause_recording).grid(row=0, column=1, padx=5)
        tk.Button(frame, text="▶ Resume", width=12, command=self.resume_recording).grid(row=0, column=2, padx=5)
        tk.Button(frame, text="⏹ Stop", width=12, command=self.stop_recording).grid(row=0, column=3, padx=5)

        tk.Button(frame, text="📁 Open File", width=12, command=self.open_file).grid(row=1, column=0, padx=5, pady=5)
        tk.Button(frame, text="📋 Copy Text", width=12, command=self.copy_text).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(frame, text="💾 Save Text", width=12, command=self.save_text).grid(row=1, column=2, padx=5, pady=5)
        tk.Button(frame, text="🧹 Clear Text", width=12, command=self.clear_text).grid(row=1, column=3, padx=5, pady=5)

        self.update_gui()

    def start_recording(self):
        self.controller.start_recording()
        self.status_label.config(text="Status: Recording...")

    def pause_recording(self):
        self.controller.pause_recording()
        self.status_label.config(text="Status: Paused")

    def resume_recording(self):
        self.controller.resume_recording()
        self.status_label.config(text="Status: Recording...")

    def stop_recording(self):
        self.controller.stop_recording()
        self.status_label.config(text="Status: Processing...")

    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav *.mp3 *.ogg")])
        if path:
            self.controller.recognize_file(path)
            self.status_label.config(text="Status: Processing file...")

    def copy_text(self):
        text = self.controller.get_text()
        if text:
            pyperclip.copy(text)
            messagebox.showinfo("Copied", "Text copied to clipboard!")

    def save_text(self):
        text = self.controller.get_text()
        if text:
            path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                filetypes=[("Text files", "*.txt")])
            if path:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(text)
                messagebox.showinfo("Saved", f"Text saved to {path}")

    def clear_text(self):
        self.controller.clear_text()
        self.text_box.delete("1.0", tk.END)
        self.status_label.config(text="Status: Idle")

    def update_gui(self):
        # update text field with recognized text
        current_text = self.controller.get_text()
        self.text_box.delete("1.0", tk.END)
        self.text_box.insert(tk.END, current_text)

        # update status based on controller state
        state = self.controller.state
        if state == "recording":
            self.status_label.config(text="Status: Recording...")
        elif state == "paused":
            self.status_label.config(text="Status: Paused")
        elif state == "processing":
            self.status_label.config(text="Status: Processing...")
        else:self.status_label.config(text="Status: Idle")

        # schedule next update
        self.root.after(500, self.update_gui)

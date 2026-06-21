import os
import threading
import platform
import subprocess
import customtkinter as ctk
from PIL import Image

class SpeechFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.is_listening = False

        # Logo/Avatar
        avatar_image = self.controller.get_avatar_image((80, 80))
        if avatar_image:
            self.avatar_label = ctk.CTkLabel(self, image=avatar_image, text="")
            self.avatar_label.pack(pady=(15, 5))

        # Title/Welcome Banner
        self.welcome_label = ctk.CTkLabel(
            self, 
            text="ECHO Dashboard", 
            font=("Arial", 18, "bold")
        )
        self.welcome_label.pack(pady=5)

        # Transcribed Text Box (New speech)
        self.transcription_title = ctk.CTkLabel(self, text="Latest Transcription", font=("Arial", 12, "bold"), text_color="gray")
        self.transcription_title.pack(anchor="w", padx=40, pady=(10, 2))
        
        self.speech_text_box = ctk.CTkTextbox(self, height=70, width=420, font=("Arial", 13))
        self.speech_text_box.pack(pady=(0, 10))
        self.speech_text_box.configure(state="disabled")

        # History Text Box
        self.history_title = ctk.CTkLabel(self, text="Speech History (Select text to analyze/play)", font=("Arial", 12, "bold"), text_color="gray")
        self.history_title.pack(anchor="w", padx=40, pady=(10, 2))
        
        self.old_text_box = ctk.CTkTextbox(self, height=130, width=420, font=("Arial", 13))
        self.old_text_box.pack(pady=(0, 10))
        self.old_text_box.configure(state="disabled")

        # Microphone Selection Dropdown
        self.mic_selection_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.mic_selection_frame.pack(pady=5)
        
        self.mic_label = ctk.CTkLabel(self.mic_selection_frame, text="Input:", font=("Arial", 12, "bold"))
        self.mic_label.grid(row=0, column=0, padx=5)
        
        self.mic_dropdown = ctk.CTkOptionMenu(
            self.mic_selection_frame,
            values=["Default Microphone"],
            width=260
        )
        self.mic_dropdown.grid(row=0, column=1, padx=5)

        # Status & Sentiment Indicators
        self.status_label = ctk.CTkLabel(
            self, 
            text="Waiting for Speech...", 
            font=("Arial", 13, "italic"),
            text_color=("black", "lightgray")
        )
        self.status_label.pack(pady=5)

        self.sentiment_label = ctk.CTkLabel(
            self, 
            text="Sentiment Analysis Result", 
            font=("Arial", 14, "bold"),
            text_color="gray"
        )
        self.sentiment_label.pack(pady=5)

        # Main Controls Frame (Icon Grid)
        self.icon_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.icon_frame.pack(pady=15)

        # Load Icons via controller's helper
        mic_icon = self.controller.get_icon("./assets/microphone.png", (24, 24))
        play_icon = self.controller.get_icon("./assets/play_icon.png", (24, 24))
        sentiment_icon = self.controller.get_icon("./assets/sentiment_icon.png", (24, 24))

        self.microphone_button = ctk.CTkButton(
            self.icon_frame,
            image=mic_icon,
            text="Start Listening",
            command=self.toggle_microphone_button,
            width=135,
            height=40,
            compound="left",
            font=("Arial", 12, "bold")
        )
        self.microphone_button.grid(row=0, column=0, padx=5)

        self.play_button = ctk.CTkButton(
            self.icon_frame,
            image=play_icon,
            text="Play Selection",
            command=self.play_highlighted_text,
            width=135,
            height=40,
            compound="left",
            font=("Arial", 12, "bold")
        )
        self.play_button.grid(row=0, column=1, padx=5)

        self.sentiment_button = ctk.CTkButton(
            self.icon_frame,
            image=sentiment_icon,
            text="Analyze",
            command=self.analyze_selected_text,
            width=100,
            height=40,
            compound="left",
            font=("Arial", 12, "bold")
        )
        self.sentiment_button.grid(row=0, column=2, padx=5)

        # Utility Buttons Frame (Report operations & Settings)
        self.utility_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.utility_frame.pack(pady=10)

        # Appearance Toggle
        self.appearance_switch = ctk.CTkSwitch(
            self.utility_frame,
            text="Dark Mode",
            command=self.toggle_appearance_switch,
            onvalue=1,
            offvalue=0
        )
        self.appearance_switch.grid(row=0, column=0, padx=20, pady=5)
        if ctk.get_appearance_mode() == "dark":
            self.appearance_switch.select()

        # Report Action Buttons
        self.download_report_button = ctk.CTkButton(
            self,
            text="Download PDF Report",
            command=self.download_sentiment_report,
            width=220,
            height=35,
            font=("Arial", 13, "bold")
        )
        self.download_report_button.pack(pady=5)

        self.open_file_button = ctk.CTkButton(
            self,
            text="Open Latest Report",
            command=self.open_downloaded_report,
            width=220,
            height=35,
            font=("Arial", 13, "bold"),
            fg_color="transparent",
            border_width=2,
            text_color=("black", "white")
        )
        self.open_file_button.pack(pady=5)

        # Logout
        self.logout_button = ctk.CTkButton(
            self,
            text="Logout",
            command=self.logout,
            width=220,
            height=35,
            fg_color="transparent",
            text_color="red",
            hover_color=("#ffebee", "#3e2723"),
            font=("Arial", 13, "bold")
        )
        self.logout_button.pack(pady=(15, 10))

    def on_show(self):
        """Called when this frame becomes active."""
        if self.controller.current_user:
            self.welcome_label.configure(text=f"Welcome, {self.controller.current_user}!")
        self.load_user_history()
        self.populate_microphones()

    def populate_microphones(self):
        mics = self.controller.speech_module.get_microphone_list()
        values = ["Default Microphone"]
        for idx, name in enumerate(mics):
            values.append(f"{idx}: {name}")
        self.mic_dropdown.configure(values=values)
        if len(values) > 1:
            # Default to MacBook Pro Microphone if available
            default_selection = "Default Microphone"
            for val in values:
                if "MacBook Pro Microphone" in val:
                    default_selection = val
                    break
            self.mic_dropdown.set(default_selection)
        else:
            self.mic_dropdown.set("Default Microphone")

    def load_user_history(self):
        user_id = self.controller.current_user_id
        if user_id is None:
            return
        
        # Load in a background thread to prevent UI freezing
        def run():
            history = self.controller.db_module.load_user_history_from_db(user_id)
            self.after(0, lambda: self.display_history(history))

        threading.Thread(target=run, daemon=True).start()

    def display_history(self, history):
        self.old_text_box.configure(state="normal")
        self.old_text_box.delete("0.0", "end")
        for text, timestamp in history:
            self.old_text_box.insert("0.0", f"{timestamp}: {text}\n")
        self.old_text_box.configure(state="disabled")

    def toggle_appearance_switch(self):
        new_mode = "light" if self.appearance_switch.get() == 0 else "dark"
        ctk.set_appearance_mode(new_mode)

    def toggle_microphone_button(self):
        if self.is_listening:
            self.is_listening = False
            self.microphone_button.configure(text="Start Listening")
            self.status_label.configure(text="Speech recognition stopped.")
        else:
            self.is_listening = True
            self.microphone_button.configure(text="Stop Listening")
            self.status_label.configure(text="Initialising microphone...")
            
            # Start recognition in background thread
            threading.Thread(target=self.run_speech_recognition, daemon=True).start()

    def run_speech_recognition(self):
        def update_status(text):
            self.after(0, lambda: self.status_label.configure(text=text))

        # Get selected device index
        selected_mic = self.mic_dropdown.get()
        device_index = None
        if selected_mic != "Default Microphone" and ":" in selected_mic:
            try:
                device_index = int(selected_mic.split(":")[0])
            except Exception:
                pass

        # Perform the actual listening block
        text, err = self.controller.speech_module.recognize_speech(
            device_index=device_index,
            on_status_change=update_status
        )
        
        # Callback to update the GUI with the result
        self.after(0, lambda: self.handle_recognition_result(text, err))

    def handle_recognition_result(self, text, err):
        self.is_listening = False
        self.microphone_button.configure(text="Start Listening")

        if err:
            self.status_label.configure(text=err)
        elif text:
            # Display recognized text in the text boxes
            self.speech_text_box.configure(state="normal")
            self.speech_text_box.delete("0.0", "end")
            self.speech_text_box.insert("0.0", text + "\n")
            self.speech_text_box.configure(state="disabled")
            
            # Save the recognized text to database
            self.controller.db_module.save_spoken_text_to_db(self.controller.current_user_id, text)
            
            # Refresh history
            self.load_user_history()
            self.status_label.configure(text="Speech saved successfully!")
        else:
            self.status_label.configure(text="No speech recognized.")

        # Reset status label after delay
        self.status_label.after(5000, lambda: self.status_label.configure(text="Waiting for Speech..."))

    def get_selected_text(self):
        new_selected_text = ""
        old_selected_text = ""
        
        try:
            if self.speech_text_box.tag_ranges("sel"):
                new_selected_text = self.speech_text_box.selection_get()
        except Exception:
            pass

        try:
            if self.old_text_box.tag_ranges("sel"):
                old_selected_text = self.old_text_box.selection_get()
        except Exception:
            pass

        return f"{new_selected_text}\n{old_selected_text}".strip()

    def analyze_selected_text(self):
        selected_text = self.get_selected_text()
        if not selected_text:
            self.sentiment_label.configure(text="No text selected for analysis.", text_color="gray")
            return

        self.status_label.configure(text="Analyzing text...")
        scores = self.controller.sentiment_module.analyze_text(selected_text)
        compound_score = scores['compound']

        if compound_score > 0.05:
            self.sentiment_label.configure(text="Sentiment: Positive 😊", text_color="green")
        elif compound_score < -0.05:
            self.sentiment_label.configure(text="Sentiment: Negative 😟", text_color="red")
        else:
            self.sentiment_label.configure(text="Sentiment: Neutral 😐", text_color="blue")

        self.status_label.after(3000, lambda: self.status_label.configure(text="Waiting for Speech..."))

    def play_highlighted_text(self):
        selected_text = self.get_selected_text()
        if not selected_text:
            self.status_label.configure(text="No text selected to play.")
            return

        self.status_label.configure(text="Playing audio...")
        
        def run():
            try:
                self.controller.audio_module.play_text_to_speech(selected_text)
                self.after(0, lambda: self.status_label.configure(text="Audio playback finished."))
            except Exception as e:
                self.after(0, lambda err=e: self.status_label.configure(text=f"Playback error: {err}"))
            
            self.status_label.after(4000, lambda: self.status_label.configure(text="Waiting for Speech..."))

        threading.Thread(target=run, daemon=True).start()

    def download_sentiment_report(self):
        if not self.controller.current_user or not self.controller.current_user_id:
            self.status_label.configure(text="Please log in first.")
            return

        selected_text = self.get_selected_text()
        if not selected_text:
            self.status_label.configure(text="Please select text from history or transcription.")
            return

        self.status_label.configure(text="Generating the report...")
        self.update_idletasks()

        def run():
            try:
                report_path = self.controller.sentiment_module.generate_report(
                    selected_text=selected_text,
                    username=self.controller.current_user,
                    user_id=self.controller.current_user_id,
                    save_to_db_callback=self.controller.db_module.save_report_to_db
                )
                if report_path:
                    self.after(0, lambda: self.status_label.configure(
                        text=f"Report saved at: {os.path.basename(report_path)}"
                    ))
                else:
                    self.after(0, lambda: self.status_label.configure(text="Failed to generate report."))
            except Exception as e:
                self.after(0, lambda err=e: self.status_label.configure(text=f"Report error: {err}"))
            
            self.status_label.after(5000, lambda: self.status_label.configure(text="Waiting for Speech..."))

        threading.Thread(target=run, daemon=True).start()

    def open_downloaded_report(self):
        if not self.controller.current_user_id:
            self.status_label.configure(text="Please log in first.")
            return

        self.status_label.configure(text="Opening latest report...")
        
        def run():
            report_path = self.controller.db_module.get_latest_report_path(self.controller.current_user_id)
            if not report_path or not os.path.exists(report_path):
                    self.after(0, lambda: self.status_label.configure(text="No local report file found."))
                    return

            try:
                if platform.system() == "Windows":
                    os.startfile(report_path)
                elif platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", report_path])
                else:
                    subprocess.run(["xdg-open", report_path])
                
                self.after(0, lambda: self.status_label.configure(
                    text=f"Opened report: {os.path.basename(report_path)}"
                ))
            except Exception as e:
                self.after(0, lambda err=e: self.status_label.configure(text=f"Error opening report: {err}"))
            
            self.status_label.after(4000, lambda: self.status_label.configure(text="Waiting for Speech..."))

        threading.Thread(target=run, daemon=True).start()

    def logout(self):
        self.controller.set_logged_in_user(None, None)
        self.speech_text_box.configure(state="normal")
        self.speech_text_box.delete("0.0", "end")
        self.speech_text_box.configure(state="disabled")
        self.old_text_box.configure(state="normal")
        self.old_text_box.delete("0.0", "end")
        self.old_text_box.configure(state="disabled")
        self.status_label.configure(text="Waiting for Speech...")
        self.sentiment_label.configure(text="Sentiment Analysis Result")
        self.controller.show_frame("MainFrame")

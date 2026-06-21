import os
import customtkinter as ctk
from PIL import Image, ImageDraw

from echo.database import db as db_module
from echo.utils.speech import SpeechRecognizer
from echo.utils.sentiment import SentimentAnalyzer
from echo.utils import audio as audio_module

from echo.gui.frames.main_frame import MainFrame
from echo.gui.frames.login_frame import LoginFrame
from echo.gui.frames.register_frame import RegisterFrame
from echo.gui.frames.speech_frame import SpeechFrame

class EchoApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Configuration
        self.title("ECHO - Voice Insight")
        self.geometry("600x750")
        
        # Load theme settings
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        # Application State
        self.current_user_id = None
        self.current_user = None

        # Modules
        self.db_module = db_module
        self.speech_module = SpeechRecognizer()
        self.sentiment_module = SentimentAnalyzer()
        self.audio_module = audio_module

        # Container for all frames
        self.container = ctk.CTkFrame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Dictionary to store frames
        self.frames = {}

        # Pre-load frames
        for FrameClass in (MainFrame, LoginFrame, RegisterFrame, SpeechFrame):
            page_name = FrameClass.__name__
            frame = FrameClass(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Show the landing frame
        self.show_frame("MainFrame")

    def show_frame(self, page_name):
        """Displays the specified frame on the top of the stack."""
        frame = self.frames[page_name]
        frame.tkraise()
        
        # Call lifecycle hook if it exists
        if hasattr(frame, "on_show"):
            frame.on_show()

    def set_logged_in_user(self, username, user_id):
        self.current_user = username
        self.current_user_id = user_id

    def get_avatar_image(self, size):
        """Generates a rounded avatar image and wraps it in a ctk.CTkImage."""
        path = "./assets/avatar.png"
        if not os.path.exists(path):
            return None
        
        try:
            image = Image.open(path).resize(size, Image.Resampling.LANCZOS)
            mask = Image.new("L", size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, size[0], size[1]), fill=255)
            rounded_image = Image.new("RGBA", size)
            rounded_image.paste(image, (0, 0), mask)
            
            # Return ctk.CTkImage for scaling
            return ctk.CTkImage(light_image=rounded_image, dark_image=rounded_image, size=size)
        except Exception as e:
            print(f"Error loading avatar: {e}")
            return None

    def get_icon(self, path, size):
        """Loads an icon file and wraps it in a ctk.CTkImage."""
        if not os.path.exists(path):
            return None
        try:
            image = Image.open(path)
            return ctk.CTkImage(light_image=image, dark_image=image, size=size)
        except Exception as e:
            print(f"Error loading icon {path}: {e}")
            return None

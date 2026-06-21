#pip install SpeechRecognition nltk gTTS customtkinter pillow fpdf matplotlib pygame playsound
#or type pip install -r requirement.txt

from echo.database import initialize_database
from echo.gui import EchoApp

def main():
    initialize_database()
    app = EchoApp()
    app.mainloop()

if __name__ == "__main__":
    main()
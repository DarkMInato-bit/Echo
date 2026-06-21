# ECHO — Voice Insight

A professional Python desktop application that combines speech recognition with sentiment analysis to provide voice-to-text conversion, emotional tone analysis, and PDF report generation — with a clean, modern dark-mode UI built using CustomTkinter.

---

## Key Features

### Authentication System
- User registration and login with secure **bcrypt** password hashing
- Contact information encrypted with **Fernet (AES-128)** symmetric encryption
- Automatic fallback to local encrypted text storage when MySQL is unavailable

### Speech Recognition
- Real-time microphone input with **ambient noise adjustment**
- Powered by **Google Web Speech API** via the `SpeechRecognition` library
- Selectable **microphone input device** (dropdown lists all detected audio inputs)
- Background thread processing — GUI stays responsive while listening

### Sentiment Analysis
- Sentence-level scoring using **NLTK VADER** (`SentimentIntensityAnalyzer`)
- Compound score range: `-1.0` (very negative) → `+1.0` (very positive)
- Visual emoji + color-coded feedback in the UI

### PDF Report Generation
- Generates detailed PDF reports with sentence-level sentiment breakdowns
- Includes an embedded **matplotlib bar chart** of overall sentiment distribution
- Reports saved to per-user folders (`users/<username>/`)
- Report metadata tracked in database or local fallback storage

### Text-to-Speech
- Converts selected text to audio using **gTTS** (Google Text-to-Speech)
- Native audio playback with **playsound**
- macOS: uses Apple Cocoa APIs (`AppKit.NSSound` via `pyobjc`)
- Windows: uses the native Windows Multimedia API

### Smart Database + Offline Fallback
- **Primary**: MySQL database (`voice_insight` schema)
- **Fallback**: Fully encrypted local text files when MySQL is not available
  - `local_users.txt` — user credentials (hashed passwords + encrypted contact)
  - `local_history.txt` — encrypted speech history
  - `local_reports.txt` — report tracking data


---

## Architecture

```
withdatabase/
├── main.py                    # Entry point — initializes DB and starts EchoApp
├── requirements.txt           # All dependencies
├── .gitignore                 # Git exclusions (keys, local data, venv, etc.)
├── secret.key                 # Fernet encryption key (auto-generated, NEVER commit)
│
├── echo/                      # Main application package
│   ├── __init__.py
│   │
│   ├── database/              # Database layer
│   │   ├── __init__.py        # Exports: initialize_database, login_user, etc.
│   │   └── db.py              # MySQL operations + local text file fallback logic
│   │
│   ├── gui/                   # GUI layer
│   │   ├── __init__.py        # Exports: EchoApp
│   │   ├── app.py             # EchoApp (ctk.CTk) — frame manager, asset loader
│   │   └── frames/            # Individual screen components
│   │       ├── __init__.py
│   │       ├── main_frame.py  # Landing screen (Login / Register buttons)
│   │       ├── login_frame.py # Login form
│   │       ├── register_frame.py  # Registration form
│   │       └── speech_frame.py    # Main dashboard (speech, history, analysis)
│   │
│   └── utils/                 # Utility modules
│       ├── __init__.py
│       ├── speech.py          # SpeechRecognizer — wraps sr.Recognizer
│       ├── sentiment.py       # SentimentAnalyzer — VADER + chart + PDF
│       └── audio.py           # play_text_to_speech — gTTS + playsound
│
├── assets/                    # UI icons and avatar
│   ├── avatar.png
│   ├── microphone.png
│   ├── play_icon.png
│   └── sentiment_icon.png
│
└── users/                     # Generated PDF reports (per-user folders)
    └── <username>/
        └── *.pdf
```

---

## Setup Instructions

### Prerequisites

**macOS** (run once before installing requirements):
```bash
brew install portaudio
brew install python-tk@3.10
```

**Windows**: No additional prerequisites.

---

### 1. Create and activate a Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

> **Windows users**: Open `requirements.txt` and comment out the two `pyobjc` lines before installing — they are macOS-only.

### 3. Download NLTK Data (run once)
```bash
python3 -c "import nltk; nltk.download('vader_lexicon')"
```

### 4. Database Setup (Optional)

ECHO works **without** a database using its local file fallback. If you want MySQL:

- Ensure MySQL server is running
- Create a database named `voice_insight`:
  ```sql
  CREATE DATABASE voice_insight;
  ```
- Update credentials in [`echo/database/db.py`](echo/database/db.py):
  ```python
  conn = mysql.connector.connect(
      host="127.0.0.1",
      user="root",
      password="your_password_here",
      database="voice_insight"
  )
  ```
- Tables are created automatically on first launch.

### 5. Grant Microphone Permissions (macOS)

macOS requires explicit microphone permission for the Terminal app:

1. Go to **System Settings → Privacy & Security → Microphone**
2. Enable the toggle for **Terminal** (or the IDE you are using)

If the permission prompt never appeared, reset it and re-run the app:
```bash
tccutil reset Microphone
```

### 6. Run the Application

```bash
python3 main.py
```

---

## Usage Guide

| Action | How |
|---|---|
| **Register** | Click Register on the home screen, fill in all fields |
| **Login** | Click Login, enter your credentials |
| **Select Microphone** | Use the **Input:** dropdown to select your active audio device |
| **Start Listening** | Click **Start Listening** and speak clearly |
| **Analyze Sentiment** | Select text in history or transcription box → click **Analyze** |
| **Play Text** | Select text → click **Play Selection** |
| **Download Report** | Select text → click **Download PDF Report** |
| **Open Report** | Click **Open Latest Report** |
| **Toggle Theme** | Use the **Dark Mode** switch |
| **Logout** | Click **Logout** |

---

## Security Notes

| File | Risk | Action |
|---|---|---|
| `secret.key` | Decrypts all stored data | **Never share or commit** |
| `local_users.txt` | Contains hashed passwords | Excluded via `.gitignore` |
| `local_history.txt` | Encrypted speech history | Excluded via `.gitignore` |
| `.venv/` | Virtual environment | Excluded via `.gitignore` |

- Passwords are **never stored in plain text** — only bcrypt hashes
- Speech history and contact info are encrypted with **Fernet (AES-128)**
- If `secret.key` is deleted, all previously encrypted data becomes unrecoverable

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `No module named '_tkinter'` | `brew install python-tk@3.10` |
| `No module named 'AppKit'` | `pip install pyobjc-framework-Cocoa` |
| Microphone not detected | Grant microphone permission to Terminal in System Settings |
| Listening times out | Speak immediately after "Listening..." appears |
| `vader_lexicon` not found | `python3 -c "import nltk; nltk.download('vader_lexicon')"` |
| Database not connecting | App will fall back to local text storage automatically |
| `secret.key` missing | A new key is generated automatically — old encrypted data will be unreadable |

---
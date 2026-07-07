# Orin — Personal Voice Assistant

A Jarvis-style desktop voice assistant built with Python, featuring a pixel art animated GUI, online/offline speech recognition fallback, local AI via Ollama, and a Discord-inspired mic mute system.

---

## Features

- **Animated GUI** — Pixel art face with blinking eyes, easing mouth animation synced to speech, and sound wave bars while listening
- **Voice Input** — Google Speech Recognition online, Vosk offline fallback with automatic switching
- **Voice Output** — Microsoft Edge TTS (Ryan Neural, British) online, pyttsx3 offline fallback
- **Local AI** — Ollama (llama3.2:1b) for open-ended conversation, with auto-relaunch if not running
- **Commands** — Open apps, shutdown/restart, web search, YouTube, Google, time, jokes, screenshot
- **Mic Mute** — Ctrl+M toggle with mid-listen detection, Discord-style animated icon
- **Floating Window** — Minimize to a small overlay with sound bars and mic status, restore with F11
- **Subtitles** — Real-time user and assistant text with fade-in animation

---

## Requirements

- Python 3.11 (recommended — newer versions may have PyAudio compatibility issues)
- [Ollama](https://ollama.com/) installed and running locally with `llama3.2:1b` pulled

### Install dependencies

```bash
pip install -r requirements.txt
```

### Download Vosk model (for offline speech recognition)

```bash
pip install sprc
sprc download vosk
```

> If `sprc` isn't recognized, run it via the full Python Scripts path:
> `C:\Users\YourName\AppData\Local\Programs\Python\Python311\Scripts\sprc.exe download vosk`

---

## Configuration

Before running, edit the `apps` dictionary in `Voice.py` to match your own application paths:

```python
apps = {
    "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "vs code": "C:\\Path\\To\\Your\\VSCode\\Code.exe",
    # Add more apps as needed
}
```

Also update the screenshot save path to your preferred folder:

```python
pyautogui.screenshot(f"C:\\Users\\YourName\\Pictures\\Screenshots\\{filename}.png")
```

---

## How to Run

```bash
py -3.11 Voice.py
```

Or open in VS Code with Python 3.11 set as the interpreter and press Run.
You can also find an executable file in the project
(Note that python 3.11 is required either way)

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+M | Toggle mic mute |
| F11 | Restore from floating window |

---

## Tech Stack

| Purpose | Library |
|---------|---------|
| Voice input (online) | `speech_recognition` + Google API |
| Voice input (offline) | `vosk` |
| Voice output (online) | `edge-tts` (Ryan Neural) |
| Voice output (offline) | `pyttsx3` |
| Local AI | `ollama` (llama3.2:1b) |
| GUI | `tkinter` |
| Audio playback | `pygame` |
| Screenshot | `pyautogui` |
| App launching | `subprocess` |

---

## Project Structure

```
VoiceAssistant/
│
├── Voice.py           # Main script
├── requirements.txt   # Python dependencies
├── icons/             # Mic icon assets (optional)
└── README.md
```

---

## Known Limitations

- App paths in the `apps` dictionary are machine-specific and must be configured manually
- Edge TTS requires an internet connection — pyttsx3 is used as fallback when offline
- Ollama must be installed separately and the `llama3.2:1b` model pulled before first run
- Wake word detection not yet implemented — assistant listens continuously

---

## Roadmap

- [ ] Wake word detection ("Hey Orin")
- [ ] Conversation memory for Ollama
- [ ] Volume control
- [ ] Config file for app paths and settings

---

Built by Ali as a learning project and portfolio piece.

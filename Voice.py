import speech_recognition as sr
import pyttsx3
import datetime
import os
import wikipedia
import webbrowser
import pyjokes
import pyaudio
import subprocess
import ollama
import ctypes
import sys
import time
import pyautogui
import pygame
import edge_tts
import asyncio
import tkinter as tk
import threading
import math
import random

# Variables
window = tk.Tk()
window.geometry("800x600")
window.title('Orin')
canvas = tk.Canvas(window, background='black')
canvas.pack(fill=tk.BOTH, expand=True)
float_canvas = None
float_win = None

pygame.mixer.init()
is_speaking = False
is_listening = False
is_muted = False
is_floating = False
num_bars = 7
bar_width = 4
bar_spacing = 18
bar_center_x = 380
bar_center_y = 450
bar_base_y = 480
bar_heights = [0] * num_bars
max_bar_height = 40

eye = (
    # ===========left eye===========
    canvas.create_rectangle(320, 240, 340, 260, fill='white', outline='white'),
    canvas.create_rectangle(300, 260, 320, 280, fill='white', outline='white'),
    canvas.create_rectangle(340, 260, 360, 280, fill='white', outline='white'),
    # ===========right eye==========
    canvas.create_rectangle(420, 240, 440, 260, fill='white', outline='white'),
    canvas.create_rectangle(400, 260, 420, 280, fill='white', outline='white'),
    canvas.create_rectangle(440, 260, 460, 280, fill='white', outline='white'),
) 


# =========Mouth=========
mouth = canvas.create_oval(350, 335, 450, 345, fill='', outline='white', width=3)
mouth_closed_height = 10
mouth_open_height = 40
mouth_width = 100
mouth_center_x = 380
mouth_center_y = 340
current_height = mouth_closed_height
user_text = canvas.create_text(380, 400, text='', fill='white', font=('Bahnschrift', 18), width=700, anchor="center")
assistant_box = tk.Text(canvas, width=60, height=6,bg='black', fg='white', font=('Bahnschrift', 16), wrap='word', relief='flat', borderwidth=0, )
assistant_box.tag_configure('center', justify='center')
assistant_box_window = canvas.create_window(380, 150, window=assistant_box)
float_mic_text = None
fade_value = 0
assistant_box.bind('<Key>', lambda e: 'break')
# ====================================================
# DISCORD MIC ICON SYSTEM (Canvas Driven)
# ====================================================
MIC_CENTER_X = 380
MIC_CENTER_Y = 530

# Colors matching Discord Desktop UI
COLOR_ACTIVE_BG = "#2b2d31"
COLOR_MUTED_BG = "#2b2d31"
COLOR_MIC_BODY = "#dbdee1"
COLOR_SLASH = "#f23f43"

mic_bg = canvas.create_oval(MIC_CENTER_X-25, MIC_CENTER_Y-25, MIC_CENTER_X+25, MIC_CENTER_Y+25, fill=COLOR_ACTIVE_BG, outline="")
mic_capsule = canvas.create_rectangle(MIC_CENTER_X-6, MIC_CENTER_Y-12, MIC_CENTER_X+6, MIC_CENTER_Y+4, fill=COLOR_MIC_BODY, outline="", width=0)
mic_u_shape = canvas.create_line(MIC_CENTER_X-10, MIC_CENTER_Y-2, MIC_CENTER_X-10, MIC_CENTER_Y+4, MIC_CENTER_X+10, MIC_CENTER_Y+4, MIC_CENTER_X+10, MIC_CENTER_Y-2, smooth=True, fill=COLOR_MIC_BODY, width=3, capstyle="round")
mic_stand = canvas.create_line(MIC_CENTER_X, MIC_CENTER_Y+4, MIC_CENTER_X, MIC_CENTER_Y+12, fill=COLOR_MIC_BODY, width=3)
mic_base = canvas.create_line(MIC_CENTER_X-7, MIC_CENTER_Y+12, MIC_CENTER_X+7, MIC_CENTER_Y+12, fill=COLOR_MIC_BODY, width=3, capstyle="round")

# Red Slash Line Overlay
discord_slash = canvas.create_line(MIC_CENTER_X-14, MIC_CENTER_Y-14, MIC_CENTER_X-14, MIC_CENTER_Y-14, fill=COLOR_SLASH, width=3.5, capstyle="round")

# Animation Configuration Matrices
shake_offsets = [10, -10, 8, -8, 5, -5, 3, -3, 1, -1, 0]
scale_steps = [1.15, 1.10, 0.90, 0.95, 1.0]  # Squash and Stretch matrix mimicking Discord UI Pop
shake_index = 0
animating = False

def render_mic_frame(offset_x, scale):
    """Dynamically redraws and updates all mic components with scale and shake factor."""
    cx = MIC_CENTER_X + offset_x
    cy = MIC_CENTER_Y
    
    # 1. Background Circle Scaling
    r_bg = 25 * scale
    canvas.coords(mic_bg, cx - r_bg, cy - r_bg, cx + r_bg, cy + r_bg)
    
    # 2. Main Inner Microphone Components Scaling
    canvas.coords(mic_capsule, cx - (6 * scale), cy - (12 * scale), cx + (6 * scale), cy + (4 * scale))
    canvas.coords(mic_u_shape, cx - (10 * scale), cy - (2 * scale), cx - (10 * scale), cy + (4 * scale), cx + (10 * scale), cy + (4 * scale), cx + (10 * scale), cy - (2 * scale))
    canvas.coords(mic_stand, cx, cy + (4 * scale), cx, cy + (12 * scale))
    canvas.coords(mic_base, cx - (7 * scale), cy + (12 * scale), cx + (7 * scale), cy + (12 * scale))
    
    # Update Background color context matching Discord
    canvas.itemconfig(mic_bg, fill=COLOR_MUTED_BG if is_muted else COLOR_ACTIVE_BG)

def blink():
    for e in eye:
        canvas.itemconfigure(e, state='hidden')
    canvas.after(150, open_eyes)

def open_eyes():
    for e in eye:
        canvas.itemconfigure(e, state='normal')
    rand_time = random.randint(3000, 6000)
    canvas.after(rand_time, blink)

def minimize_to_float(event):
    global is_floating
    global float_canvas
    global float_win
    global is_muted
    global float_mic_text
    if event.widget == window and not is_floating:
        is_floating = True
        window.withdraw()
        float_win = tk.Toplevel()
        float_win.geometry('200x200+1670+20')
        float_win.overrideredirect(True)
        float_canvas = tk.Canvas(float_win, background='black', highlightcolor='black')
        float_canvas.pack(fill='both', expand=True)
        animate_float_bars()
        print('minimized')
        float_mic_text = float_canvas.create_text(100, 73, text='', font=('Bahnschrift', 18), fill='white', anchor='center')
        float_win.bind('<Control-m>', toggle_mute)
        float_win.bind('<F11>', restore_window)
        
window.bind('<Unmap>', minimize_to_float)

def animate_float_bars():
    global is_listening
    global bar_heights
    global max_bar_height
    global float_canvas
    float_canvas.delete('bars')
    for num in range(num_bars):
        if is_listening == False:
            target_height = 0
        else:
            target_height = (
                math.sin(time.time() * 3 + num * 1.5) * 0.5 + 
                math.sin(time.time() * 7 + num * 0.8) * 0.3 +
                math.sin(time.time() * 13 + num * 2.1) * 0.2
            ) + 1 * (max_bar_height / 2)
            center_weight = 1 - abs(num - num_bars // 2) / (num_bars // 2)
            target_height *= center_weight
        bar_heights[num] += (target_height - bar_heights[num]) * 0.4
        float_canvas.create_rectangle((46 + bar_spacing * num), (114 - bar_heights[num]), (46 + bar_spacing * num) + (bar_width), (114 + bar_heights[num]), tags='bars', fill='white', outline='white')
    float_canvas.after(50, animate_float_bars)

def restore_window(event=None):
    global is_floating, float_canvas, float_mic_text
    float_win.destroy()
    window.deiconify()
    is_floating = False
    float_canvas = None
    float_mic_text = None


def toggle_mute(event=None):
    global is_muted, shake_index, animating, float_mic_text, float_canvas
    if animating:
        return
    if float_mic_text is not None:
        float_canvas.itemconfig(float_mic_text, text='Listening...' if is_muted else 'Mic muted')
    is_muted = not is_muted
    animating = True
    shake_index = 0
    animate_discord_effects()

def animate_discord_effects():
    global shake_index, animating
    
    total_steps = len(shake_offsets)
    step_fraction = (shake_index + 1) / total_steps
    
    current_offset = shake_offsets[shake_index]
    current_scale = scale_steps[min(shake_index, len(scale_steps)-1)]
    
    render_mic_frame(current_offset, current_scale)
    
    start_x, start_y = (MIC_CENTER_X - 14), (MIC_CENTER_Y - 14)
    target_x, target_y = (MIC_CENTER_X + 14), (MIC_CENTER_Y + 14)
    
    if not is_muted:
        # Reverse animations
        step_fraction = 1.0 - step_fraction
        
    current_x2 = start_x + (target_x - start_x) * step_fraction
    current_y2 = start_y + (target_y - start_y) * step_fraction
    
    if is_muted or step_fraction > 0.01:
        canvas.coords(discord_slash, start_x + current_offset, start_y, current_x2 + current_offset, current_y2)
    else:
        # Completely hide when inactive unmuted state is confirmed
        canvas.coords(discord_slash, start_x, start_y, start_x, start_y)
        
    shake_index += 1
    
    if shake_index < total_steps:
        canvas.after(20, animate_discord_effects)
    else:
        animating = False
        render_mic_frame(0, 1.0) 
        if is_muted:
            canvas.coords(discord_slash, start_x, start_y, target_x, target_y)
        else:
            canvas.coords(discord_slash, start_x, start_y, start_x, start_y)

window.bind('<Control-m>', toggle_mute)

def speak(text):
    global is_speaking
    print(f"Assistant: {text}")
    window.after(0, lambda: assistant_box.insert('end', '\n' + text + '\n', 'center'))
    window.after(0,lambda: assistant_box.see('end'))
    fade_value = 0
    try:
        
        is_speaking = True
        asyncio.run(_speak_edge(text))
    except:
        is_speaking = True
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    is_speaking = False

def wish_user():
    hour = int(datetime.datetime.now().hour)
    if hour < 12:
        speak("Good Morning Sir")
    elif hour < 18:
        speak("Good Afternoon Sir")
    else:
        speak("Good Evening Sir")
    speak("How can I help you today?")

recognizer = sr.Recognizer()
internet_success = True

def take_command():
    global canvas
    global user_text
    global internet_success
    global is_listening
    global is_muted
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        while True:
            if is_muted:
                is_listening = False
                window.after(0, lambda: canvas.itemconfig(user_text, text=''))
                return None
            else:
                is_listening = True
                window.after(0, lambda: canvas.itemconfig(user_text, text='Listening...'))
            try:
                audio = recognizer.listen(source, timeout=2, phrase_time_limit=5)
                if is_muted:
                    is_listening = False
                    window.after(0, lambda: canvas.itemconfig(user_text, text='Mic muted'))
                    return None
                break
            except sr.WaitTimeoutError:
                continue

        try:
            words = recognizer.recognize_google(audio)
            print(words)
            internet_success = True
            window.after(0, lambda: canvas.itemconfig(user_text, text=words))
            is_listening = False
            return (words.lower())
        except sr.UnknownValueError:
            speak("Sorry, I couldn't understand that. Please try again.")
            is_listening = False

        
        except sr.RequestError:
            if internet_success == True:
                speak("Internet seems to be down, switching to offline mode...")
                internet_success = False
            try:
                words = recognizer.recognize_vosk(audio)
                print(words)
                is_listening = False

                return (words.lower())
            except sr.UnknownValueError:
                speak("Sorry, I couldn't understand that. Please try again.")
                is_listening = False


async def _speak_edge(text):
    communicate = edge_tts.Communicate(text, "en-GB-RyanNeural")
    await communicate.save("temp_audio.mp3")
    pygame.mixer.music.load("temp_audio.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.music.unload()
    os.remove("temp_audio.mp3")

apps = {
    "life is strange before the storm": "D:\\Life is strange\\Life is Strange Before the Storm\\Life is Strange Before the Storm\\Life is Strange - Before the Storm.exe",
    "life is strange 1": "D:\\Life is strange\\Life is Strange Complete Season\\Binaries\\Win32\\LifeIsStrange.exe",
    "cuphead": "F:\\Games\\Cuphead\\Cuphead.exe",
    "fifa 23": [
        "F:\\Games\\FIFA 23\\FIFA 23\\Launcher.exe",
        "C:\\Users\\User\\Desktop\\x360ce.exe"
    ],
    "valorant": [
        "F:\\Games\\Valorant\\Riot Games\\Riot Client\\RiotClientServices.exe",
        "C:\\Users\\User\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Overwolf\\Valorant Tracker.lnk"
    ],
    "epic games": "F:\\Epic Games\\Epic Games\\Launcher\\Portal\\Binaries\\Win64\\EpicGamesLauncher.exe",
    "vs code": "F:\\VSC\\Microsoft VS Code\\Code.exe",
    "visual studio code": "F:\\VSC\\Microsoft VS Code\\Code.exe",
    "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "google chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "firefox": "C:\\Program Files\\Mozilla Firefox\\firefox.exe",
    "steam": "C:\\Program Files (x86)\\Steam\\steam.exe",
    "ollama": "C:\\Users\\User\\AppData\\Local\\Programs\\Ollama\\ollama app.exe"
}


def run_assistant():
    
    
    wish_user()
    while True:
        query = take_command()
        if query == None:
            continue
        elif 'youtube' in query:
            speak("Anything Else?")
            speak("Opening YouTube..")
            webbrowser.open("https://www.youtube.com/")
        elif 'google' in query:
            speak("Opening Google...")
            webbrowser.open("https://www.google.com/")
        elif 'open' in query or 'run' in query:
            app_name = ' '.join(query.split()[1:])
            if app_name in apps:
                if isinstance(apps[app_name], list):
                    for path in apps[app_name]:
                        try:
                            subprocess.Popen(path)
                        except OSError:
                            ctypes.windll.shell32.ShellExecuteW(None, "runas", app_name, " ".join(sys.argv), None, 1)
                        speak(f"Opening {app_name}")
                else:
                    try:
                        subprocess.Popen(apps[app_name])
                    except OSError:
                        ctypes.windll.shell32.ShellExecuteW(None, "runas", apps[app_name], None, os.path.dirname(apps[app_name]), 1)
                    speak(f"Opening {app_name}")
            else:
                try:
                    os.system("start " + app_name)
                    speak(f"Opening {app_name}")
                except FileNotFoundError:
                    speak(f"Sorry, I couldn't find {app_name}, Please confirm it's not deleted.")
                
        
        
        elif 'time' in query:
            strTime = datetime.datetime.now().strftime("%H:%M")
            speak(f"The current time is {strTime}")
        elif 'joke' in query:
            joke = pyjokes.get_joke()
            speak(joke)
        elif 'exit' in query or 'bye' in query or 'quit' in query or 'close' in query:
            speak("Goodbye! Have a nice day!")
            window.after(0, window.destroy)
            break
        elif 'shutdown' in query or 'power off' in query or 'turn off' in query or 'shut down' in query:
            os.system("shutdown /s /t 0")
            speak("Shutdown in progress...")
        elif 'restart' in query or 'reboot' in query:
            os.system("shutdown /r /t 0")
            speak("restart in progress...")
        elif 'search for' in query or 'how does' in query:
            search_words = ' '.join(query.split()[2:])
            webbrowser.open(f"https://www.google.com/search?q={search_words}")
        elif 'screen shot' in query or 'screenshot' in query:
            filename = str(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
            pyautogui.screenshot(f"C:\\Users\\User\\Pictures\\Screenshots\\{filename}.png")
            speak('Screenshot was saved in Screenshots folder.')
            print(f"C:\\Users\\User\\Pictures\\Screenshots\\{filename}.png")
        else:
            try:
                response = ollama.chat(
                model="llama3.2:1b",
                messages=[
                    {"role": "system", "content": "You are a helpful voice assistant called Orin. Keep your responses short and direct since they will be spoken out loud."},
                    {"role": "user", "content": query}
                    ]
                )
                speak(response['message']['content'])
            except ConnectionError:
                subprocess.Popen("ollama")
                time.sleep(3)
                try:
                    response = ollama.chat(
                    model="llama3.2:1b",
                    messages=[
                        {"role": "system", "content": "You are a helpful voice assistant called Orin. Keep your responses short and direct since they will be spoken out loud. Keep responses under 2-3 sentences maximum. Be concise."},
                        {"role": "user", "content": query}
                        ]
                    )
                    speak(response['message']['content'])
                except ConnectionError:
                    speak("Sorry, Ollama is taking too long to start. Please try again in a moment.")

def animate_mouth():
    global current_height
    global is_speaking
    if is_speaking and pygame.mixer.music.get_busy():
        current_height = mouth_closed_height + (math.sin(time.time() * 10) + 1) * (mouth_open_height / 2)
    else:
        current_height += (mouth_closed_height - current_height) * 0.4
    canvas.coords(mouth, (mouth_center_x - mouth_width // 2), (mouth_center_y - current_height // 2), (mouth_center_x + mouth_width // 2), (mouth_center_y + current_height // 2))
    canvas.after(50, animate_mouth)


def animate_bars():
    global is_listening
    global bar_heights
    global max_bar_height
    canvas.delete('bars')
    for num in range(num_bars):
        if is_listening == False:
            target_height = 0
        else:
            target_height = (
                math.sin(time.time() * 3 + num * 1.5) * 0.5 + 
                math.sin(time.time() * 7 + num * 0.8) * 0.3 +
                math.sin(time.time() * 13 + num * 2.1) * 0.2
            ) + 1 * (max_bar_height / 2)
            center_weight = 1 - abs(num - num_bars // 2) / (num_bars // 2)
            target_height *= center_weight
        bar_heights[num] += (target_height - bar_heights[num]) * 0.4
        canvas.create_rectangle((326 + bar_spacing * num), (bar_center_y - bar_heights[num]), (326 + bar_spacing * num) + (bar_width), (bar_center_y + bar_heights[num]), tags='bars', fill='white', outline='white')
    canvas.after(50, animate_bars)
canvas.pack(fill='both', expand=True)


t = threading.Thread(target=run_assistant)
t.start()

blink()
animate_mouth()
animate_bars()
window.mainloop()


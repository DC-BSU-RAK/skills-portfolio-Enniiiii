from tkinter import *
from tkinter import messagebox# Used for error handling
import random
import pyttsx3
import threading
import customtkinter as ctk
from pygame import mixer
from PIL import ImageTk, Image
import os

mixer.init()
buttonSound = mixer.Sound("AlexaTellMeAJoke/Menu.mp3")
jokeSound= mixer.Sound("AlexaTellMeAJoke/Joke.mp3")
def playBackgroundMusic():
    music_file = "AlexaTellMeAJoke/Music.mp3"  # Replace with your music file path
    
    if os.path.exists(music_file):
        mixer.music.load(music_file)
        # Play the music in an infinite loop (-1 means loop forever)
        mixer.music.play(-1) 
    else:
        print(f"Error: {music_file} not found.")

music_thread = threading.Thread(target=playBackgroundMusic)
music_thread.daemon = True # Allows the thread to close when the main program exits
music_thread.start()

def find_female_voice_id():
    try:
        tmp_engine = pyttsx3.init()
        voices = tmp_engine.getProperty("voices")
        female_id = None
        for v in voices:
            name_lower = (v.name or "").lower()
            id_lower = (v.id or "").lower()
            # try multiple heuristics
            if "female" in name_lower or "female" in id_lower or "woman" in name_lower:
                female_id = v.id
                break
        tmp_engine.stop()
        return female_id
    except Exception:
        return None

female_voice_id = find_female_voice_id()


def loadJokes(filename):
    jokes = []
    try:
        with open(filename, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if "?" in line:
                    joke, punchline = line.split("?", 1)
                    jokes.append((joke.strip() + "?", punchline.strip()))
        return jokes
    except FileNotFoundError:
        messagebox.showerror("Error", f"File '{filename}' not found!")
        root.destroy()
        return []
jokes = loadJokes("AlexaTellMeAJoke/randomJokes.txt")

def showFrame(frame):
    frame.tkraise()
    buttonSound.play()

def tts_worker(text, female_voice_id_local):
    try:
        engine_local = pyttsx3.init()
        if female_voice_id_local:
            try:
                engine_local.setProperty("voice", female_voice_id_local)
            except Exception:
                pass  # ignore if setting voice fails
        engine_local.say(text)
        engine_local.runAndWait()
        engine_local.stop()
    except Exception as e:
        print("TTS error:", e)

# --- Called when "Listen" pressed ---
def speakText():
    text = joke_label.cget("text").strip()
    if text == "":
        text = "There is no text to read yet. Please show a joke first."
    # start a thread so GUI doesn't freeze and so each call uses its own engine lifecycle
    t = threading.Thread(target=tts_worker, args=(text, female_voice_id), daemon=True)
    t.start()

#I had to utilize AI to for text to speech to work for both the joke and the punchline and the AI came up with this, since i had trouble utlizing the pyttx3 engine
#So all of the functions utlizing text to speech is AI




def showJoke():
    buttonSound.play()
    global current_joke
    if not jokes:
        joke_label.config(text="No jokes available!")
        return
    current_joke = random.choice(jokes)
    joke_label.config(text=current_joke[0])

def showPunchline():
    buttonSound.play()
    jokeSound.play()
    if current_joke:
        joke_label.config(text=current_joke[1])
    else:
        joke_label.config(text="Press 'Show Joke' first!")

def returnToMenu():
    joke_label.config(text="")
    showFrame(start_frame)


def startApp():
    showFrame(joke_frame)

def quitApp():
    root.destroy()

root = Tk()
root.title("Cirno's Perfect Joke App!")
root.geometry("1000x1000")
root.iconphoto(False, ImageTk.PhotoImage(file="AlexaTellMeAJoke/Cirno.png"))


root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)


current_joke = None

img1 = Image.open("AlexaTellMeAJoke/Cirno.png")
resized_img1 = img1.resize ((500,400), Image.Resampling.LANCZOS)
photo1 = ImageTk.PhotoImage(resized_img1)


start_frame = Frame(root, bg="white")
start_frame.grid(row=0, column=0, sticky="nsew")
img1_label = Label(start_frame, image=photo1, bg= "white")
img1_label.image = photo1
img1_label.place(x=-50, y=250)

mainTitle =Label(start_frame, text="Welcome to Cirno's Greatest Joke App!", font=("Impact", 32,), bg="white").place(x=155, y=190)
startButton = ctk.CTkButton(master=start_frame, text="Start", fg_color="#aaaaaa",text_color="black", hover_color="#484848", width=150, height= 50, corner_radius=50,font=('Impact',20),command=startApp).place(x=425, y=300)

quitButton = ctk.CTkButton(master=start_frame, text="Quit", fg_color="#aaaaaa",text_color="black", hover_color="#484848", width=150, height= 50, corner_radius=50,font=('Impact',20),command=quitApp).place(x=425, y= 375)

img2= Image.open("AlexaTellMeAJoke/Speech.png")
resized_img2=img2.resize((500,200), Image.Resampling.LANCZOS)
photo2 = ImageTk.PhotoImage(resized_img2)

joke_frame = Frame(root, bg="white")
joke_frame.grid(row=0, column=0, sticky="nsew")

img2_label = Label(joke_frame, image= photo2, bg="white")
img2_label.image=photo2
img2_label.place(x=250, y= 50)
img1_label = Label(joke_frame, image=photo1, bg= "white")
img1_label.image = photo1
img1_label.place(x=500, y=250)

joke_label = Label(joke_frame, text="", wraplength=400, font=("Impact", 14), bg="white")
joke_label.place(x=325, y=110)

jokeButton = ctk.CTkButton(master=joke_frame, text="Show Joke", fg_color="#aaaaaa",text_color="black", hover_color="#484848", width=150, height= 50, corner_radius=50,font=('Impact',20), command=showJoke).place(x=430, y=300)
punchlineButton = ctk.CTkButton(master=joke_frame, text="Show Punchline", fg_color="#aaaaaa",text_color="black", hover_color="#484848", width=150, height= 50, corner_radius=50,font=('Impact',20), command=showPunchline).place(x=415, y=360)
ListenButton =ctk.CTkButton(master=joke_frame, text="Listen", fg_color="#aaaaaa",text_color="black", hover_color="#484848", width=120, height= 30, corner_radius=50,font=('Impact',20), command=speakText).place(x=440, y=225)
returnButton = ctk.CTkButton(master=joke_frame, text="Return", fg_color="#aaaaaa",text_color="black", hover_color="#484848", width=150, height= 50, corner_radius=50,font=('Impact',20), command=returnToMenu).place(x=430, y=420)

showFrame(start_frame)

root.mainloop()

from tkinter import *
import random
import operator
from PIL import ImageTk, Image
from pygame import mixer
import threading
import os
import customtkinter as ctk

mixer.init()
correct_sound = mixer.Sound("Math quiz/Correct.mp3")
wrong_sound = mixer.Sound("Math quiz/Wrong.mp3")
button_sound = mixer.Sound("Math quiz/Menu.mp3")

def play_background_music():
    music_file = "Math quiz/Bgmusic.mp3"  # Replace with your music file path
    
    if os.path.exists(music_file):
        mixer.music.load(music_file)
        # Play the music in an infinite loop (-1 means loop forever)
        mixer.music.play(-1) 
    else:
        print(f"Error: {music_file} not found.")

def stop_music():
    mixer.music.stop()

root = Tk()
root.configure(bg="#F9EBFF")
root.title("Neco's Impossible Math Quiz")
root.geometry('1000x1000')
root.iconphoto(False, ImageTk.PhotoImage(file="Math Quiz/icon.png"))

score = 0
current_question = 0
operations = {
    '+': operator.add,
    '-': operator.sub,
}
last_grade_frame = None

music_thread = threading.Thread(target=play_background_music)
music_thread.daemon = True # Allows the thread to close when the main program exits
music_thread.start()

def decideNumbers(difficulty):
    if difficulty == "easy":
        return random.randint(1, 9), random.randint(1, 9)
    elif difficulty == "moderate":
        return random.randint(10, 99), random.randint(10, 99)
    else:  # hard
        return random.randint(1000, 9999), random.randint(1000, 9999)
    
def decideOperation():
    return random.choice(['+', '-'])

def check_answer(num1, num2, op, user_answer, attempts=1):
    global score
    correct_answer = operations[op](num1, num2)# Perform the operation
    try:
        user_answer = float(user_answer)
    except ValueError:
        return False
    
    if abs(correct_answer - user_answer) < 0.01:  # For floating point comparison
        if attempts == 1:
            score += 10
        else:
            score += 5
        return True
    return False


def displayResults():
    global last_grade_frame
    grade_frame = Frame(difficultyMenu, bg="#F9EBFF")
    grade_frame.place(x=200, y=0, width=600, height=600)
    last_grade_frame = grade_frame
    
    if score >= 90:
        grade = "A+"
    elif score >= 80:
        grade = "A"
    elif score >= 70:
        grade = "B"
    elif score >= 60:
        grade = "C"
    elif score >= 50:
        grade = "D"
    else:
        grade = "F"
    Label(grade_frame, text=f"Final Score: {score}/100\nGrade: {grade}", 
          font=('Comic Sans MS', 24), bg='#F9EBFF').pack(pady=20)

    def close_grade_and_goto_menu():  # Close grade frame and go to main menu
        global last_grade_frame # to track the last grade frame
        if last_grade_frame is not None:
            try:
                last_grade_frame.destroy()
            except:
                pass
            last_grade_frame = None
        switch_to_frame(menu)

    ctk.CTkButton(master=grade_frame, text="Try Again", border_width=7, border_color="#1500ff", fg_color="#f2cbff",text_color="black", hover_color="#B075B1", width=210, height= 70, corner_radius=50,font=('Comic Sans MS',30),command=close_grade_and_goto_menu).pack(pady=10)
    
def start_quiz(difficulty):
    button_sound.play()
    global score, current_question, last_grade_frame
    if last_grade_frame is not None:
        try:
            last_grade_frame.destroy()
        except:
            pass
        last_grade_frame = None
    score = 0
    current_question = 0

    quiz_frame = Frame(difficultyMenu, bg="#F9EBFF")
    quiz_frame.place(x=200, y=0, width=600, height=600)

    problem_label = Label(quiz_frame, text="", font=('Comic Sans MS', 20), bg='#F9EBFF')
    problem_label.pack(pady=20)

    answer_entry = Entry(quiz_frame, font=('Comic Sans MS', 16))
    answer_entry.pack(pady=10)

    result_label = Label(quiz_frame, text="", font=('Comic Sans MS', 16), bg='#F9EBFF')
    result_label.pack(pady=10)
    # create one Submit button and reuse it for every question (prevents multiple buttons)
    submit_button = ctk.CTkButton(master=quiz_frame, text="Submit", border_width=7, border_color="#1500ff", fg_color="#f2cbff",text_color="black", hover_color="#B075B1", width=210, height= 70, corner_radius=50,font=('Comic Sans MS',30))
    submit_button.pack(pady=10)

    # Add quit button
    def quit_quiz():
        quiz_frame.destroy()
        switch_to_frame(menu)
    
    quit_button = ctk.CTkButton(master=quiz_frame, text="Quit to Menu", border_width=7, border_color="#1500ff", fg_color="#f2cbff",text_color="black", hover_color="#B075B1", width=210, height= 70, corner_radius=50,font=('Comic Sans MS',30),command = quit_quiz)
    quit_button.pack(pady=10)

    def next_question():
        nonlocal submit_button
        if current_question >= 10:
            quiz_frame.destroy()
            displayResults()
            return
        # reset attempts for this new question
        attempts = 0
        num1, num2 = decideNumbers(difficulty)
        op = decideOperation()
        problem_label.configure(text=f"Question {current_question + 1}/10:\n{num1} {op} {num2} = ?")
        answer_entry.delete(0, END)
        result_label.configure(text="")

        def check_and_proceed():
            nonlocal attempts, num1, num2, op
            global current_question
            attempts += 1
            user_answer = answer_entry.get()

            if check_answer(num1, num2, op, user_answer, attempts):
                if attempts == 1:
                    result_label.configure(text="Correct! +10 points", fg="green")
                    correct_sound.play()
                else:
                    result_label.configure(text="Correct! +5 points", fg="green")
                current_question += 1
                correct_sound.play()
                # small delay so user sees feedback
                difficultyMenu.after(800, next_question)
            else:
                if attempts >= 2:
                    result_label.configure(text="Wrong! 0 points", fg="red")
                    current_question += 1
                    difficultyMenu.after(800, next_question)
                    wrong_sound.play()
                else:
                    result_label.configure(text="Wrong! Try again (5 points if correct)", fg="orange")
                    wrong_sound.play()

        # set the submit button to call the current question's checker (overwrite previous command)
        submit_button.configure(command=check_and_proceed)
    next_question()
    
def close_window():
    root.destroy()
def switch_to_frame(frame):
    button_sound.play()
    frame.tkraise()

# Function to display the difficulty menu
def display_menu():
    switch_to_frame(difficultyMenu)

# Create Frame 1
menu = Frame(root,bg="#F9EBFF")
img = Image.open("Math quiz/neco.png")
titleImg = Image.open("Math quiz/Title.png")
# Resize image to reasonable dimensions (adjust size as needed)
resized_img = img.resize((300, 400), Image.Resampling.LANCZOS)
resized_img2 = titleImg.resize((600, 200), Image.Resampling.LANCZOS) # Use LANCZOS for high-quality downsampling
photo = ImageTk.PhotoImage(resized_img)
photo2 = ImageTk.PhotoImage(resized_img2)

# Create label to hold image
title_Label = Label(menu, image=photo2, bg='#F9EBFF')
title_Label.image = photo2  # Keep a reference to prevent garbage collection
title_Label.place(x=190, y=0)
img_label = Label(menu, image=photo, bg='#F9EBFF')
img_label.image = photo  # Keep a reference to prevent garbage collection
img_label.place(x=70, y=195)


button1 = ctk.CTkButton(master=menu, text="Play",command=display_menu,border_width=7, border_color="#1500ff", fg_color="#f2cbff",text_color="black", hover_color="#B075B1", width=210, height= 70, corner_radius=50,font=('Comic Sans MS',30))
button1.place(x=400,y=250)
button2 = ctk.CTkButton(master=menu, text="Instructions",command=lambda:switch_to_frame(instructionsMenu),border_width=7, border_color="#1500ff", fg_color="#f2cbff",text_color="black", hover_color="#B075B1", width=210, height= 70, corner_radius=50,font=('Comic Sans MS',30))
button2.place(x=380,y=325)
button3 = ctk.CTkButton(command=close_window, master=menu, text="Quit", border_width=7, border_color="#1500ff", fg_color="#f2cbff",text_color="black", hover_color="#B075B1", width=210, height= 70, corner_radius=50,font=('Comic Sans MS',30))
button3.place(x=400,y=400)
menu.place(x=0,y=50, width=1000,height=1000)

difficultyMenu = Frame(root, bg="#F9EBFF")
Label(difficultyMenu, text="Choose Difficulty", font=('Comic Sans MS', 24), bg='#F9EBFF').pack(pady=20)

ctk.CTkButton(master=difficultyMenu, text="Easy", border_width=7, border_color="#1500ff", fg_color="#83ff94",text_color="black", hover_color="#B075B1", width=210, height= 70, corner_radius=50,font=('Comic Sans MS',30), command=lambda: start_quiz("easy")).pack(pady=10)
ctk.CTkButton(master=difficultyMenu, text="Moderate", border_width=7, border_color="#1500ff", fg_color="#ffea7f",text_color="black", hover_color="#B075B1", width=210, height= 70, corner_radius=50,font=('Comic Sans MS',30), command=lambda: start_quiz("moderate")).pack(pady=10)
ctk.CTkButton(master=difficultyMenu, text="Hard", border_width=7, border_color="#1500ff", fg_color="#ff6a6a",text_color="black", hover_color="#B075B1", width=210, height= 70, corner_radius=50,font=('Comic Sans MS',30),command=lambda: start_quiz("hard")).pack(pady=10)
ctk.CTkButton(master=difficultyMenu, text="Back to menu", border_width=7, border_color="#1500ff", fg_color="#f2cbff",text_color="black", hover_color="#B075B1", width=210, height= 70, corner_radius=50,font=('Comic Sans MS',30),command=lambda: switch_to_frame(menu)).pack(pady=10)

difficultyMenu.place(x=0, y=50, width=1000, height=1000)


instructionsMenu = Frame(root, bg="#F9EBFF" )

label1 = Label(instructionsMenu, text="INSTRUCTIONS", font=('Comic Sans MS',24),bg= '#F9EBFF', fg="#000000")
label1.pack(pady=10)
instructions_text = """
Neco Arc has prepared a few math questions to test your intellect.

There are three difficulties which are easy, moderate and hard. 
They differ with the values used.

There are 10 questions present in each difficulty and you have 2 attempts 
to get the answer correct.

Each answer is worth:
• 10 points for correct first attempt
• 5 points if correct on second attempt
• 0 points if both attempts are wrong

What are you waiting for? Answer those questions!
"""
# Create and pack the instruction label
label2 = Label(instructionsMenu, text=instructions_text, 
               font=('Comic Sans MS',16), bg='#F9EBFF', 
               fg="#000000", justify=LEFT)
label2.pack(pady=10)

button3 = ctk.CTkButton(master=instructionsMenu, text="Return", border_width=7, border_color="#1500ff", fg_color="#f2cbff",text_color="black", hover_color="#B075B1", width=210, height= 70, corner_radius=50,font=('Comic Sans MS',30),command=lambda: switch_to_frame(menu))
button3.pack()
instructionsMenu.place(x=0,y=50, width=1000,height=1000)
# Initially, show Frame 1
switch_to_frame(menu)
root.mainloop()
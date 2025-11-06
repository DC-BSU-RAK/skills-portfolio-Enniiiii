from tkinter import *
import random
import operator
from PIL import ImageTk, Image

root = Tk()
root.config(bg="#FFFFFF")
root.title("Neco's Impossible Math Quiz")
root.geometry('1000x1000')

score = 0
current_question = 0
operations = {
    '+': operator.add,
    '-': operator.sub,
}
last_grade_frame = None

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
    grade_frame = Frame(difficultyMenu, bg="white")
    grade_frame.place(x=200, y=0, width=600, height=400)
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
          font=('Roboto', 24), bg='white').pack(pady=20)

    def close_grade_and_goto_menu():  # Close grade frame and go to main menu
        global last_grade_frame # to track the last grade frame
        if last_grade_frame is not None:
            try:
                last_grade_frame.destroy()
            except:
                pass
            last_grade_frame = None
        switch_to_frame(menu)

    Button(grade_frame, text="Try Again", command=close_grade_and_goto_menu,
           fg="#ffffff", bg="#234567").pack(pady=10)
    
def start_quiz(difficulty):
    global score, current_question, last_grade_frame
    if last_grade_frame is not None:
        try:
            last_grade_frame.destroy()
        except:
            pass
        last_grade_frame = None
    score = 0
    current_question = 0

    quiz_frame = Frame(difficultyMenu, bg="white")
    quiz_frame.place(x=200, y=0, width=600, height=400)

    problem_label = Label(quiz_frame, text="", font=('Roboto', 20), bg='white')
    problem_label.pack(pady=20)

    answer_entry = Entry(quiz_frame, font=('Roboto', 16))
    answer_entry.pack(pady=10)

    result_label = Label(quiz_frame, text="", font=('Roboto', 16), bg='white')
    result_label.pack(pady=10)
    # create one Submit button and reuse it for every question (prevents multiple buttons)
    submit_button = Button(quiz_frame, text="Submit", fg="#ffffff", bg="#234567")
    submit_button.pack(pady=10)

    # Add quit button
    def quit_quiz():
        quiz_frame.destroy()
        switch_to_frame(menu)
    
    quit_button = Button(quiz_frame, text="Quit to Main Menu", 
                        command=quit_quiz,
                        fg="#ffffff", bg="#234567")
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
        problem_label.config(text=f"Question {current_question + 1}/10:\n{num1} {op} {num2} = ?")
        answer_entry.delete(0, END)
        result_label.config(text="")

        def check_and_proceed():
            nonlocal attempts, num1, num2, op
            global current_question
            attempts += 1
            user_answer = answer_entry.get()

            if check_answer(num1, num2, op, user_answer, attempts):
                if attempts == 1:
                    result_label.config(text="Correct! +10 points", fg="green")
                else:
                    result_label.config(text="Correct! +5 points", fg="green")
                current_question += 1
                # small delay so user sees feedback
                difficultyMenu.after(800, next_question)
            else:
                if attempts >= 2:
                    result_label.config(text="Wrong! 0 points", fg="red")
                    current_question += 1
                    difficultyMenu.after(800, next_question)
                else:
                    result_label.config(text="Wrong! Try again (5 points if correct)", fg="orange")

        # set the submit button to call the current question's checker (overwrite previous command)
        submit_button.config(command=check_and_proceed)
    next_question()
    
def close_window():
    root.destroy()
def switch_to_frame(frame):
    frame.tkraise()

# Function to display the difficulty menu
def display_menu():
    switch_to_frame(difficultyMenu)   



# Create Frame 1
menu = Frame(root,bg="white")
img = Image.open("necobarc.png")
titleImg = Image.open("Title.png")
# Resize image to reasonable dimensions (adjust size as needed)
resized_img = img.resize((300, 400), Image.Resampling.LANCZOS)
resized_img2 = titleImg.resize((600, 200), Image.Resampling.LANCZOS) # Use LANCZOS for high-quality downsampling
photo = ImageTk.PhotoImage(resized_img)
photo2 = ImageTk.PhotoImage(resized_img2)

# Create label to hold image
title_Label = Label(menu, image=photo2, bg='white')
title_Label.image = photo2  # Keep a reference to prevent garbage collection
title_Label.place(x=190, y=0)
img_label = Label(menu, image=photo, bg='white')
img_label.image = photo  # Keep a reference to prevent garbage collection
img_label.place(x=50, y=220)


button1 = Button(menu, text="Play",fg="#ffffff",bg="#234567", command=display_menu,width=20,font=('Roboto',12))
button1.place(x=400,y=250)
button2 = Button(menu, text="Instructions",fg="#ffffff",bg="#234567", command=lambda:switch_to_frame(instructionsMenu),width=20,font=('Roboto',12))
button2.place(x=400,y=300)
button3 = Button(menu, text="Quit",fg="#ffffff",bg="#234567", command=close_window,width=20,font=('Roboto',12))
button3.place(x=400,y=350)
menu.place(x=0,y=50, width=1000,height=1000)

difficultyMenu = Frame(root, bg="white")
Label(difficultyMenu, text="Choose Difficulty", font=('Roboto', 24), bg='white').pack(pady=20)

Button(difficultyMenu, text="Easy", command=lambda: start_quiz("easy"),
       fg="#ffffff", bg="#234567", width=20, font=('Roboto', 12)).pack(pady=10)
Button(difficultyMenu, text="Moderate", command=lambda: start_quiz("moderate"),
       fg="#ffffff", bg="#234567", width=20, font=('Roboto', 12)).pack(pady=10)
Button(difficultyMenu, text="Hard", command=lambda: start_quiz("hard"),
       fg="#ffffff", bg="#234567", width=20, font=('Roboto', 12)).pack(pady=10)
Button(difficultyMenu, text="Back to Main Menu", command=lambda: switch_to_frame(menu),
       fg="#ffffff", bg="#234567", width=20, font=('Roboto', 12)).pack(pady=10)

difficultyMenu.place(x=0, y=50, width=1000, height=1000)


instructionsMenu = Frame(root, bg="#FFFFFF" )

label1 = Label(instructionsMenu, text="INSTRUCTIONS", font=('Roboto',24),bg= 'white', fg="#000000")
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
               font=('Roboto',16), bg='white', 
               fg="#000000", justify=LEFT)
label2.pack(pady=10)

button3 = Button(instructionsMenu, text="Return to Main Menu",fg="#ffffff",bg="#234567", command=lambda: switch_to_frame(menu))
button3.pack()
instructionsMenu.place(x=0,y=50, width=1000,height=1000)
# Initially, show Frame 1
switch_to_frame(menu)
root.mainloop()
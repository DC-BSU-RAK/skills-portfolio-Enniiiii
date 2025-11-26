from tkinter import *
from tkinter import ttk
from tkinter import messagebox # Used for error handling
from pygame import mixer
from PIL import ImageTk, Image
import os
import threading

mixer.init()
def quitButton():
    root.destroy()

def updateFileData(student_id, name, c1, c2, c3, exam):
    lines = []
    with open("StudentManager/studentMarks.txt", "r") as f:
        lines = f.readlines()

    # Write back, replacing the matching student line (match id at start)
    with open("StudentManager/studentMarks.txt", "w") as f:
        for line in lines:
            line_strip = line.strip()
            if not line_strip:
                continue
            # robust split to compare id
            parts = line_strip.split(",")
            if parts[0] == str(student_id):
                f.write(f"{student_id},{name},{c1},{c2},{c3},{exam}\n")
            else:
                f.write(line if line.endswith("\n") else line + "\n")


def updateStudentWindow():
    
    selected = tree.selection()
    values = tree.item(selected)["values"]

    student_id = str(values[0])

    student = {
    "id": values[0],
    "name": values[1],
    "c1": int(values[2]),
    "c2": int(values[3]),
    "c3": int(values[4]),
    "exam": int(values[5]),
    }
    if not selected:
        messagebox.showerror("Error", "Please select a student to update.")
        return

    item = tree.item(selected)
    values = item["values"]

    student_id = str(values[0])  # ensure string for matching
    # find the student in the in-memory list
    student = None
    for s in students:
        if s["id"] == student_id:
            student = s
            break

    if student is None:
        messagebox.showerror("Error", "Selected student not found in memory.")
        return

    # popup window
    updateWin = Toplevel(root)
    updateWin.title("Update Student Record")
    updateWin.geometry("350x380")

    # ID (disabled)
    Label(updateWin, text="Student ID: (cannot change)").pack()
    id_entry = Entry(updateWin)
    id_entry.insert(0, student["id"])
    id_entry.config(state="disabled")
    id_entry.pack()

    # Name
    Label(updateWin, text="Student Name:").pack()
    name_entry = Entry(updateWin)
    name_entry.insert(0, student["name"])
    name_entry.pack()

    # Course marks (use the original c1,c2,c3)
    Label(updateWin, text="Course Mark 1 (0-60):").pack()
    c1_entry = Entry(updateWin)
    c1_entry.insert(0, str(student["c1"]))
    c1_entry.pack()

    Label(updateWin, text="Course Mark 2 (0-60):").pack()
    c2_entry = Entry(updateWin)
    c2_entry.insert(0, str(student["c2"]))
    c2_entry.pack()

    Label(updateWin, text="Course Mark 3 (0-60):").pack()
    c3_entry = Entry(updateWin)
    c3_entry.insert(0, str(student["c3"]))
    c3_entry.pack()

    Label(updateWin, text="Exam Mark (0-100):").pack()
    exam_entry = Entry(updateWin)
    exam_entry.insert(0, str(student["exam"]))
    exam_entry.pack()

    def save_updates():
        # Validate and parse
        new_name = name_entry.get().strip()
        try:
            new_c1 = int(c1_entry.get())
            new_c2 = int(c2_entry.get())
            new_c3 = int(c3_entry.get())
            new_exam = int(exam_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Course and exam marks must be integers.")
            return

        if not (0 <= new_c1 <= 60 and 0 <= new_c2 <= 60 and 0 <= new_c3 <= 60):
            messagebox.showerror("Invalid Course Mark", "Coursework marks must be 0–60.")
            return
        if not (0 <= new_exam <= 100):
            messagebox.showerror("Invalid Exam Mark", "Exam mark must be 0–100.")
            return

        # recompute totals, percent and grade
        total_course = new_c1 + new_c2 + new_c3
        percent = ((total_course + new_exam) / 160) * 100
        if percent >= 70:
            grade = "A"
        elif percent >= 60:
            grade = "B"
        elif percent >= 50:
            grade = "C"
        elif percent >= 40:
            grade = "D"
        else:
            grade = "F"

        # update in-memory student dict
        student["name"] = new_name
        student["c1"] = new_c1
        student["c2"] = new_c2
        student["c3"] = new_c3
        student["course"] = total_course
        student["exam"] = new_exam
        student["percent"] = percent
        student["grade"] = grade

        # update file
        updateFileData(student["id"], new_name, new_c1, new_c2, new_c3, new_exam)

        # refresh treeview and dropdown
        viewAll()  # rebuilds table and updates summary
        # update dropdown menu entries (rebuild to avoid duplicates)
        menu = dropdownMenu["menu"]
        menu.delete(0, "end")
        for nm in [s["name"] for s in students]:
            menu.add_command(label=nm, command=lambda v=nm: dropdownButton.set(v))

        messagebox.showinfo("Success", "Student record updated.")
        updateWin.destroy()

    Button(updateWin, text="Save Changes", command=save_updates).pack(pady=10)


def playBackgroundMusic():
    music_file = "StudentManager/BGM.mp3"  # Replace with your music file path
    
    if os.path.exists(music_file):
        mixer.music.load(music_file)
        # Play the music in an infinite loop (-1 means loop forever)
        mixer.music.play(-1) 
    else:
        print(f"Error: {music_file} not found.")

music_thread = threading.Thread(target=playBackgroundMusic)
music_thread.daemon = True # Allows the thread to close when the main program exits
music_thread.start()

def deleteStudentRecord():
    selected = tree.selection()
    if not selected:
        messagebox.showerror("Error", "Please select a student to delete.")
        return

    item = tree.item(selected)
    student_id = item["values"][0]  # first column is ID

    # Confirm delete
    confirm = messagebox.askyesno("Delete Student", f"Delete student ID {student_id}?")
    if not confirm:
        return

    # Remove from file
    lines = []
    with open("StudentManager/studentMarks.txt", "r") as f:
        lines = f.readlines()

    with open("StudentManager/studentMarks.txt", "w") as f:
        for line in lines:
            if not line.startswith(str(student_id)):
                f.write(line)

    # Remove from tree
    tree.delete(selected)

    messagebox.showinfo("Success", "Student record deleted.")


def addStudentWindow():
    win = Toplevel(root)
    win.title("Add New Student")
    win.geometry("300x320")

    labels = ["Student ID", "Name", "Course Mark 1", "Course Mark 2", "Course Mark 3", "Exam Mark"]
    entries = []

    for i, text in enumerate(labels):
        lbl = Label(win, text=text)
        lbl.pack()
        ent = Entry(win)
        ent.pack()
        entries.append(ent)

    def submit_newStudent():
        sid = entries[0].get().strip()
        name = entries[1].get().strip()

        try:
            c1 = int(entries[2].get())
            c2 = int(entries[3].get())
            c3 = int(entries[4].get())
            exam = int(entries[5].get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Course and exam marks must be numbers.")
            return

        # Validate ranges
        if not sid.isdigit() or len(sid) != 4:
            messagebox.showerror("Invalid ID", "Student ID must be 4 digits.")
            return
        if not (0 <= c1 <= 60 and 0 <= c2 <= 60 and 0 <= c3 <= 60):
            messagebox.showerror("Invalid Course Mark", "Coursework marks must be 0–60.")
            return
        if not (0 <= exam <= 100):
            messagebox.showerror("Invalid Exam Mark", "Exam mark must be 0–100.")
            return

        # Compute totals
        totalCourse = c1 + c2 + c3
        percent = ((totalCourse + exam) / 160) * 100

        if percent >= 70: grade = "A"
        elif percent >= 60: grade = "B"
        elif percent >= 50: grade = "C"
        elif percent >= 40: grade = "D"
        else: grade = "F"

        # Add to in-memory list
        newStudent = {
            "id": sid,
            "name": name,
            "course": totalCourse,
            "exam": exam,
            "percent": percent,
            "grade": grade
        }
        students.append(newStudent)

        # Append to text file
        with open("StudentManager/studentMarks.txt", "a") as f:
            f.write(f"\n{sid},{name},{c1},{c2},{c3},{exam}")

        # Refresh table
        viewAll()

        # Update dropdown list
        menu = dropdownMenu["menu"]
        menu.add_command(label=name, command=lambda v=name: dropdownButton.set(v))

        messagebox.showinfo("Success", f"Student '{name}' added.")
        win.destroy()

    submitButton=Button(win, text="Submit", command=submit_newStudent).pack(pady=10)



def sortAscending():
    clearTable()
    sortedStudents = sorted(students, key=lambda s: s["percent"])
    for s in sortedStudents:
        insertStudent(s)
    summaryLabel.config(text="Sorted: Ascending (Lowest → Highest)")

def sortDescending():
    clearTable()
    sortedStudents = sorted(students, key=lambda s: s["percent"], reverse=True)
    for s in sortedStudents:
        insertStudent(s)
    summaryLabel.config(text="Sorted: Descending (Highest → Lowest)")


def loadStudents():
    students = []
    with open("StudentManager/studentMarks.txt", "r") as f:
      for line in f:
            parts = line.strip().split(",")
            if len(parts) != 6:
                continue

            sid = parts[0]
            name = parts[1]
            c1, c2, c3 = map(int, parts[2:5])
            exam = int(parts[5])

            totalCourse = c1 + c2 + c3   # /60
            percent = ((totalCourse + exam) / 160) * 100

            if percent >= 70: grade = "A"
            elif percent >= 60: grade = "B"
            elif percent >= 50: grade = "C"
            elif percent >= 40: grade = "D"
            else: grade = "F"

            students.append({
                "id": sid,
                "name": name,
                "c1": c1,
                "c2": c2,
                "c3": c3,
                "course": totalCourse,
                "exam": exam,
                "percent": percent,
                "grade": grade
            }
            )

    return students


students = loadStudents()






def clearTable():
    for row in tree.get_children():
        tree.delete(row)

def insertStudent(s):
     tree.insert("", "end", values=(
        s["id"],
        s["name"],
        s["c1"],
        s["c2"],
        s["c3"],
        s["exam"],
        s["course"],     # total out of 60
        round(s["percent"], 2),
        s["grade"]
    ))


def viewAll():
    for row in tree.get_children():
        tree.delete(row)

    for s in students:
        insertStudent(s)





def viewSelected(*args):
    name = dropdownButton.get()

    clearTable()

    for s in students:
        if s["name"] == name:
            insertStudent(s)
            summaryLabel.config(text=f"Showing Record for {name}")
            return



def viewHighest():
    clearTable()
    top = max(students, key=lambda s: s["percent"])
    insertStudent(top)
    summaryLabel.config(text=f"Highest Scoring Student: {top['name']} ({top['percent']:.2f}%)")



def viewLowest():
    clearTable()
    low = min(students, key=lambda s: s["percent"])
    insertStudent(low)
    summaryLabel.config(text=f"Lowest Scoring Student: {low['name']} ({low['percent']:.2f}%)")



root = Tk()
root.title("Student Manager")
root.geometry("1300x1000")
root.iconphoto(False, ImageTk.PhotoImage(file="StudentManager/icon.png"))

BSUimg = Image.open("StudentManager/BSULOGO.png")
resizedBSUimg = BSUimg.resize((900,200), Image.Resampling.LANCZOS)
BSUPhoto = ImageTk.PhotoImage(resizedBSUimg)


BSULabel = Label(root, image = BSUPhoto)
BSULabel.image = BSUPhoto
BSULabel.pack(pady= 5)
Name = Label(root, text=" Student Manager", font=('Roboto',25), fg='#22263d')
Name.pack(pady=5)

columns = ("ID", "Name", "C1", "C2", "C3", "Exam", "CourseTotal", "Percent", "Grade")
tree = ttk.Treeview(root, columns=columns, show="headings", height=10)
scroll = ttk.Scrollbar(root, orient="vertical", command=tree.yview)


tree.heading("ID", text="ID")
tree.heading("Name", text="Name")
tree.heading("C1", text="Course 1")
tree.heading("C2", text="Course 2")
tree.heading("C3", text="Course 3")
tree.heading("Exam", text="Exam")
tree.heading("CourseTotal", text="Course Total")
tree.heading("Percent", text="Percent")
tree.heading("Grade", text="Grade")

tree.column("ID", width=60)
tree.column("Name", width=150)
tree.column("C1", width=80)
tree.column("C2", width=80)
tree.column("C3", width=80)
tree.column("Exam", width=80)
tree.column("CourseTotal", width=100)
tree.column("Percent", width=80)
tree.column("Grade", width=60)

tree.pack(side="left", fill="both", expand=True)  
scroll.pack(side="right", fill="y")


btnFrame = Frame(root)
btnFrame.pack()



viewButton = Button(btnFrame, text="View All Students", height=5,width=20, command=viewAll).grid(row=0, column=0, padx=5, pady=5)
highestMarkButton = Button(btnFrame, text="Highest Mark",height=5, width=20, command=viewHighest).grid(row=0, column=1, padx=5, pady=5)
lowestMarkButton = Button(btnFrame, text="Lowest Mark",height=5, width=20, command=viewLowest).grid(row=0, column=2, padx=5, pady=5)
ascendingButton = Button(btnFrame, text="Sort Ascending", height=5,width=20, command=sortAscending).grid(row=1, column=1, padx=5, pady=5)
descendingButton = Button(btnFrame, text="Sort Descending",height=5, width=20, command=sortDescending).grid(row=1, column=2, padx=5, pady=5)
studentButton = Button(btnFrame, text="Add Student",height=5, width=20, command=addStudentWindow).grid(row=1, column=0, padx=5, pady=5)
deleteButton = Button(btnFrame, text="Delete Student Record",height=5,width=20, command=deleteStudentRecord).grid(row=2, column=0, padx=5, pady=5)
updateButton = Button(btnFrame, text="Update Student Record",height=5,width = 20, command=updateStudentWindow).grid(row=2, column=1, padx=5, pady=5) 

quitButton = Button(root, text="Quit Student Manager", command=quitButton).pack(pady=10)

dropdownButton = StringVar()
dropdownButton.set("Select Student")

names = [s["name"] for s in students]
dropdownMenu = ttk.OptionMenu(btnFrame, dropdownButton, "Select Student", *names, command=viewSelected)
dropdownMenu.grid(row=3, column=0, columnspan=3, pady=10)
summaryLabel = Label(root, text="", font=("Arial", 12))
summaryLabel.pack(pady=5)

root.mainloop()

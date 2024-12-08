import tkinter as tk
from tkinter import *
import cv2
import os
import datetime
import time
from pymongo import MongoClient

# MongoDB Connection
try:
    client = MongoClient("mongodb://localhost:27017/")
    db = client["attendance_management"]
    print("Connected to MongoDB")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")

# Main window
window = tk.Tk()
window.title("Attendance Management System")
window.geometry('1280x720')
window.configure(background='#ffffd4')

# Helper function for error popups
def error_popup(message):
    popup = tk.Toplevel(window)
    popup.geometry('300x100')
    popup.title('Warning!')
    popup.configure(background='grey80')
    tk.Label(popup, text=message, fg='red', bg='white', font=('times', 14)).pack(pady=10)
    tk.Button(popup, text='OK', command=popup.destroy, fg="black", bg="green", width=10).pack()

# Log student with face image and save attendance history
def log_student_image():
    enrollment = txt.get()
    name = txt2.get()
    subject = subject_txt.get()
    if not enrollment or not name or not subject:
        error_popup("Enrollment, Name, and Subject are required!")
        return

    try:
        cam = cv2.VideoCapture(0)
        detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        sample_num = 0
        while True:
            ret, img = cam.read()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                sample_num += 1
                file_path = f"TrainingImage/{name}_{enrollment}_{sample_num}.jpg"
                cv2.imwrite(file_path, gray[y:y+h, x:x+w])
                cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.imshow('Capturing Images', img)
            if cv2.waitKey(1) & 0xFF == ord('q') or sample_num >= 5:  # Capture 5 images
                break
        cam.release()
        cv2.destroyAllWindows()

        ts = time.time()
        logged_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        logged_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')

        student_data = {
            "enrollment": enrollment,
            "name": name,
            "subject": subject,
            "images_saved": sample_num,
            "image_path": f"TrainingImage/{name}_{enrollment}_1.jpg",
            "attendance_history": [
                {
                    "subject": subject,
                    "date": logged_date,
                    "time": logged_time
                }
            ]
        }

        db["students"].insert_one(student_data)
        error_popup(f"Student {name} logged successfully!")
    except Exception as e:
        error_popup(f"Error logging student: {e}")

# Manual Attendance Entry
def manually_fill():
    def log_manual_attendance():
        subject = SUB_ENTRY.get()
        student_name = STUDENT_NAME_ENTRY.get()
        student_enrollment = STUDENT_ENROLLMENT_ENTRY.get()
        if not subject or not student_name or not student_enrollment:
            error_popup("All fields are required!")
            return

        ts = time.time()
        date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        time_logged = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        record = {
            "subject": subject,
            "date": date,
            "time": time_logged,
            "students": [{"name": student_name, "enrollment": student_enrollment}]
        }
        try:
            db["manual_attendance"].insert_one(record)
            error_popup("Manual Attendance Logged!")
            manual_window.destroy()
        except Exception as e:
            error_popup(f"Error logging attendance: {e}")

    def capture_image_for_manual():
        student_name = STUDENT_NAME_ENTRY.get()
        student_enrollment = STUDENT_ENROLLMENT_ENTRY.get()
        subject = SUB_ENTRY.get()
        if not student_name or not student_enrollment or not subject:
            error_popup("Please fill Name, Enrollment, and Subject first!")
            return

        try:
            cam = cv2.VideoCapture(0)
            detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            sample_num = 0
            while True:
                ret, img = cam.read()
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = detector.detectMultiScale(gray, 1.3, 5)
                for (x, y, w, h) in faces:
                    sample_num += 1
                    file_path = f"TrainingImage/{student_name}_{student_enrollment}_{sample_num}.jpg"
                    cv2.imwrite(file_path, gray[y:y+h, x:x+w])
                    cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
                cv2.imshow('Capturing Images', img)
                if cv2.waitKey(1) & 0xFF == ord('q') or sample_num >= 5:  # Stop after 5 images
                    break
            cam.release()
            cv2.destroyAllWindows()
            error_popup(f"Images for {student_name} logged successfully!")
        except Exception as e:
            error_popup(f"Error capturing image: {e}")

    manual_window = tk.Toplevel(window)
    manual_window.title("Manual Attendance")
    manual_window.geometry('580x450')
    manual_window.configure(background='grey80')

    tk.Label(manual_window, text="Subject:", font=('Times New Roman', 15)).place(x=30, y=50)
    SUB_ENTRY = tk.Entry(manual_window, width=20, font=('Times New Roman', 20))
    SUB_ENTRY.place(x=200, y=50)

    tk.Label(manual_window, text="Student Name:", font=('Times New Roman', 15)).place(x=30, y=120)
    STUDENT_NAME_ENTRY = tk.Entry(manual_window, width=20, font=('Times New Roman', 20))
    STUDENT_NAME_ENTRY.place(x=200, y=120)

    tk.Label(manual_window, text="Enrollment No:", font=('Times New Roman', 15)).place(x=30, y=190)
    STUDENT_ENROLLMENT_ENTRY = tk.Entry(manual_window, width=20, font=('Times New Roman', 20))
    STUDENT_ENROLLMENT_ENTRY.place(x=200, y=190)

    tk.Button(manual_window, text="Log Image", command=capture_image_for_manual, font=('Times New Roman', 15),
              bg="lightgreen", width=15).place(x=100, y=300)
    tk.Button(manual_window, text="Submit Attendance", command=log_manual_attendance, font=('Times New Roman', 15),
              bg="SkyBlue1", width=15).place(x=340, y=300)

# View logged students
# def view_logged_students():
#     students = list(db["students"].find())
#     records_window = tk.Toplevel(window)
#     records_window.title("Logged Students")
#     records_window.geometry('600x400')
#     records_window.configure(background='grey80')
#     tk.Label(records_window, text="Logged Students", font=('Times New Roman', 20, 'bold')).pack()
#     if students:
#         for student in students:
#             info = (f"Name: {student['name']}, Enrollment: {student['enrollment']}, "
#                     f"Subject: {student['subject']}, Images Saved: {student.get('images_saved', 0)}")
#             tk.Label(records_window, text=info, font=('Times New Roman', 14)).pack()
#     else:
#         tk.Label(records_window, text="No records found!", font=('Times New Roman', 14)).pack()

def view_attendance():
    attendance_records = list(db["manual_attendance"].find())
    attendance_window = tk.Toplevel(window)
    attendance_window.title("View Attendance")
    attendance_window.geometry('800x400')
    attendance_window.configure(background='grey80')
    tk.Label(attendance_window, text="Attendance Records", font=('Times New Roman', 20, 'bold')).pack()
    if attendance_records:
        for record in attendance_records:
            record_info = (f"Subject: {record['subject']}, Date: {record['date']}, "
                           f"Time: {record['time']}, Students: {', '.join([s['name'] for s in record['students']])}")
            tk.Label(attendance_window, text=record_info, font=('Times New Roman', 14)).pack()
    else:
        tk.Label(attendance_window, text="No attendance records found!", font=('Times New Roman', 14)).pack()



# Main GUI
tk.Label(window, text="Attendance Management System", font=('Times New Roman', 30), bg="black", fg="white").pack()

# Enrollment field
tk.Label(window, text="Enrollment:", font=('Times New Roman', 15)).place(x=200, y=150)
txt = tk.Entry(window, font=('Times New Roman', 15))
txt.place(x=400, y=150)

# Subject field
tk.Label(window, text="Subject:", font=('Times New Roman', 15)).place(x=200, y=200)
subject_txt = tk.Entry(window, font=('Times New Roman', 15))
subject_txt.place(x=400, y=200)

# Name field
tk.Label(window, text="Name:", font=('Times New Roman', 15)).place(x=200, y=250)
txt2 = tk.Entry(window, font=('Times New Roman', 15))
txt2.place(x=400, y=250)

# Buttons
tk.Button(window, text="Log Image", command=log_student_image, font=('Times New Roman', 15),bg="lightgreen" , width=15).place(x=200, y=300)
tk.Button(window, text="Manual Attendance", command=manually_fill, font=('Times New Roman', 15)).place(x=400, y=300)
# tk.Button(window, text="View Students", command=view_logged_students, font=('Times New Roman', 15)).place(x=600, y=300)
tk.Button(window, text="View Attendance", command=view_attendance, font=('Times New Roman', 15), width=15).place(x=600, y=300)


window.mainloop()

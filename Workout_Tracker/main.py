


import requests
import webbrowser
from tkinter import *
from tkinter import messagebox
from datetime import datetime

# Nutritionix API
APP_ID = "5c663869"
API_KEY = "9a68c02a386d3641f296ee1b2d073aed"

# Sheety API
SHEET_URL = "https://api.sheety.co/39de4e2da8695938464d35c3b6cfe976/workouts/workouts"
SHEET_HEADERS = {"Authorization": f"Bearer a6fgeigfiqh98"}

# Google Sheet link (the one linked to Sheety)
GOOGLE_SHEET_LINK = "https://docs.google.com/spreadsheets/d/1mZZUtnBNew1gG6E91HwoJjJtXPor6yr9W4-ezxA6-O8/edit?gid=0#gid=0"


# TRACKING WORKOUT

def track(inp):
    url = "https://trackapi.nutritionix.com/v2/natural/exercise"
    parameters = {
        "query": inp,
        "weight_kg": 62,
        "height_cm": 172,
        "age": 18
    }
    headers = {"x-app-id": APP_ID, "x-app-key": API_KEY}

    try:
        response = requests.post(url=url, json=parameters, headers=headers)
        response.raise_for_status()
        data = response.json()
        exercise_data = data['exercises']
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch workout data: {e}")
        return

    today = datetime.now()

    for i in exercise_data:
        sheet_params = {
            "workout": {
                "date": today.strftime("%d/%m/%Y"),
                "time": today.strftime("%H:%M:%S"),
                "exercise": i["name"],
                "duration": i["duration_min"],
                "calories": i["nf_calories"]
            }
        }
        try:
            response2 = requests.post(url=SHEET_URL, json=sheet_params, headers=SHEET_HEADERS)
            response2.raise_for_status()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save workout: {e}")
            return

    messagebox.showinfo("Success", "Workout added successfully ✅")


# OPENING GOOGLE SHEETS

def view_history():
    try:
        webbrowser.open(GOOGLE_SHEET_LINK)
    except Exception as e:
        messagebox.showerror("Error", f"Could not open Google Sheets: {e}")


# GUI

window = Tk()
window.title('Workout Tracker')
window.config(padx=50, pady=50, bg="yellow")

def submit():
    inp = entry.get()
    entry.delete(0, END)
    track(inp)

label = Label(text="What did you workout today:", background="yellow", padx=10, pady=10)
label.grid(column=1, row=1)

entry = Entry(width=35)
entry.grid(column=1, row=2)

button = Button(text="Submit", command=submit)
button.grid(column=1, row=3, pady=5)

history_button = Button(text="View History", command=view_history)
history_button.grid(column=1, row=4, pady=5)

canvas = Canvas(width=448, height=200, bg="yellow", highlightthickness=0)
image = PhotoImage(file="gym.png")
canvas.create_image(224, 100, image=image)
canvas.grid(column=1, row=0)

window.mainloop()










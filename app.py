import csv
import os


import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

shifts = []

CSV_FILE = "shifts.csv"

def save_shifts():
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["type", "start", "end", "duration"])  # header
        for s in shifts:
            writer.writerow([s["type"], s["start"].strftime("%Y-%m-%d %H:%M"),
                             s["end"].strftime("%Y-%m-%d %H:%M"), s["duration"]])

def load_shifts():
    if not os.path.exists(CSV_FILE):
        return
    with open(CSV_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            shifts.append({
                "type": row["type"],
                "start": datetime.strptime(row["start"], "%Y-%m-%d %H:%M"),
                "end": datetime.strptime(row["end"], "%Y-%m-%d %H:%M"),
                "duration": int(row["duration"])
            })


def add_shift():
    try:
        shift_type = type_var.get()
        start_time = datetime.strptime(start_entry.get(), "%Y-%m-%d %H:%M")
        end_time = datetime.strptime(end_entry.get(), "%Y-%m-%d %H:%M")
        duration = int((end_time - start_time).seconds / 3600)

        shifts.append({"type": shift_type, "start": start_time, "end": end_time, "duration": duration})
        update_table()
        update_summary()
        save_shifts()


        start_entry.delete(0, tk.END)
        end_entry.delete(0, tk.END)

    except Exception as e:
        messagebox.showerror("Error", "Please use format YYYY-MM-DD HH:MM")

def update_table():
    for row in table.get_children():
        table.delete(row)

    for s in shifts:
        table.insert("", tk.END, values=(s["type"], s["start"].strftime("%Y-%m-%d %H:%M"),
                                         s["end"].strftime("%Y-%m-%d %H:%M"), s["duration"]))

def update_summary():
    work_hours = sum(s["duration"] for s in shifts if s["type"] == "Work")
    study_hours = sum(s["duration"] for s in shifts if s["type"] == "Study")
    summary_label.config(text=f"Total Work Hours: {work_hours} | Total Study Hours: {study_hours}")

# --- GUI Setup ---
root = tk.Tk()
root.title("Shift & Study Planner")
root.geometry("650x400")

frame = tk.Frame(root)
frame.pack(pady=10)

# Type dropdown
type_var = tk.StringVar(value="Work")
type_menu = ttk.Combobox(frame, textvariable=type_var, values=["Work", "Study"])
type_menu.grid(row=0, column=0, padx=5)

# Start + End entries
start_entry = tk.Entry(frame)
start_entry.insert(0, "YYYY-MM-DD HH:MM")
start_entry.grid(row=0, column=1, padx=5)

end_entry = tk.Entry(frame)
end_entry.insert(0, "YYYY-MM-DD HH:MM")
end_entry.grid(row=0, column=2, padx=5)

# Add button
add_button = tk.Button(frame, text="Add Shift", command=add_shift)
add_button.grid(row=0, column=3, padx=5)

# Table
columns = ("Type", "Start", "End", "Duration")
table = ttk.Treeview(root, columns=columns, show="headings", height=10)
for col in columns:
    table.heading(col, text=col)
table.pack(pady=10, fill="x")

# Summary
summary_label = tk.Label(root, text="Total Work Hours: 0 | Total Study Hours: 0")
summary_label.pack(pady=10)

load_shifts()
update_table()
update_summary()


root.mainloop()

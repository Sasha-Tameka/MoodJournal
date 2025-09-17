import tkinter as tk
from tkinter import messagebox, simpledialog, Toplevel, filedialog, ttk
import sqlite3
from datetime import datetime, timedelta
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
from collections import Counter
import numpy as np

#Set style for better plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

# --- Database Setup ---
conn = sqlite3.connect("mood_journal.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS journal (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        mood TEXT,
        entry TEXT
    )
""")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS password (
        id INTEGER PRIMARY KEY,
        pwd TEXT
    )
""")

conn.commit()

# --- Global variables ---
editing_id = None

# --- Password Setup ---
def get_password():
    cursor.execute("SELECT pwd FROM password WHERE id=1")
    result = cursor.fetchone()
    return result[0] if result else None

def set_password(pwd):
    cursor.execute("DELETE FROM password")
    cursor.execute("INSERT INTO password (id, pwd) VALUES (1, ?)" , (pwd,))
    conn.commit()

def prompt_password():
    saved_pwd = get_password()
    if not saved_pwd:
        new_pwd = simpledialog.askstring("Create Password", "Create a password:", show="*")
        if new_pwd:
            set_password(new_pwd)
            messagebox.showinfo("Success", "Password created successfully.")
        else:
            root.destroy()
    else:
        for _ in range(3):
            entered_pwd = simpledialog.askstring("Login", "Enter your password:", show="*")
            if entered_pwd == saved_pwd:
                return
            else:
                messagebox.showerror("Error", "Incorrect password.")
        root.destroy()
        
# Data loading function

def load_data_to_dataframe():
# load journal data into pandas DataFrame
    cursor.execute("SELECT id, date, mood, entry FROM joournal ORDER BY date")
    data = cursor.fetchall()
    
    if not data:
        return pd.DataFrame()
    
    df = pd.DataFrame(data, columns=["id", "date", "mood", "entry"])
    df["date"] = pd.to_datetime(df["date"])
    df['entry_length'] = df['entry'].str.len()
    df['mood_clean'] = df['mood'].str.replace(r'[^\w\s]', '', regex=True.str.strip())
    df['day_of_week'] = df['date'].dt.day_name()
    df['month'] = df['date'].dt.month_name()
    df['week'] = df['date'].dt.to_period('W')
    return df


# --- Save Entry ---
def save_entry():
    global editing_id
    date = datetime.now().strftime("%Y-%m-%d")
    mood = mood_var.get()
    entry = journal_box.get("1.0", tk.END).strip()

    if not mood or not entry:
        messagebox.showwarning("Input Error", "Please select a mood and write something.")
        return

    if editing_id:
        cursor.execute("UPDATE journal SET mood=?, entry=? WHERE id=?", (mood, entry, editing_id))
        messagebox.showinfo("Updated", "Your entry was updated.")
        editing_id = None
    else:
        cursor.execute("INSERT INTO journal (date, mood, entry) VALUES (?, ?, ?)", (date, mood, entry))
        messagebox.showinfo("Saved", "Your mood entry was saved!")

    conn.commit()
    journal_box.delete("1.0", tk.END)
    mood_var.set("")

def edit_entry(entry_id, mood, text):
    global editing_id
    editing_id = entry_id
    mood_var.set(mood)
    journal_box.delete("1.0", tk.END)
    journal_box.insert(tk.END, text)
    root.lift()

def delete_entry(entry_id):
    if messagebox.askyesno("Delete", "Are you sure you want to delete this entry?"):
        cursor.execute("DELETE FROM journal WHERE id=?", (entry_id,))
        conn.commit()
        show_entries()

def show_entries():
    view_win = Toplevel(root)
    view_win.title("Previous Entries")
    view_win.geometry("360x500")  
    view_win.configure(bg="#f0f4f8")

    canvas = tk.Canvas(view_win, bg="#f0f4f8", highlightthickness=0)
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = tk.Scrollbar(view_win, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    canvas.configure(yscrollcommand=scrollbar.set)
    frame = tk.Frame(canvas, bg="#f0f4f8")
    canvas.create_window((0, 0), window=frame, anchor="nw")

    def on_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    frame.bind("<Configure>", on_configure)

    cursor.execute("SELECT id, date, mood, entry FROM journal ORDER BY id DESC")
    results = cursor.fetchall()

    for entry_id, date, mood, entry in results:
        card = tk.Frame(frame, bg="white", bd=1, relief="raised", padx=10, pady=5)
        card.pack(fill="x", padx=5, pady=5)

        tk.Label(card, text=f"{date} - {mood}", font=("Helvetica", 12, "bold"), bg="white").pack(anchor="w")
        tk.Label(card, text=entry, wraplength=280, justify="left", font=("Helvetica", 11), bg="white").pack(anchor="w", pady=(0, 5))

        button_row = tk.Frame(card, bg="white")
        button_row.pack(anchor="e")

        tk.Button(button_row, text="✏️ Edit", command=lambda e=entry_id, m=mood, t=entry: edit_entry(e, m, t),
                  font=("Helvetica", 10), bg="#4CAF50", fg="white", padx=5).pack(side="left", padx=2)
        tk.Button(button_row, text="🗑️ Delete", command=lambda e=entry_id: delete_entry(e),
                  font=("Helvetica", 10), bg="#f44336", fg="white", padx=5).pack(side="left", padx=2)

#Analytics Dashboard
def create_analytics_dashboard():
    df = load_data_to_dataframe()
    
    if df.empty:
        messagebox.showinfo("No Data", "No journal entries found for analysis.")
        return

    #Analytics window
    analytics_window = tk.Toplevel(root)
    analytics_window.title("Mood Analytics Dashboard")
    analytics_window.geometry("1000x700")
    analytics_window.configure(bg="#f0f4f8")
    
    #Notebook for tabs
    notebook = ttk.Notebook(analytics_window)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)
    
    #Tab 1: Summary statistics
    create_summary_tab(notebook, df)
    
    #Tab 2: Mood Trends
    create_trends_tab(notebook, df)
    
    #Tab 3: Pattern Detection
    create_patterns_tab(notebook, df)
    
# --- GUI Setup ---
root = tk.Tk()
root.withdraw()
prompt_password()
root.deiconify()

bg_color = "#f0f4f8"
primary_color = "#4a90e2"
accent_color = "#50e3c2"
font_family = "Helvetica"

root.title("Mood Journal")
root.geometry("360x640")
root.configure(bg=bg_color)
root.resizable(False, False)

header = tk.Frame(root, bg=primary_color, height=80)
header.pack(fill="x")
tk.Label(header, text="Mood Journal", font=(font_family, 20, "bold"), bg=primary_color, fg="white").pack(pady=20)

def change_password():
    old_pwd = simpledialog.askstring("Change Password", "Enter current password:", show="*")
    if old_pwd != get_password():
        messagebox.showerror("Error", "Incorrect current password.")
        return
    new_pwd = simpledialog.askstring("New Password", "Enter new password:", show="*")
    if new_pwd:
        set_password(new_pwd)
        messagebox.showinfo("Success", "Password changed successfully.")

button_frame = tk.Frame(root, bg=bg_color)
button_frame.pack(pady=10)

view_btn = tk.Button(button_frame, text="📖 View Entries", command=show_entries,
                     font=(font_family, 11), bg=accent_color, fg="black", padx=10, pady=5)
view_btn.grid(row=0, column=0, padx=10)

pwd_btn = tk.Button(button_frame, text="🔒 Change Password", command=change_password,
                    font=(font_family, 11), bg=accent_color, fg="black", padx=10, pady=5)
pwd_btn.grid(row=0, column=1, padx=10)

main = tk.Frame(root, bg=bg_color)
main.pack(padx=20, pady=10, fill="both", expand=False)

tk.Label(main, text="How are you feeling today?", font=(font_family, 14), bg=bg_color, fg="#333").pack(anchor="w", pady=(0, 10))

moods = ["😊 Happy", "😠 Angry", "😢 Sad", "🤩 Excited", "😌 Relaxed", "😫 Stressed"]
mood_var = tk.StringVar()

for mood in moods:
    tk.Radiobutton(main, text=mood, variable=mood_var, value=mood,
                   font=(font_family, 12), bg=bg_color, anchor="w", indicatoron=0,
                   width=25, pady=5, fg="#444", selectcolor=accent_color).pack(pady=2)

tk.Label(main, text="Journal Entry:", font=(font_family, 14, "bold"), bg=bg_color, fg="#333").pack(anchor="w", pady=(20, 5))
journal_box = tk.Text(main, height=4, width=35, font=(font_family, 11), wrap="word", bd=2, relief="groove")
journal_box.pack()

tk.Button(main, text="Save Entry", command=save_entry, font=(font_family, 13, "bold"),
          bg=primary_color, fg="white", padx=10, pady=5).pack(pady=10)

root.mainloop()

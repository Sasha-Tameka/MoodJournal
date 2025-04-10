import tkinter as tk
from datetime import datetime 
import sqlite3

def say_hello():
    label.config(text="Hello, Tkinter!")

# Create the main window
root = tk.Tk()
root.title("Mood Journal App")
root.geometry("800x600")

def create_db():
# Connect to the database
    conn = sqlite3.connect("mood_journal.db")
    cursor = conn.cursor()

#Create table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS journal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            mood TEXT,
            entry TEXT
        )
    """)

    #Commit changes to the database
    conn.commit()   

    #Close the database connection
    conn.close()

#Run to create the database
create_db()

#Function to save date, mood, and entry to the database
def save_entry():
    date = date_entry.get()
    mood = feeling_var.get()
    entry = journal_box.get("1.0", "end-1c")
    
    if not date or not mood or not entry:
        print("Please fill in all fields.")
        return

    try:
        # Connect to the database
        conn = sqlite3.connect("mood_journal.db")
        cursor = conn.cursor()

        # Make sure the table exists (or create it if not)
        cursor.execute('''CREATE TABLE IF NOT EXISTS journal (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            date TEXT,
                            mood TEXT,
                            entry TEXT
                        )''')

        # Insert data into the journal table
        cursor.execute("INSERT INTO journal (date, mood, entry) VALUES (?, ?, ?)", (date, mood, entry))

        # Commit changes
        conn.commit()

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the connection
        conn.close()


      


# Format YYYY-MM-DD
current_date = datetime.now().strftime("%Y-%m-%d")

# Date label
date_label = tk.Label(root, text="Date: ", font=("Arial", 12, "bold"))
date_label.grid(row=0, column=0, pady=10, sticky="w")

# Date entry
date_entry = tk.Entry(root, font=("Arial", 12))
date_entry.insert(0, current_date)
date_entry.grid(row=0, column=1, pady=10)

# Question label
feeling_label = tk.Label(root, text="How are you feeling today?", font=("Arial", 24))
feeling_label.grid(row=1, column=0, columnspan=2, pady=10)

# Feeling list
feelings = ["Happy", "Angry", "Sad", "Excited", "Relaxed", "Stressed"]

# Journal label
journal_label = tk.Label(root, text="Journal Entry:", font=("Arial", 12, "bold"))
journal_label.grid(row=2, column=0, pady=10, sticky="w")

# Journal Entry
journal_box = tk.Text(root, height=5, width=30, font=("Arial", 12))
journal_box.grid(row=3, column=0, columnspan=2, pady=10)

# Function to get text from textbox
def get_text():
    text = journal_box.get("1.0", "end-1c")
    print(text)

# Function to handle feeling selection
def show_response(feeling):
    result_label.config(text=f"You selected: {feeling}")

# Create a frame for the buttons and add them to the grid
for idx, item in enumerate(feelings):
    btn = tk.Button(root, text=item, command=lambda feeling=item: show_response(feeling))
    btn.grid(row=4 + idx, column=0, pady=5, sticky="w")  # Place each button in a new row

# Create a label to display the selected feeling
result_label = tk.Label(root, text="", font=("Arial", 16))
result_label.grid(row=10, column=0, columnspan=2, pady=10)

# Add the "Enter Mood" button
button = tk.Button(root, text="Enter Mood", command=say_hello)
button.grid(row=11, column=0, columnspan=2, pady=10)

# Add a label for feedback
label = tk.Label(root, text="")
label.grid(row=12, column=0, columnspan=2)

# Run the app
root.mainloop()

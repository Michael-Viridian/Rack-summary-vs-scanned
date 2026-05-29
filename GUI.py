# =============================================================================
# Module imports
# =============================================================================

import customtkinter as ctk
from tkcalendar import DateEntry
from tkinter import filedialog, messagebox

# =============================================================================
# Function imports
# =============================================================================

from CompareReports import run_compare

# =============================================================================
# Main function
# =============================================================================

class FileFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.button = ctk.CTkButton(self, text="Select File", command=self.open_file)
        self.button.pack(pady=20)
        self.label = ctk.CTkLabel(self, text="No file selected")
        self.label.pack(pady=10)

    def open_file(self):
        self.file_path = filedialog.askopenfilename()
        if self.file_path:
            self.label.configure(text=self.file_path)

class RadiobuttonFrame(ctk.CTkFrame):
    def __init__(self, master, title, values):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.values = values
        self.title = title
        self.radiobuttons = []
        self.variable = ctk.StringVar(value="")

        self.title = ctk.CTkLabel(self, text=self.title, fg_color="gray30", corner_radius=6)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")

        for i, value in enumerate(self.values):
            radiobutton = ctk.CTkRadioButton(self, text=value, value=value, variable=self.variable)
            radiobutton.grid(row=i + 1, column=0, padx=10, pady=(10, 0), sticky="w")
            self.radiobuttons.append(radiobutton)

    def get(self):
        return self.variable.get()

    def set(self, value):
        self.variable.set(value)

class DateFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.label = ctk.CTkLabel(self, text="Select a date")
        self.label.pack(pady=10)

        # tkcalendar widget (works fine inside customtkinter)
        self.date_entry = DateEntry(self)
        self.date_entry.pack(pady=10)

    def get_date(self):
        return self.date_entry.get_date()


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Rack summaries vs Scanned")
        self.geometry("400x180")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.File_frame = FileFrame(self)
        self.File_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsw")

        self.Date_frame = DateFrame(self)
        self.Date_frame.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="nsw")

        self.radiobutton_frame = RadiobuttonFrame(self, "Delivery Location", values=["Local", "OOT"])
        self.radiobutton_frame.grid(row=2, column=0, padx=(0, 10), pady=(10, 0), sticky="nsew")

        self.button = ctk.CTkButton(self, text="Run rack summaries vs scanned report", \
            command=self.button_callback)
        self.button.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        

    def button_callback(self):
        filename = run_compare(scanned_file_path=self.File_frame.file_path, \
            target_date=self.Date_frame.get_date(), delivery_location=self.radiobutton_frame.get())
        
        messagebox.showinfo(
            "Success",
            f"Rack Summaries vs Scanned Glass Comparison Report Generated:\n{filename}"
        )

app = App()
app.mainloop()
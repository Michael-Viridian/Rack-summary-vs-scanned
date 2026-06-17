# =============================================================================
# Module imports
# =============================================================================

import tkinter as tk
from tkcalendar import DateEntry
from tkinter import filedialog, messagebox, ttk

# =============================================================================
# Function imports
# =============================================================================

def do_nothing():
    pass

def green_outline_button(parent, text, command=do_nothing):
    btn = tk.Button(
        parent,
        text=text,
        command=command,
        bg="white",
        fg=GREEN,
        activeforeground="white",
        font=("Segoe UI", 11, "bold"),
        relief="solid",
        borderwidth=2,
        highlightthickness=0,
        cursor="hand2"
    )

    # Hover effects
    btn.bind("<Enter>", lambda e: btn.config(
        bg=GREEN,
        fg="white",
        activebackground=GREEN_HOVER
    ))

    btn.bind("<Leave>", lambda e: btn.config(
        bg="white",
        fg=GREEN,
        activebackground=GREEN
    ))

    return btn

def calendar_box(parent):
    return DateEntry(
        parent,
        width=14,
        font=("Segoe UI", 10),
        background="white",
        foreground="black",
        borderwidth=1,
        date_pattern="dd/mm/yyyy"  # ✅ ISO format
    )

def center_window(window):
    window.update_idletasks()
    w = window.winfo_width()
    h = window.winfo_height()
    x = (window.winfo_screenwidth() - w) // 2
    y = (window.winfo_screenheight() - h) // 2
    window.geometry(f"{w}x{h}+{x}+{y}")

# =============================================================================
# Constants
# =============================================================================

GREEN = "#2ecc71"
GREEN_HOVER = "#27ae60"
WHITE = "#ffffff"
WHITE_HOVER = "#ecf0f1"

# =============================================================================
# Main function
# =============================================================================

class TitleFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)

        self.label = tk.Label(
            self, 
            text="Rack Summaries vs Scanned Glass", 
            font=("Font", 30),
            anchor="center"
        )
        self.label.grid(row=0, column=0, sticky="nsew", pady=(20, 20))

class SubTitleFrame(tk.Frame):
    def __init__(self, master, text):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)

        self.label = tk.Label(
            self, 
            text=text, 
            font=("Font", 16, "bold"),
            anchor="center"
        )
        self.label.grid(row=0, column=0, sticky="nsew", pady=(10, 10))

class FileFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)

        self.border_frame = tk.Frame(self)
        self.border_frame.grid(row=0, column=0, pady=6, sticky="nsew")

        self.border_frame.grid_columnconfigure(0, weight=1)

        self.button = green_outline_button(
            self.border_frame,
            text="Select File",
            command=self.open_file
        )
        self.button.grid(row=0, column=0, sticky="nsew")
        self.label = tk.Label(self, text="No file selected")
        self.label.grid(row=1, column=0, sticky="nsew")

    def open_file(self):
        self.file_path = filedialog.askopenfilename()
        if self.file_path:
            self.label.configure(text=self.file_path)

class FolderFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)

        self.border_frame = tk.Frame(self)
        self.border_frame.grid(row=0, column=0, pady=6, sticky="nsew")

        self.border_frame.grid_columnconfigure(0, weight=1)

        self.button = green_outline_button(
            self.border_frame,
            text="Select Folder",
            command=self.open_folder
        )
        self.button.grid(row=0, column=0, sticky="nsew")
        self.label = tk.Label(self, text="No folder selected")
        self.label.grid(row=1, column=0, sticky="nsew")

    def open_folder(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            self.label.configure(text=self.folder_path)

class DateFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)

        self.label = tk.Label(self, text="Select Date:", font=("Segoe UI", 9, "bold"))
        self.label.grid(row=0, column=0, sticky="nsew", pady=(0, 6))

        self.date_entry = calendar_box(
            self,
        )
        self.date_entry.grid(row=1, column=0, sticky="nsew", pady=(0, 6))

    def get_date(self):
        return self.date_entry.entry.get()

class RadiobuttonFrame(tk.Frame):
    def __init__(self, master, title, values):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)

        self.values = values
        self.title = title
        self.radiobuttons = []
        self.variable = tk.StringVar(value="")

        self.title_label = tk.Label(self, text=self.title)
        self.title_label.grid(row=0, column=0, sticky="nsew", pady=(0, 6))

        for i, value in enumerate(self.values, start=1):
            radiobutton = tk.Radiobutton(
                self,
                text=value,
                value=value,
                variable=self.variable,
            )
            radiobutton.grid(row=i, column=0, sticky="nsew", pady=5)
            self.radiobuttons.append(radiobutton)

    def get(self):
        return self.variable.get()
    
    def set(self, value):
        self.variable.set(value)

class DropdownFrame(tk.Frame):
    def __init__(self, master, data=None):
        super().__init__(master)

        self.dropdowns = []
        self.data = data
        self.label = tk.Label(self, text="Select Run (s):", font=("Segoe UI", 9, "bold"))
        self.label.grid(row=0, column=0, sticky="nsew", pady=(0, 6))

        self.create_dropdown()

    def create_dropdown(self):
        
        selected_values = [dropdown.get() for dropdown in self.dropdowns]

        if "All" in selected_values:
            return
        
        remaining = [
            opt for opt in self.data if opt not in selected_values
        ]

        if len(self.dropdowns) > 0:
            remaining = [opt for opt in remaining if opt != "All"]

        if not remaining:
            return

        combobox = ttk.Combobox(self, values=remaining, state="readonly")
        combobox.grid(row=len(self.dropdowns) + 1, column=0, sticky="nsew", pady=(0, 6))

        combobox.bind("<<ComboboxSelected>>", lambda e, c=combobox: self.on_selection(c))

        self.dropdowns.append(combobox)

    def on_selection(self, combobox):
        index = self.dropdowns.index(combobox)
        for dropdown in self.dropdowns[index+1:]:
            dropdown.destroy()
        self.dropdowns = self.dropdowns[:index+1]

        selected_value = combobox.get()

        if selected_value == "All": 
            return
        
        self.create_dropdown()

    def set_values(self, values):
        self.data = values

        for dropdown in self.dropdowns:
            dropdown.destroy()

        self.dropdowns = []

        self.create_dropdown()

    def get_selected(self):
        return [dropdown.get() for dropdown in self.dropdowns]
    
class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Rack summaries vs Scanned")
        self.geometry("1280x720")
        
        self.grid_columnconfigure(0, weight=16)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=16)

        self.grid_rowconfigure(0, weight=3)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=3)

        container = tk.Frame(self)
        container.grid(row=1, column=1, sticky="nsew")
        container.grid_columnconfigure(0, weight=1)
        
        title_frame = TitleFrame(container)
        title_frame.grid(row=0, column=0, sticky="nsew", pady=6)

        self.Scanned_Subtitle_frame = SubTitleFrame(container, "Select Scanned Glass Report")
        self.Scanned_Subtitle_frame.grid(row=1, column=0, sticky="nsew", pady=6)

        self.Folder_frame = FolderFrame(container)
        self.Folder_frame.grid(row=2, column=0, sticky="nsew")

        self.Scanned_File_frame = FileFrame(container)
        self.Scanned_File_frame.grid(row=3, column=0, sticky="nsew", pady=6)

        self.Date_frame = DateFrame(container)
        self.Date_frame.grid(row=4, column=0, sticky="nsew", pady=6)

        # self.radiobutton_frame = RadiobuttonFrame(container, "Delivery Location", values=["Local", "OOT", "All"])
        # self.radiobutton_frame.grid(row=5, column=0, sticky="nsew", pady=10)
        # self.radiobutton_frame.variable.trace_add("write", self.update_dropdown)

        self.Dropdown_frame = DropdownFrame(container, data=["All", "8310-Oamaru", "8311-Timaru", "8312-Ashburton", "8327-Chch To Nel Brn", "8329-Chch To Dun Brn"])
        self.Dropdown_frame.grid(row=6, column=0, pady=(3, 6))

        self.button_rack_scanned = green_outline_button(
            container, 
            text="Run rack summaries vs scanned report",
            command=self.rack_scanned_button_callback, 
        )
        self.button_rack_scanned.grid(row=7, column=0, sticky="nsew", pady=(3, 6))

        self.Manifest_Subtitle_frame = SubTitleFrame(container, "Select Manifest Glass Report")
        self.Manifest_Subtitle_frame.grid(row=8, column=0, sticky="nsew", pady=6)

        self.Manifest_File_frame = FileFrame(container)
        self.Manifest_File_frame.grid(row=9, column=0, sticky="nsew", pady=(0, 6))

        self.button_scanned_manifest = green_outline_button(
            container, 
            text="Run scanned discrepancies vs manifest report",
            command=self.scanned_manifest_button_callback
        )
        self.button_scanned_manifest.grid(row=10, column=0, sticky="nsew", pady=6)

        self.button_rack_manifest = green_outline_button(
            container, 
            text="Run rack discrepancies vs manifest report",
            command=self.rack_manifest_button_callback
        )
        self.button_rack_manifest.grid(row=11, column=0, sticky="nsew", pady=6)

    def rack_scanned_button_callback(self):
        try:
            from CompareReports import run_rack_scanned_compare
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import CompareReports: {e}")
            return

        self.rack_scanned_filename = run_rack_scanned_compare(
            rack_folder_path=getattr(self.Folder_frame, 'folder_path', None),
            scanned_file_path=getattr(self.Scanned_File_frame, 'file_path', None),
            # target_date=self.Date_frame.get_date(), 
            # delivery_location=self.radiobutton_frame.get(),
            runs=self.Dropdown_frame.get_selected()
        )
        
        if self.rack_scanned_filename is None:
            messagebox.showerror(
                "Error",
                "Failed to generate comparison report."
            )
        else:
            messagebox.showinfo(
            "Success",
            f"Rack Summaries vs Scanned Glass Comparison Report Generated:\n{self.rack_scanned_filename}"
        )
            
    def scanned_manifest_button_callback(self):
        try:
            from CompareReports import compare_scanned_discrepancy_manifest_reports
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import CompareReports: {e}")
            return
        
        compare_scanned_discrepancy_manifest_reports(
            scanned_discrepancy_file_path=self.rack_scanned_filename,
            manifest_file_path=getattr(self.File_frame_manifest, 'file_path', None)
        )

        messagebox.showinfo("Info", "Check comparison report for manifest status.")

    def rack_manifest_button_callback(self):
        try:
            from CompareReports import compare_rack_discrepancy_manifest_reports
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import CompareReports: {e}")
            return
        
        compare_rack_discrepancy_manifest_reports(
            rack_discrepancy_file_path=self.rack_scanned_filename,
            manifest_file_path=getattr(self.File_frame_manifest, 'file_path', None)
        )

        messagebox.showinfo("Info", "Check comparison report for manifest status.")

    def update_dropdown(self, *args):
        # choice = self.radiobutton_frame.get()

        # if choice == "OOT":
        #     data = ["All", "8310-Oamaru", "8311-Timaru", "8312-Ashburton", "8327-Chch To Nel Brn", "8329-Chch To Dun Brn"]
        # elif choice == "Local":
        #     # data = ["All", "8301: Christchurch 1", "8302: Christchurch 2", "8303: Christchurch 3"]
        #     data = ["All"]
        # elif choice == "All":
        #     data = ["All"]
        # else:
        #     data = ["All"]

        data = ["All", "8310-Oamaru", "8311-Timaru", "8312-Ashburton", "8327-Chch To Nel Brn", "8329-Chch To Dun Brn"]

        self.Dropdown_frame.set_values(data)

app = App()
center_window(app)
app.mainloop()

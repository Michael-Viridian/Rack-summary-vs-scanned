# =============================================================================
# Module imports
# =============================================================================

from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.widgets import DateEntry

# =============================================================================
# Function imports
# =============================================================================

from CompareReports import run_compare

# =============================================================================
# Main function
# =============================================================================

class TitleFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)

        self.label = ttk.Label(
            self, 
            text="Rack Summaries vs Scanned Glass", 
            bootstyle="primary", 
            font=("Helvetica", 16, "bold"),
            anchor="center"
        )
        self.label.grid(row=0, column=0, sticky="ew", pady=(20, 20))

class FileFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)

        self.button = ttk.Button(self, text="Select File", command=self.open_file, bootstyle="primary")
        self.button.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.label = ttk.Label(self, text="No file selected", bootstyle="secondary")
        self.label.grid(row=1, column=0, sticky="ew", pady=(0, 10))

    def open_file(self):
        self.file_path = filedialog.askopenfilename()
        if self.file_path:
            self.label.configure(text=self.file_path)

class DateFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)

        self.label = ttk.Label(self, text="Select Date", bootstyle="secondary")
        self.label.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        self.date_entry = DateEntry(
            self,
            bootstyle="primary",
            dateformat="%Y-%m-%d"   # clean ISO format
        )
        self.date_entry.grid(row=1, column=0, sticky="ew", pady=(0, 10), padx=20)

    def get_date(self):
        return self.date_entry.entry.get()

class RadiobuttonFrame(ttk.Frame):
    def __init__(self, master, title, values):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)

        self.values = values
        self.title = title
        self.radiobuttons = []
        self.variable = ttk.StringVar(value="")

        self.title_label = ttk.Label(self, text=self.title, bootstyle="secondary")
        self.title_label.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        for i, value in enumerate(self.values, start=1):
            radiobutton = ttk.Radiobutton(
                self,
                text=value,
                value=value,
                variable=self.variable,
                bootstyle="info"
            )
            radiobutton.grid(row=i, column=0, sticky="ew", padx=20, pady=5)
            self.radiobuttons.append(radiobutton)

    def get(self):
        return self.variable.get()
    
    def set(self, value):
        self.variable.set(value)

class DropdownFrame(ttk.Frame):
    def __init__(self, master, data=None):
        super().__init__(master)

        self.dropdowns = []
        self.data = data
        self.label = ttk.Label(self, text="Select Run (s)", bootstyle="secondary")
        self.label.grid(row=0, column=0, sticky="ew", pady=(0, 10))

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

        combobox = ttk.Combobox(self, values=remaining, state="readonly", bootstyle="primary")
        combobox.grid(row=len(self.dropdowns) + 1, column=0, sticky="ew", pady=(0, 10))

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
    
class App(ttk.Window):
    def __init__(self):
        super().__init__(themename="flatly")

        self.title("Rack summaries vs Scanned")
        self.geometry("500x300")
        
        self.grid_columnconfigure(0, weight=4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=4)

        self.grid_rowconfigure(0, weight=3)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=3)

        container = ttk.Frame(self, padding=5)
        container.grid(row=1, column=1, sticky="nsew")
        container.grid_columnconfigure(0, weight=1)
        
        title_frame = TitleFrame(container)
        title_frame.grid(row=0, column=0, sticky="ew", pady=10)

        self.File_frame = FileFrame(container)
        self.File_frame.grid(row=1, column=0, sticky="ew", pady=10)

        self.Date_frame = DateFrame(container)
        self.Date_frame.grid(row=2, column=0, sticky="ew", pady=10)

        self.radiobutton_frame = RadiobuttonFrame(container, "Delivery Location", values=["Local", "OOT", "All"])
        self.radiobutton_frame.grid(row=3, column=0, sticky="ew", pady=10)
        self.radiobutton_frame.variable.trace_add("write", self.update_dropdown)

        self.Dropdown_frame = DropdownFrame(container, data=["All"])
        self.Dropdown_frame.grid(row=4, column=0, sticky="ew", pady=10)

        self.button = ttk.Button(
            container, 
            text="Run rack summaries vs scanned report",
            command=self.button_callback, 
            bootstyle="success"
        )
        self.button.grid(row=5, column=0, sticky="ew", pady=(10, 0))

    def button_callback(self):
        filename = run_compare(
            scanned_file_path=self.File_frame.file_path,
            target_date=self.Date_frame.get_date(), 
            delivery_location=self.radiobutton_frame.get(),
            runs=self.Dropdown_frame.dropdowns
        )
        
        messagebox.showinfo(
            "Success",
            f"Rack Summaries vs Scanned Glass Comparison Report Generated:\n{filename}"
        )

    def update_dropdown(self, *args):
        choice = self.radiobutton_frame.get()

        if choice == "OOT":
            data = ["All", "8327: Nelson", "8329: Dunedin"]
        elif choice == "Local":
            data = ["All", "8327: Nelson", "8329: Dunedin"]
        elif choice == "All":
            data = ["All"]
        else:
            data = ["All"]

        self.Dropdown_frame.set_values(data)

app = App()
app.mainloop()
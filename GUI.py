# =============================================================================
# Module imports
# =============================================================================

from tkinter import filedialog, messagebox, Toplevel
import ttkbootstrap as ttk
from ttkbootstrap.widgets import DateEntry

# =============================================================================
# Function imports
# =============================================================================

# Defer importing the potentially heavy `CompareReports` module until the
# report is run. This keeps static analysis (PyInstaller) from pulling in
# large dependencies unnecessarily when building the GUI-only exe.

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
            bootstyle="bg", 
            font=("Helvetica", 16, "bold"),
            anchor="center"
        )
        self.label.grid(row=0, column=0, sticky="ew", pady=(20, 20))

class SubTitleFrame(ttk.Frame):
    def __init__(self, master, text):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)

        self.label = ttk.Label(
            self, 
            text=text, 
            bootstyle="bg", 
            font=("Helvetica", 12, "bold"),
            anchor="center"
        )
        self.label.grid(row=0, column=0, sticky="ew", pady=(10, 10))

class FileFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)

        self.border_frame = ttk.Frame(self, bootstyle="secondary", padding=2)
        self.border_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.border_frame.grid_columnconfigure(0, weight=1)

        self.button = ttk.Button(
            self.border_frame,
            text="Select File",
            command=self.open_file,
            bootstyle="success-outline"
        )
        self.button.grid(row=0, column=0, sticky="ew")
        self.label = ttk.Label(self, text="No file selected", bootstyle="bg")
        self.label.grid(row=1, column=0, sticky="ew", pady=(0, 10))

    def open_file(self):
        self.file_path = filedialog.askopenfilename()
        if self.file_path:
            self.label.configure(text=self.file_path)

class FolderFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)

        self.border_frame = ttk.Frame(self, bootstyle="secondary", padding=2)
        self.border_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.border_frame.grid_columnconfigure(0, weight=1)

        self.button = ttk.Button(
            self.border_frame,
            text="Select Folder",
            command=self.open_folder,
            bootstyle="success-outline"
        )
        self.button.grid(row=0, column=0, sticky="ew")
        self.label = ttk.Label(self, text="No folder selected", bootstyle="bg")
        self.label.grid(row=1, column=0, sticky="ew", pady=(0, 10))

    def open_folder(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            self.label.configure(text=self.folder_path)

class DateFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)

        self.label = ttk.Label(self, text="Select Date", bootstyle="bg")
        self.label.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        self.date_entry = DateEntry(
            self,
            bootstyle="success",
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

        self.title_label = ttk.Label(self, text=self.title, bootstyle="bg")
        self.title_label.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        for i, value in enumerate(self.values, start=1):
            radiobutton = ttk.Radiobutton(
                self,
                text=value,
                value=value,
                variable=self.variable,
                bootstyle="bg"
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
        self.label = ttk.Label(self, text="Select Run (s)", bootstyle="bg")
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

        combobox = ttk.Combobox(self, values=remaining, state="readonly", bootstyle="success")
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

    def get_selected(self):
        return [dropdown.get() for dropdown in self.dropdowns]
    
class App(ttk.Window):
    def __init__(self):
        super().__init__(themename="lumen")

        self.title("Rack summaries vs Scanned")
        self.geometry("1440x1024")
        
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

        self.Scanned_Subtitle_frame = SubTitleFrame(container, "Select Scanned Glass Report")
        self.Scanned_Subtitle_frame.grid(row=1, column=0, sticky="ew", pady=10)

        self.Folder_frame = FolderFrame(container)
        self.Folder_frame.grid(row=2, column=0, sticky="ew", pady=10)

        self.Scanned_File_frame = FileFrame(container)
        self.Scanned_File_frame.grid(row=3, column=0, sticky="ew", pady=10)

        # self.Date_frame = DateFrame(container)
        # self.Date_frame.grid(row=4, column=0, sticky="ew", pady=10)

        # self.radiobutton_frame = RadiobuttonFrame(container, "Delivery Location", values=["Local", "OOT", "All"])
        # self.radiobutton_frame.grid(row=5, column=0, sticky="ew", pady=10)
        # self.radiobutton_frame.variable.trace_add("write", self.update_dropdown)

        self.Dropdown_frame = DropdownFrame(container, data=["All", "8310-Oamaru", "8311-Timaru", "8312-Ashburton", "8327-Chch To Nel Brn", "8329-Chch To Dun Brn"])
        self.Dropdown_frame.grid(row=6, column=0, sticky="ew", pady=10)

        self.button_rack_scanned = ttk.Button(
            container, 
            text="Run rack summaries vs scanned report",
            command=self.rack_scanned_button_callback, 
            bootstyle="success"
        )
        self.button_rack_scanned.grid(row=7, column=0, sticky="ew", pady=(10, 0))

        self.Manifest_Subtitle_frame = SubTitleFrame(container, "Select Manifest Glass Report")
        self.Manifest_Subtitle_frame.grid(row=8, column=0, sticky="ew", pady=10)

        self.Manifest_File_frame = FileFrame(container)
        self.Manifest_File_frame.grid(row=9, column=0, sticky="ew", pady=10)

        self.button_scanned_manifest = ttk.Button(
            container, 
            text="Run scanned discrepancies vs manifest report",
            command=self.scanned_manifest_button_callback, 
            bootstyle="success"
        )
        self.button_scanned_manifest.grid(row=10, column=0, sticky="ew", pady=(10, 0))

        self.button_rack_manifest = ttk.Button(
            container, 
            text="Run rack discrepancies vs manifest report",
            command=self.rack_manifest_button_callback, 
            bootstyle="success"
        )
        self.button_rack_manifest.grid(row=11, column=0, sticky="ew", pady=(10, 0))

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
app.mainloop()

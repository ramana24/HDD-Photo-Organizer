
import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
from PIL import Image, ExifTags
from datetime import datetime, timezone
import threading
import json
import sys
import traceback

class PhotoOrganizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Photo Organizer Pro - 10 Years Collection Manager")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')

        # Initialize variables
        self.source_folder = ""
        self.destination_folder = ""
        self.is_processing = False
        self.processed_count = 0
        self.total_files = 0

        # Create GUI elements
        self.create_widgets()

    def create_widgets(self):
        # Title Frame
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        title_frame.pack(fill='x', padx=5, pady=5)
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame, text="Photo Organizer Pro", 
                              font=("Arial", 24, "bold"), fg='white', bg='#2c3e50')
        title_label.pack(pady=20)

        subtitle_label = tk.Label(title_frame, text="Organize 10 years of memories with ease", 
                                 font=("Arial", 12), fg='#ecf0f1', bg='#2c3e50')
        subtitle_label.pack()

        # Main content frame
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Folder selection frame
        folder_frame = tk.LabelFrame(main_frame, text="Folder Selection", 
                                    font=("Arial", 12, "bold"), bg='#f0f0f0', fg='#2c3e50')
        folder_frame.pack(fill='x', pady=5)

        # Source folder selection
        source_frame = tk.Frame(folder_frame, bg='#f0f0f0')
        source_frame.pack(fill='x', padx=10, pady=5)

        tk.Label(source_frame, text="Source Folder (Photos):", 
                font=("Arial", 10, "bold"), bg='#f0f0f0').pack(anchor='w')

        source_select_frame = tk.Frame(source_frame, bg='#f0f0f0')
        source_select_frame.pack(fill='x', pady=2)

        self.source_label = tk.Label(source_select_frame, text="No folder selected", 
                                    bg='white', relief='sunken', anchor='w')
        self.source_label.pack(side='left', fill='x', expand=True, padx=(0, 5))

        tk.Button(source_select_frame, text="Browse", command=self.select_source_folder,
                 bg='#3498db', fg='white', font=("Arial", 9, "bold")).pack(side='right')

        # Destination folder selection
        dest_frame = tk.Frame(folder_frame, bg='#f0f0f0')
        dest_frame.pack(fill='x', padx=10, pady=5)

        tk.Label(dest_frame, text="Destination Folder (Organized):", 
                font=("Arial", 10, "bold"), bg='#f0f0f0').pack(anchor='w')

        dest_select_frame = tk.Frame(dest_frame, bg='#f0f0f0')
        dest_select_frame.pack(fill='x', pady=2)

        self.dest_label = tk.Label(dest_select_frame, text="No folder selected", 
                                  bg='white', relief='sunken', anchor='w')
        self.dest_label.pack(side='left', fill='x', expand=True, padx=(0, 5))

        tk.Button(dest_select_frame, text="Browse", command=self.select_dest_folder,
                 bg='#3498db', fg='white', font=("Arial", 9, "bold")).pack(side='right')

        # Options frame
        options_frame = tk.LabelFrame(main_frame, text="Organization Options", 
                                     font=("Arial", 12, "bold"), bg='#f0f0f0', fg='#2c3e50')
        options_frame.pack(fill='x', pady=5)

        options_inner = tk.Frame(options_frame, bg='#f0f0f0')
        options_inner.pack(fill='x', padx=10, pady=5)

        # Organization structure
        self.structure_var = tk.StringVar(value="year_month")
        tk.Label(options_inner, text="Folder Structure:", 
                font=("Arial", 10, "bold"), bg='#f0f0f0').pack(anchor='w')

        structure_frame = tk.Frame(options_inner, bg='#f0f0f0')
        structure_frame.pack(fill='x', pady=2)

        tk.Radiobutton(structure_frame, text="Year/Month (2023/01-January)", 
                      variable=self.structure_var, value="year_month", bg='#f0f0f0').pack(anchor='w')
        tk.Radiobutton(structure_frame, text="Year Only (2023)", 
                      variable=self.structure_var, value="year_only", bg='#f0f0f0').pack(anchor='w')
        tk.Radiobutton(structure_frame, text="Year/Month/Day (2023/01-January/15)", 
                      variable=self.structure_var, value="year_month_day", bg='#f0f0f0').pack(anchor='w')

        # Copy or move options
        self.operation_var = tk.StringVar(value="copy")
        tk.Label(options_inner, text="Operation:", 
                font=("Arial", 10, "bold"), bg='#f0f0f0').pack(anchor='w', pady=(10, 0))

        operation_frame = tk.Frame(options_inner, bg='#f0f0f0')
        operation_frame.pack(fill='x', pady=2)

        tk.Radiobutton(operation_frame, text="Copy files (Keep originals)", 
                      variable=self.operation_var, value="copy", bg='#f0f0f0').pack(anchor='w')
        tk.Radiobutton(operation_frame, text="Move files (Remove from source)", 
                      variable=self.operation_var, value="move", bg='#f0f0f0').pack(anchor='w')

        # Duplicate handling
        self.duplicate_var = tk.StringVar(value="skip")
        tk.Label(options_inner, text="Handle Duplicates:", 
                font=("Arial", 10, "bold"), bg='#f0f0f0').pack(anchor='w', pady=(10, 0))

        duplicate_frame = tk.Frame(options_inner, bg='#f0f0f0')
        duplicate_frame.pack(fill='x', pady=2)

        tk.Radiobutton(duplicate_frame, text="Skip duplicates", 
                      variable=self.duplicate_var, value="skip", bg='#f0f0f0').pack(anchor='w')
        tk.Radiobutton(duplicate_frame, text="Rename duplicates", 
                      variable=self.duplicate_var, value="rename", bg='#f0f0f0').pack(anchor='w')
        tk.Radiobutton(duplicate_frame, text="Overwrite existing", 
                      variable=self.duplicate_var, value="overwrite", bg='#f0f0f0').pack(anchor='w')

        # Control buttons frame
        control_frame = tk.Frame(main_frame, bg='#f0f0f0')
        control_frame.pack(fill='x', pady=10)

        # Start button
        self.start_button = tk.Button(control_frame, text="Start Organization", 
                                     command=self.start_organization, bg='#27ae60', 
                                     fg='white', font=("Arial", 12, "bold"), height=2)
        self.start_button.pack(side='left', padx=(0, 10), fill='x', expand=True)

        # Stop button
        self.stop_button = tk.Button(control_frame, text="Stop", 
                                    command=self.stop_organization, bg='#e74c3c', 
                                    fg='white', font=("Arial", 12, "bold"), height=2, state='disabled')
        self.stop_button.pack(side='left', padx=(0, 10), fill='x', expand=True)

        # Preview button
        self.preview_button = tk.Button(control_frame, text="Preview Structure", 
                                       command=self.preview_structure, bg='#f39c12', 
                                       fg='white', font=("Arial", 12, "bold"), height=2)
        self.preview_button.pack(side='left', fill='x', expand=True)

        # Progress frame
        progress_frame = tk.LabelFrame(main_frame, text="Progress", 
                                      font=("Arial", 12, "bold"), bg='#f0f0f0', fg='#2c3e50')
        progress_frame.pack(fill='both', expand=True, pady=5)

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100, length=300)
        self.progress_bar.pack(padx=10, pady=5, fill='x')

        # Status label
        self.status_label = tk.Label(progress_frame, text="Ready to organize photos", 
                                    bg='#f0f0f0', font=("Arial", 10))
        self.status_label.pack(pady=5)

        # Log text area
        self.log_text = scrolledtext.ScrolledText(progress_frame, height=8, 
                                                 font=("Courier", 9))
        self.log_text.pack(padx=10, pady=5, fill='both', expand=True)

        self.log("Photo Organizer Pro initialized successfully!")
        self.log("Select source and destination folders to begin.")

    def select_source_folder(self):
        folder = filedialog.askdirectory(title="Select source folder containing photos")
        if folder:
            self.source_folder = folder
            self.source_label.config(text=folder)
            self.log(f"Source folder selected: {folder}")
            self.count_files()

    def select_dest_folder(self):
        folder = filedialog.askdirectory(title="Select destination folder for organized photos")
        if folder:
            self.destination_folder = folder
            self.dest_label.config(text=folder)
            self.log(f"Destination folder selected: {folder}")

    def count_files(self):
        if not self.source_folder:
            return

        count = 0
        for root, dirs, files in os.walk(self.source_folder):
            for file in files:
                if self.is_image_file(file):
                    count += 1

        self.total_files = count
        self.log(f"Found {count} image files in source folder")

    def is_image_file(self, filename):
        """Check if file is an image based on extension"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', 
                           '.gif', '.webp', '.raw', '.cr2', '.nef', '.arw', 
                           '.dng', '.orf', '.rw2', '.pef', '.srw'}
        return os.path.splitext(filename.lower())[1] in image_extensions

    def get_image_date(self, file_path):
        """Extract date from image EXIF data or file modification time"""
        try:
            # Try to get date from EXIF
            with Image.open(file_path) as img:
                exif = img._getexif()
                if exif:
                    for tag, value in exif.items():
                        tag_name = ExifTags.TAGS.get(tag, tag)
                        if tag_name in ['DateTime', 'DateTimeOriginal', 'DateTimeDigitized']:
                            return datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
        except Exception:
            pass

        # Fallback to file modification time
        try:
            timestamp = os.path.getmtime(file_path)
            return datetime.fromtimestamp(timestamp)
        except Exception:
            return datetime.now()

    def get_destination_path(self, date_obj, original_filename):
        """Generate destination path based on selected structure"""
        year = date_obj.strftime('%Y')
        month_num = date_obj.strftime('%m')
        month_name = date_obj.strftime('%B')
        day = date_obj.strftime('%d')

        structure = self.structure_var.get()

        if structure == "year_only":
            dest_dir = os.path.join(self.destination_folder, year)
        elif structure == "year_month":
            dest_dir = os.path.join(self.destination_folder, year, f"{month_num}-{month_name}")
        else:  # year_month_day
            dest_dir = os.path.join(self.destination_folder, year, f"{month_num}-{month_name}", day)

        return os.path.join(dest_dir, original_filename)

    def handle_duplicate(self, dest_path):
        """Handle duplicate files based on selected option"""
        if not os.path.exists(dest_path):
            return dest_path

        duplicate_option = self.duplicate_var.get()

        if duplicate_option == "skip":
            return None
        elif duplicate_option == "overwrite":
            return dest_path
        else:  # rename
            base, ext = os.path.splitext(dest_path)
            counter = 1
            while os.path.exists(f"{base}_{counter}{ext}"):
                counter += 1
            return f"{base}_{counter}{ext}"

    def organize_photos(self):
        """Main organization function"""
        if not self.source_folder or not self.destination_folder:
            messagebox.showerror("Error", "Please select both source and destination folders")
            return

        self.is_processing = True
        self.processed_count = 0
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')

        try:
            operation = self.operation_var.get()

            for root, dirs, files in os.walk(self.source_folder):
                if not self.is_processing:
                    break

                for file in files:
                    if not self.is_processing:
                        break

                    if not self.is_image_file(file):
                        continue

                    source_path = os.path.join(root, file)

                    try:
                        # Get image date
                        date_obj = self.get_image_date(source_path)

                        # Get destination path
                        dest_path = self.get_destination_path(date_obj, file)

                        # Handle duplicates
                        final_dest_path = self.handle_duplicate(dest_path)
                        if final_dest_path is None:
                            self.log(f"Skipped duplicate: {file}")
                            continue

                        # Create destination directory
                        os.makedirs(os.path.dirname(final_dest_path), exist_ok=True)

                        # Copy or move file
                        if operation == "copy":
                            shutil.copy2(source_path, final_dest_path)
                            self.log(f"Copied: {file} → {os.path.relpath(final_dest_path, self.destination_folder)}")
                        else:
                            shutil.move(source_path, final_dest_path)
                            self.log(f"Moved: {file} → {os.path.relpath(final_dest_path, self.destination_folder)}")

                        self.processed_count += 1
                        progress = (self.processed_count / max(self.total_files, 1)) * 100
                        self.progress_var.set(progress)
                        self.status_label.config(text=f"Processed {self.processed_count} of {self.total_files} files")

                        # Update GUI
                        self.root.update_idletasks()

                    except Exception as e:
                        self.log(f"Error processing {file}: {str(e)}")

            if self.is_processing:
                self.log(f"\nOrganization completed! Processed {self.processed_count} files.")
                messagebox.showinfo("Success", f"Photo organization completed!\n\nProcessed {self.processed_count} files.")
            else:
                self.log("\nOrganization stopped by user.")

        except Exception as e:
            self.log(f"Error during organization: {str(e)}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

        finally:
            self.is_processing = False
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
            self.progress_var.set(0)
            self.status_label.config(text="Ready for next operation")

    def start_organization(self):
        """Start organization in a separate thread"""
        if not self.source_folder or not self.destination_folder:
            messagebox.showerror("Error", "Please select both source and destination folders")
            return

        # Confirm operation
        operation = "copy" if self.operation_var.get() == "copy" else "move"
        structure = self.structure_var.get().replace("_", " ").title()

        message = f"Ready to {operation} {self.total_files} photos\nStructure: {structure}\n\nContinue?"

        if messagebox.askyesno("Confirm Operation", message):
            thread = threading.Thread(target=self.organize_photos)
            thread.daemon = True
            thread.start()

    def stop_organization(self):
        """Stop the organization process"""
        self.is_processing = False
        self.log("Stopping organization...")

    def preview_structure(self):
        """Show preview of folder structure that will be created"""
        if not self.source_folder:
            messagebox.showerror("Error", "Please select source folder first")
            return

        # Sample dates for preview
        sample_dates = [
            datetime(2023, 1, 15),
            datetime(2023, 6, 20),
            datetime(2022, 12, 25),
            datetime(2021, 8, 10),
        ]

        structure = self.structure_var.get()
        preview_text = "Folder structure preview:\n\n"

        for date_obj in sample_dates:
            sample_path = self.get_destination_path(date_obj, "sample_photo.jpg")
            relative_path = os.path.relpath(sample_path, self.destination_folder)
            preview_text += f"  {os.path.dirname(relative_path)}/\n"

        preview_text += f"\nTotal estimated folders: Varies based on photo dates\n"
        preview_text += f"Selected structure: {structure.replace('_', ' ').title()}"

        messagebox.showinfo("Structure Preview", preview_text)

    def log(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)

def main():
    root = tk.Tk()
    app = PhotoOrganizer(root)
    root.mainloop()

if __name__ == "__main__":
    main()

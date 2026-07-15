import os
import threading
from pathlib import Path
from PIL import Image
import pillow_avif
import customtkinter as ctk
from tkinter import filedialog, messagebox

# Appearance Settings
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class AvifConverterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AVIF Ultra Converter")
        self.geometry("600x450")

        # UI Elements
        self.label = ctk.CTkLabel(self, text="AVIF Ultra Converter", font=("Helvetica", 20, "bold"))
        self.label.pack(pady=20)

        # Source Folder
        self.src_frame = ctk.CTkFrame(self)
        self.src_frame.pack(fill="x", padx=20, pady=5)
        self.src_label = ctk.CTkLabel(self.src_frame, text="Source Folder:")
        self.src_label.pack(side="left", padx=10)
        self.src_entry = ctk.CTkEntry(self.src_frame, width=300)
        self.src_entry.pack(side="left", padx=10, expand=True, fill="x")
        self.src_btn = ctk.CTkButton(self.src_frame, text="Browse", width=80, command=self.browse_src)
        self.src_btn.pack(side="right", padx=10)

        # Destination Folder
        self.dst_frame = ctk.CTkFrame(self)
        self.dst_frame.pack(fill="x", padx=20, pady=5)
        self.dst_label = ctk.CTkLabel(self.dst_frame, text="Save Folder:  ")
        self.dst_label.pack(side="left", padx=10)
        self.dst_entry = ctk.CTkEntry(self.dst_frame, width=300)
        self.dst_entry.pack(side="left", padx=10, expand=True, fill="x")
        self.dst_btn = ctk.CTkButton(self.dst_frame, text="Browse", width=80, command=self.browse_dst)
        self.dst_btn.pack(side="right", padx=10)

        # Quality Slider
        self.quality_label = ctk.CTkLabel(self, text="Quality (93 is recommended):")
        self.quality_label.pack(pady=(10, 0))
        self.quality_slider = ctk.CTkSlider(self, from_=50, to=100, number_of_steps=50)
        self.quality_slider.set(93)
        self.quality_slider.pack(pady=5)

        # Progress Bar
        self.progress = ctk.CTkProgressBar(self, width=400)
        self.progress.set(0)
        self.progress.pack(pady=20)

        # Convert Button
        self.convert_btn = ctk.CTkButton(self, text="Start Conversion", font=("Helvetica", 16, "bold"), height=40, command=self.start_conversion_thread)
        self.convert_btn.pack(pady=10)

        # Log Output
        self.log = ctk.CTkTextbox(self, height=100)
        self.log.pack(fill="both", padx=20, pady=10)

    def browse_src(self):
        folder = filedialog.askdirectory()
        self.src_entry.delete(0, 'end')
        self.src_entry.insert(0, folder)

    def browse_dst(self):
        folder = filedialog.askdirectory()
        self.dst_entry.delete(0, 'end')
        self.dst_entry.insert(0, folder)

    def log_message(self, message):
        self.log.insert("end", message + "\n")
        self.log.see("end")

    def start_conversion_thread(self):
        # Run conversion in a background thread so the UI doesn't freeze
        thread = threading.Thread(target=self.run_conversion)
        thread.start()

    def run_conversion(self):
        src = self.src_entry.get()
        dst = self.dst_entry.get()
        quality = int(self.quality_slider.get())

        if not src or not dst:
            messagebox.showerror("Error", "Please select both source and destination folders.")
            return

        src_path = Path(src)
        dst_path = Path(dst)
        extensions = {'.png', '.webp', '.jpg', '.jpeg', '.bmp', '.tiff'}
        
        # Get list of files
        files = [f for f in src_path.rglob('*') if f.suffix.lower() in extensions]
        
        if not files:
            self.log_message("No images found in the source folder.")
            return

        self.convert_btn.configure(state="disabled")
        total_files = len(files)

        for i, file_path in enumerate(files):
            try:
                relative_path = file_path.relative_to(src_path)
                output_file_path = dst_path.joinpath(relative_path).with_suffix('.avif')
                output_file_path.parent.mkdir(parents=True, exist_ok=True)

                with Image.open(file_path) as img:
                    exif_data = img.info.get("exif")
                    img.save(output_file_path, "AVIF", quality=quality, speed=6, exif=exif_data)

                self.log_message(f"Converted: {file_path.name}")
            except Exception as e:
                self.log_message(f"Error {file_path.name}: {str(e)}")
            
            # Update progress bar
            self.progress.set((i + 1) / total_files)
        
        self.convert_btn.configure(state="normal")
        messagebox.showinfo("Success", "All images converted successfully!")

if __name__ == "__main__":
    app = AvifConverterApp()
    app.mainloop()
    

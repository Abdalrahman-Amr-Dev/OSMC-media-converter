import threading
from pathlib import Path
from PIL import Image
import customtkinter as ctk
from tkinter import filedialog, messagebox

# Appearance Settings
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class OSMC(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("OSMC - Image Converter")
        self.geometry("600x550")

        # UI Elements
        self.label = ctk.CTkLabel(self, text="OSMC", font=("Helvetica", 28, "bold"))
        self.label.pack(pady=(20, 5))
        


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

        # Format Selection
        self.format_frame = ctk.CTkFrame(self)
        self.format_frame.pack(fill="x", padx=20, pady=5)
        self.format_label = ctk.CTkLabel(self.format_frame, text="Output Format:")
        self.format_label.pack(side="left", padx=10)
        self.format_option = ctk.CTkOptionMenu(self.format_frame, values=["AVIF", "WebP", "JPEG", "PNG"])
        self.format_option.set("AVIF")
        self.format_option.pack(side="left", padx=10)

        # Quality Slider
        self.quality_label = ctk.CTkLabel(self, text="Quality (10-100):")
        self.quality_label.pack(pady=(10, 0))
        self.quality_slider = ctk.CTkSlider(self, from_=10, to=100, number_of_steps=90)
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
        self.log = ctk.CTkTextbox(self, height=120)
        self.log.pack(fill="both", padx=20, pady=10)

    def browse_src(self):
        folder = filedialog.askdirectory()
        if folder:
            self.src_entry.delete(0, 'end')
            self.src_entry.insert(0, folder)

    def browse_dst(self):
        folder = filedialog.askdirectory()
        if folder:
            self.dst_entry.delete(0, 'end')
            self.dst_entry.insert(0, folder)

    def log_message(self, message):
        self.log.insert("end", message + "\n")
        self.log.see("end")

    def start_conversion_thread(self):
        thread = threading.Thread(target=self.run_conversion, daemon=True)
        thread.start()

    def run_conversion(self):
        src = self.src_entry.get()
        dst = self.dst_entry.get()
        quality = int(self.quality_slider.get())
        selected_format = self.format_option.get()

        format_settings = {
            "AVIF": {"ext": ".avif", "pil": "AVIF"},
            "WebP": {"ext": ".webp", "pil": "WEBP"},
            "JPEG": {"ext": ".jpg",  "pil": "JPEG"},
            "PNG":  {"ext": ".png",  "pil": "PNG"}
        }
        
        target_ext = format_settings[selected_format]["ext"]
        target_pil = format_settings[selected_format]["pil"]

        if not src or not dst:
            messagebox.showerror("Error", "Please select both source and destination folders.")
            return

        src_path = Path(src)
        dst_path = Path(dst)
        input_extensions = {'.png', '.webp', '.jpg', '.jpeg', '.bmp', '.tiff', '.avif'}
        
        files = [f for f in src_path.rglob('*') if f.suffix.lower() in input_extensions]
        
        if not files:
            self.log_message("No supported images found.")
            return

        self.convert_btn.configure(state="disabled")
        self.progress.set(0)
        
        total_files = len(files)

        for i, file_path in enumerate(files):
            try:
                relative_path = file_path.relative_to(src_path)
                output_file_path = dst_path.joinpath(relative_path).with_suffix(target_ext)
                output_file_path.parent.mkdir(parents=True, exist_ok=True)

                with Image.open(file_path) as img:
                    # Fix for JPEG/AVIF non-transparency support
                    if target_pil in ["JPEG", "AVIF"] and img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")
                    
                    # Prepare arguments
                    save_kwargs = {"format": target_pil}
                    
                    # ONLY add exif if it actually exists to avoid 'NoneType' error
                    exif_data = img.info.get("exif")
                    if exif_data is not None:
                        save_kwargs["exif"] = exif_data
                    
                    if target_pil != "PNG":
                        save_kwargs["quality"] = quality
                    
                    if target_pil == "AVIF":
                        save_kwargs["speed"] = 6

                    img.save(output_file_path, **save_kwargs)

                self.log_message(f"Success: {file_path.name}")
            except Exception as e:
                self.log_message(f"Failed {file_path.name}: {str(e)}")
            
            self.progress.set((i + 1) / total_files)
        
        self.convert_btn.configure(state="normal")
        messagebox.showinfo("OSMC", f"Finished! All images converted to {selected_format}.")

if __name__ == "__main__":
    app = OSMC()
    app.mainloop()
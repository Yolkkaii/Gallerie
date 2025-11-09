import customtkinter as ctk
from pathlib import Path
from Widgets import *
from Menu import *
from PIL import Image, ImageTk, ImageOps, ImageEnhance, ImageFilter
import os
import subprocess
import sys

# Enable HEIC support
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
    HEIC_SUPPORT = True
except ImportError:
    HEIC_SUPPORT = False
    print("Warning: pillow-heif not installed. HEIC files will not be supported.")

class Gallerie(ctk.CTk):
    def __init__(self):
        #Initial setup
        super().__init__()
        ctk.set_appearance_mode("dark")
        self.geometry('1000x600')
        self.title("Gallerie")
        self.minsize(800, 500)
        
        # Photos directory - Set this FIRST before anything else
        self.photos_dir = Path(__file__).resolve().parent / "photos"
        self.photos_dir.mkdir(exist_ok=True)
        
        self.init_parameters()


        #Program layout
        self.rowconfigure(0, weight = 1)
        self.columnconfigure(0, weight = 2, uniform = 'a')
        self.columnconfigure(1, weight = 6, uniform = 'a')

        #Canvas data
        self.image_width = 0
        self.image_height = 0
        self.canvas_width = 0
        self.canvas_height = 0

        # Create and pack the menu
        self.main_menu = MainMenu(
            master=self,
            on_import=self.handle_import,
            on_edit=self.handle_edit,
            on_gallery=self.handle_gallery,
            on_exit=self.handle_exit
        )

        #Run program
        self.mainloop()

    def init_parameters(self):
        self.pos_vars = {
            'rotate': ctk.DoubleVar(value = ROTATE_DEFAULT),
            'zoom': ctk.DoubleVar(value = ZOOM_DEFAULT),
            'flip': ctk.StringVar(value = FLIP_OPT[0])
        }
        self.color_vars = {
            'brightness': ctk.DoubleVar(value = BRIGHTNESS_DEFAULT),
            'grayscale': ctk.BooleanVar(value=GRAYSCALE_DEFAULT),
            'invert': ctk.BooleanVar(value=INVERT_DEFAULT),
            'vibrance': ctk.DoubleVar(value = VIBRANCE_DEFAULT)
        }
        self.effect_vars = {
            'blur': ctk.DoubleVar(value = BLUR_DEFAULT),
            'contrast': ctk.IntVar(value= CONTRAST_DEFAULT),
            'effect': ctk.StringVar(value= EFFECT_OPT[0])
        }

        #Tracing
        combined_vars = list(self.pos_vars.values()) + list(self.color_vars.values()) + list(self.effect_vars.values())
        
        for var in combined_vars:
            var.trace('w', self.manipulate_image)

    def manipulate_image(self, *args):
        self.image = self.original

        #Rotate
        if self.pos_vars['rotate'].get() != ROTATE_DEFAULT:
            self.image = self.image.rotate(self.pos_vars['rotate'].get())

        #Zoom
        if self.pos_vars['zoom'].get() != ZOOM_DEFAULT:
            self.image = ImageOps.crop(image = self.image, border= self.pos_vars['zoom'].get())

        #Flip
        if self.pos_vars['flip'].get() != FLIP_OPT[0]:
            if self.pos_vars['flip'].get() == 'X':
                self.image = ImageOps.mirror(self.image)
            if self.pos_vars['flip'].get() == 'Y':
                self.image = ImageOps.flip(self.image)
            if self.pos_vars['flip'].get() == 'Both':
                self.image = ImageOps.mirror(self.image)
                self.image = ImageOps.flip(self.image)

        #Brightness / Vibrance
        if self.color_vars['brightness'].get() != BRIGHTNESS_DEFAULT:
            brightness_enhancer = ImageEnhance.Brightness(self.image)
            self.image = brightness_enhancer.enhance(self.color_vars['brightness'].get())

        if self.color_vars['vibrance'].get() != VIBRANCE_DEFAULT:
            vibrance_enhancer = ImageEnhance.Color(self.image)
            self.image = vibrance_enhancer.enhance(self.color_vars['vibrance'].get())

        #Color
        if self.color_vars['grayscale'].get():
            self.image = ImageOps.grayscale(self.image)
        if self.color_vars['invert'].get():
            self.image = ImageOps.invert(self.image)

        #Blur & Contrast
        if self.effect_vars['blur'].get() != BLUR_DEFAULT:
            self.image = self.image.filter(ImageFilter.GaussianBlur(self.effect_vars['blur'].get()))

        if self.effect_vars['contrast'].get() != CONTRAST_DEFAULT:
            self.image = self.image.filter(ImageFilter.UnsharpMask(self.effect_vars['contrast'].get()))

        match self.effect_vars['effect'].get():
            case 'Emboss': self.image = self.image.filter(ImageFilter.EMBOSS)
            case 'Find edges': self.image = self.image.filter(ImageFilter.FIND_EDGES)
            case 'Contour': self.image = self.image.filter(ImageFilter.CONTOUR)
            case 'Edge enhance': self.image = self.image.filter(ImageFilter.EDGE_ENHANCE_MORE)

        self.place_image()

    def handle_import(self, path):
        self.original = Image.open(path)
        # Convert RGBA to RGB if necessary
        if self.original.mode == 'RGBA':
            rgb_image = Image.new('RGB', self.original.size, (255, 255, 255))
            rgb_image.paste(self.original, mask=self.original.split()[3])
            self.original = rgb_image
        
        self.image = self.original
        self.image_ratio = self.image.size[0] / self.image.size[1]
        self.image_tk = ImageTk.PhotoImage(self.image)

        # Reset all parameters to default values
        self.reset_parameters()

        self.main_menu.grid_forget()
        self.image_output = Import_Page(self, self.resize_image)
        self.close_button = CloseButton(self, self.close_edit)
        self.menu = Menu(self, self.pos_vars, self.color_vars, self.effect_vars, self.export_image)

    def reset_parameters(self):
        """Reset all editing parameters to their default values"""
        # Reset position variables
        self.pos_vars['rotate'].set(ROTATE_DEFAULT)
        self.pos_vars['zoom'].set(ZOOM_DEFAULT)
        self.pos_vars['flip'].set(FLIP_OPT[0])
        
        # Reset color variables
        self.color_vars['brightness'].set(BRIGHTNESS_DEFAULT)
        self.color_vars['grayscale'].set(GRAYSCALE_DEFAULT)
        self.color_vars['invert'].set(INVERT_DEFAULT)
        self.color_vars['vibrance'].set(VIBRANCE_DEFAULT)
        
        # Reset effect variables
        self.effect_vars['blur'].set(BLUR_DEFAULT)
        self.effect_vars['contrast'].set(CONTRAST_DEFAULT)
        self.effect_vars['effect'].set(EFFECT_OPT[0])

    def close_edit(self):
        self.image_output.grid_forget()
        self.close_button.place_forget()
        self.menu.grid_forget()

        self.main_menu = MainMenu(
            master=self,
            on_import=self.handle_import,
            on_edit=self.handle_edit,
            on_gallery=self.handle_gallery,
            on_exit=self.handle_exit
        )

    def resize_image(self, event):
        #Current canvas ratio
        canvas_ratio = event.width / event.height

        #Update canvas sizes
        self.canvas_width = event.width
        self.canvas_height = event.height
        
        #Resize
        if canvas_ratio > self.image_ratio:
            self.image_height = int(event.height)
            self.image_width = int(self.image_height * self.image_ratio)
        else:
            self.image_width = int(event.width)
            self.image_height = int(self.image_width  / self.image_ratio)

        self.place_image()

    def place_image(self):
        self.image_output.delete('all')
        resized_image = self.image.resize((self.image_width, self.image_height))
        self.image_tk = ImageTk.PhotoImage(resized_image)
        self.image_output.create_image(self.canvas_width / 2, self.canvas_height / 2, image = self.image_tk)

    def export_image(self, name, file):
        export_string = f'{self.photos_dir}/{name}.{file}'
        # Convert RGBA to RGB for JPEG export
        if file.lower() in ['jpg', 'jpeg'] and self.image.mode == 'RGBA':
            rgb_image = Image.new('RGB', self.image.size, (255, 255, 255))
            rgb_image.paste(self.image, mask=self.image.split()[3])
            rgb_image.save(export_string)
        else:
            self.image.save(export_string)
        self.close_edit()

    def handle_edit(self):
        """Open the photo management page"""
        self.main_menu.grid_forget()
        self.photo_manager = PhotoManager(self, self.photos_dir, self.return_to_menu, self.edit_photo)

    def handle_gallery(self):
        """Open the Pinterest-style gallery"""
        self.main_menu.grid_forget()
        self.gallery_view = GalleryView(self, self.photos_dir, self.return_to_menu)

    def return_to_menu(self):
        """Return to main menu from any view"""
        # Remove all possible views
        for widget in self.winfo_children():
            widget.grid_forget()
            widget.place_forget()
        
        # Recreate main menu
        self.main_menu = MainMenu(
            master=self,
            on_import=self.handle_import,
            on_edit=self.handle_edit,
            on_gallery=self.handle_gallery,
            on_exit=self.handle_exit
        )

    def edit_photo(self, photo_path):
        """Open a photo for editing"""
        self.handle_import(photo_path)

    def handle_exit(self):
        self.destroy()


class PhotoManager(ctk.CTkFrame):
    """Photo management page with preview and full view"""
    def __init__(self, master, photos_dir, return_callback, edit_callback):
        super().__init__(master)
        self.grid(row=0, column=0, columnspan=2, sticky='nsew')
        self.photos_dir = photos_dir
        self.return_callback = return_callback
        self.edit_callback = edit_callback
        self.selected_photo = None
        # No need for photo_refs with CTkImage

        # Configure layout
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)

        # Header with back button
        header = ctk.CTkFrame(self, fg_color='transparent')
        header.grid(row=0, column=0, columnspan=2, sticky='ew', padx=10, pady=10)
        
        back_btn = ctk.CTkButton(header, text="← Back", command=self.return_callback, width=100)
        back_btn.pack(side='left')
        
        title = ctk.CTkLabel(header, text="Manage Photos", font=("Arial", 24, "bold"))
        title.pack(side='left', padx=20)

        # Left side - Thumbnail grid
        self.thumbnail_frame = ctk.CTkScrollableFrame(self, fg_color=DARK_GREY)
        self.thumbnail_frame.grid(row=1, column=0, sticky='nsew', padx=(10, 5), pady=10)

        # Right side - Full preview and actions (scrollable)
        self.preview_frame = ctk.CTkScrollableFrame(self, fg_color=DARK_GREY)
        self.preview_frame.grid(row=1, column=1, sticky='nsew', padx=(5, 10), pady=10)
        
        self.preview_label = ctk.CTkLabel(self.preview_frame, text="Select a photo to view", 
                                          font=("Arial", 16))
        self.preview_label.pack(expand=True, pady=50)

        # Load photos
        self.load_thumbnails()

    def load_thumbnails(self):
        """Load all photos as thumbnails"""
        # No need for photo_refs list anymore with CTkImage
        
        # Clear existing thumbnails
        for widget in self.thumbnail_frame.winfo_children():
            widget.destroy()

        # Get all image files
        image_files = []
        extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp']
        if HEIC_SUPPORT:
            extensions.extend(['*.heic', '*.HEIC'])
        
        for ext in extensions:
            image_files.extend(self.photos_dir.glob(ext))

        if not image_files:
            no_photos = ctk.CTkLabel(self.thumbnail_frame, text="No photos found", 
                                     font=("Arial", 14))
            no_photos.pack(pady=20)
            return

        # Create thumbnail grid
        row, col = 0, 0
        max_cols = 3

        for img_path in image_files:
            try:
                # Load and resize thumbnail
                img = Image.open(img_path)
                img.thumbnail((150, 150))
                
                # Use CTkImage for better scaling on HighDPI displays
                ctk_photo = ctk.CTkImage(light_image=img, dark_image=img, size=(150, 150))

                # Create thumbnail button
                btn_frame = ctk.CTkFrame(self.thumbnail_frame, fg_color='transparent')
                btn_frame.grid(row=row, column=col, padx=5, pady=5)

                btn = ctk.CTkButton(btn_frame, image=ctk_photo, text="", 
                                   width=150, height=150,
                                   command=lambda p=img_path: self.show_full_image(p))
                btn.pack()

                # Photo name label
                name_label = ctk.CTkLabel(btn_frame, text=img_path.name, 
                                         font=("Arial", 10))
                name_label.pack()

                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1

            except Exception as e:
                print(f"Error loading {img_path}: {e}")

    def show_full_image(self, photo_path):
        """Display full image with action buttons"""
        self.selected_photo = photo_path

        # Clear preview frame
        for widget in self.preview_frame.winfo_children():
            widget.destroy()

        try:
            # Load full image
            img = Image.open(photo_path)
            
            # Resize to fit preview area while maintaining aspect ratio
            max_size = (600, 400)
            img.thumbnail(max_size)
            
            # Use CTkImage for better scaling
            ctk_photo = ctk.CTkImage(light_image=img, dark_image=img, 
                                     size=(img.width, img.height))

            # Display image
            img_label = ctk.CTkLabel(self.preview_frame, image=ctk_photo, text="")
            img_label.pack(pady=20)

            # Photo info
            info_text = f"Name: {photo_path.name}\nSize: {photo_path.stat().st_size / 1024:.1f} KB"
            info_label = ctk.CTkLabel(self.preview_frame, text=info_text, font=("Arial", 12))
            info_label.pack(pady=10)

            # Action buttons
            btn_frame = ctk.CTkFrame(self.preview_frame, fg_color='transparent')
            btn_frame.pack(pady=20)

            edit_btn = ctk.CTkButton(btn_frame, text="Edit", width=120, height=40,
                                    command=lambda: self.edit_callback(str(photo_path)))
            edit_btn.grid(row=0, column=0, padx=10)

            open_btn = ctk.CTkButton(btn_frame, text="Open File", width=120, height=40,
                                    command=lambda: self.open_file(photo_path))
            open_btn.grid(row=0, column=1, padx=10)

            delete_btn = ctk.CTkButton(btn_frame, text="Delete", width=120, height=40,
                                      fg_color="#c0392b", hover_color="#e74c3c",
                                      command=lambda: self.delete_photo(photo_path))
            delete_btn.grid(row=0, column=2, padx=10)

        except Exception as e:
            error_label = ctk.CTkLabel(self.preview_frame, 
                                      text=f"Error loading image: {str(e)}", 
                                      font=("Arial", 14))
            error_label.pack(expand=True)

    def open_file(self, photo_path):
        """Open the image file in the default system viewer"""
        try:
            if sys.platform == 'win32':
                os.startfile(photo_path)
            elif sys.platform == 'darwin':
                subprocess.run(['open', photo_path])
            else:
                subprocess.run(['xdg-open', photo_path])
        except Exception as e:
            print(f"Error opening file: {e}")

    def delete_photo(self, photo_path):
        """Delete the selected photo"""
        # Confirm deletion
        confirm_window = ctk.CTkToplevel(self)
        confirm_window.title("Confirm Delete")
        confirm_window.geometry("300x150")
        confirm_window.transient(self)
        confirm_window.grab_set()

        label = ctk.CTkLabel(confirm_window, text=f"Delete {photo_path.name}?", 
                            font=("Arial", 14))
        label.pack(pady=20)

        btn_frame = ctk.CTkFrame(confirm_window, fg_color='transparent')
        btn_frame.pack(pady=10)

        def confirm_delete():
            try:
                photo_path.unlink()
                confirm_window.destroy()
                self.load_thumbnails()
                
                # Clear preview
                for widget in self.preview_frame.winfo_children():
                    widget.destroy()
                self.preview_label = ctk.CTkLabel(self.preview_frame, 
                                                 text="Photo deleted\nSelect another photo", 
                                                 font=("Arial", 16))
                self.preview_label.pack(expand=True)
            except Exception as e:
                print(f"Error deleting file: {e}")

        yes_btn = ctk.CTkButton(btn_frame, text="Yes", width=100,
                               fg_color="#c0392b", hover_color="#e74c3c",
                               command=confirm_delete)
        yes_btn.pack(side='left', padx=10)

        no_btn = ctk.CTkButton(btn_frame, text="No", width=100,
                              command=confirm_window.destroy)
        no_btn.pack(side='left', padx=10)


class GalleryView(ctk.CTkFrame):
    """Pinterest-style gallery view"""
    def __init__(self, master, photos_dir, return_callback):
        super().__init__(master)
        self.grid(row=0, column=0, columnspan=2, sticky='nsew')
        self.photos_dir = photos_dir
        self.return_callback = return_callback
        # No need for photo_refs with CTkImage

        # Configure layout
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color='transparent')
        header.grid(row=0, column=0, sticky='ew', padx=10, pady=10)
        
        back_btn = ctk.CTkButton(header, text="← Back", command=self.return_callback, width=100)
        back_btn.pack(side='left')
        
        title = ctk.CTkLabel(header, text="Gallery", font=("Arial", 24, "bold"))
        title.pack(side='left', padx=20)

        # Scrollable gallery frame
        self.gallery_frame = ctk.CTkScrollableFrame(self, fg_color=BACKGROUND_COLOR)
        self.gallery_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=10)

        # Load gallery
        self.load_gallery()

    def load_gallery(self):
        """Load photos in a Pinterest-style masonry layout"""
        # No need for photo_refs list anymore with CTkImage

        # Get all image files
        image_files = []
        extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp']
        if HEIC_SUPPORT:
            extensions.extend(['*.heic', '*.HEIC'])
        
        for ext in extensions:
            image_files.extend(self.photos_dir.glob(ext))

        if not image_files:
            no_photos = ctk.CTkLabel(self.gallery_frame, text="No photos in gallery", 
                                     font=("Arial", 16))
            no_photos.pack(pady=50)
            return

        # Create columns for masonry layout
        num_columns = 4
        columns = [ctk.CTkFrame(self.gallery_frame, fg_color='transparent') 
                   for _ in range(num_columns)]
        
        for i, col in enumerate(columns):
            col.grid(row=0, column=i, sticky='nsew', padx=5)
            self.gallery_frame.columnconfigure(i, weight=1, uniform='gallery')

        # Distribute images across columns
        for idx, img_path in enumerate(image_files):
            try:
                # Load image
                img = Image.open(img_path)
                
                # Calculate thumbnail size while maintaining aspect ratio
                base_width = 220
                w_percent = base_width / float(img.size[0])
                h_size = int(float(img.size[1]) * w_percent)
                img = img.resize((base_width, h_size), Image.Resampling.LANCZOS)
                
                # Use CTkImage for better scaling
                ctk_photo = ctk.CTkImage(light_image=img, dark_image=img, 
                                         size=(base_width, h_size))

                # Determine which column to add to (round-robin)
                col_idx = idx % num_columns

                # Create card
                card = ctk.CTkFrame(columns[col_idx], fg_color=DARK_GREY, corner_radius=10)
                card.pack(pady=8, fill='x')

                # Image button
                btn = ctk.CTkButton(card, image=ctk_photo, text="", 
                                   fg_color='transparent', hover_color=GREY,
                                   command=lambda p=img_path: self.open_fullscreen(p))
                btn.pack(padx=5, pady=5)

                # Photo name
                name_label = ctk.CTkLabel(card, text=img_path.stem, 
                                         font=("Arial", 11, "bold"))
                name_label.pack(padx=10, pady=(0, 10))

            except Exception as e:
                print(f"Error loading {img_path}: {e}")

    def open_fullscreen(self, photo_path):
        """Open photo in fullscreen view"""
        fullscreen_window = ctk.CTkToplevel(self)
        fullscreen_window.title(photo_path.name)
        fullscreen_window.geometry("800x600")
        fullscreen_window.configure(fg_color=BACKGROUND_COLOR)

        try:
            img = Image.open(photo_path)
            
            # Resize to fit window
            max_size = (750, 550)
            img.thumbnail(max_size)
            photo = ImageTk.PhotoImage(img)

            label = ctk.CTkLabel(fullscreen_window, image=photo, text="")
            label.image = photo  # Keep reference
            label.pack(expand=True, pady=20)

            close_btn = ctk.CTkButton(fullscreen_window, text="Close", 
                                     command=fullscreen_window.destroy)
            close_btn.pack(pady=10)

        except Exception as e:
            error_label = ctk.CTkLabel(fullscreen_window, 
                                      text=f"Error loading image: {str(e)}", 
                                      font=("Arial", 14))
            error_label.pack(expand=True)

Gallerie()

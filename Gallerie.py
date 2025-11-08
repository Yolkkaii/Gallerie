import customtkinter as ctk
from pathlib import Path
from Widgets import *
from Menu import *
from PIL import Image, ImageTk, ImageOps, ImageEnhance, ImageFilter

class Gallerie(ctk.CTk):
    def __init__(self):
        #Initial setup
        super().__init__()
        ctk.set_appearance_mode("dark")
        self.geometry('1000x600')
        self.title("Gallerie")
        self.minsize(800, 500)
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
        self.image = self.original
        self.image_ratio = self.image.size[0] / self.image.size[1]
        self.image_tk = ImageTk.PhotoImage(self.image)

        self.main_menu.grid_forget()
        self.image_output = Import_Page(self, self.resize_image)
        self.close_button = CloseButton(self, self.close_edit)
        self.menu = Menu(self, self.pos_vars, self.color_vars, self.effect_vars, self.export_image)

    def close_edit(self):
        self.image_output.grid_forget()
        self.close_button.place_forget()
        self.menu.grid_forget()

        self.image_import = MainMenu(
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
        directory = Path(__file__).resolve().parent
        image_folder = directory / "photos"
        image_folder.mkdir(exist_ok=True)

        export_string = f'{image_folder}/{name}.{file}'
        self.image.save(export_string)
        self.close_edit()

    def handle_edit(self):
        print("Edit clicked")

    def handle_gallery(self):
        print("Gallery clicked")

    def handle_exit(self):
        self.destroy()

Gallerie()

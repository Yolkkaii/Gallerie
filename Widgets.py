import customtkinter as ctk
from tkinter import filedialog, Canvas
from Settings import *

class MainMenu(ctk.CTkFrame):
    def __init__(self, master, on_import, on_edit, on_gallery, on_exit):
        super().__init__(master)
        self.grid(column = 0, columnspan = 2, row = 0, sticky = 'nsew')
        self.on_import = on_import
        self.on_edit = on_edit
        self.on_gallery = on_gallery
        self.on_exit = on_exit

        # Title
        title_label = ctk.CTkLabel(self, text="Main Menu", font=("Arial", 36))
        title_label.pack(expand = True)

        # Buttons
        import_btn = ctk.CTkButton(self, text="Import", width = 200, height = 50, font=("Arial", 18), command=self.open_dialog)
        import_btn.pack(expand = True)

        edit_btn = ctk.CTkButton(self, text="Edit", width = 200, height = 50, font=("Arial", 18), command=on_edit)
        edit_btn.pack(expand = True)

        gallery_btn = ctk.CTkButton(self, text="Gallery", width = 200, height = 50, font=("Arial", 18), command=on_gallery)
        gallery_btn.pack(expand = True)

        exit_btn = ctk.CTkButton(self, text="Exit", width = 200, height = 50, font=("Arial", 18), fg_color="#c0392b", hover_color="#e74c3c", command=on_exit)
        exit_btn.pack(expand = True)

    def open_dialog(self):
        path = filedialog.askopenfile().name
        self.on_import(path)

    def handle_edit(self):
        print("Edit clicked")

    def handle_gallery(self):
        print("Gallery clicked")

    def handle_exit(self):
        self.destroy()

class Import_Page(Canvas):
    def __init__(self, master, resize_image):
        super().__init__(master, background = BACKGROUND_COLOR, bd = 0, highlightthickness = 0, relief = 'ridge')
        self.grid(row = 0,column = 1, sticky = 'nsew', padx = 10, pady = 10)
        self.bind('<Configure>', resize_image)

class CloseButton(ctk.CTkButton):
    def __init__(self, master, close):
        super().__init__(master, command = close, text = 'x', text_color =  WHITE, fg_color = 'transparent', width = 40, height = 40, hover_color = CLOSE_RED)
        self.place(relx = 0.99, rely = 0.01, anchor = 'ne')
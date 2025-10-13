from tkinter import *
from tkinter import ttk

class Gallerie:
    def __init__(self, root):
        self.root = root
        self.root.title("Photo Gallery Application")
        self.root.geometry("800x600")

        # Define themes
        self.themes = {
            "light": {
                "bg": "#f0f0f0",
                "card": "#ffffff",
                "fg": "black",
                "button_bg": "white",
                "button_fg": "black"
            },
            "dark": {
                "bg": "#1e1e1e",
                "card": "#2a2a2a",
                "fg": "white",
                "button_bg": "#3a3a3a",
                "button_fg": "white"
            }
        }

        # Default theme
        self.current_theme = "light"

        self.container = Frame(root)
        self.container.pack(fill="both", expand=True)

        self.frames = {}

        # 4 main screens
        for F in (HomeScreen, GalleryScreen, PhotoViewerScreen, SettingsScreen):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("HomeScreen")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.update_theme()
        frame.tkraise()

    def set_theme(self, theme_name):
        if theme_name in self.themes:
            self.current_theme = theme_name
            # Update all frames immediately
            for frame in self.frames.values():
                frame.update_theme()

# ------------------------------------------------------ #
# Base Frame with automatic theme update
# ------------------------------------------------------ #
class ThemedFrame(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

    def update_theme(self):
        theme = self.controller.themes[self.controller.current_theme]
        self.configure(bg=theme["bg"])
        for widget in self.winfo_children():
            self.apply_theme(widget, theme)

    def apply_theme(self, widget, theme):
        if isinstance(widget, (Label, Button, Frame)):
            widget.configure(bg=theme.get("bg", "#f0f0f0"), fg=theme.get("fg", "black"))
        if isinstance(widget, Button):
            widget.configure(
                bg=theme["button_bg"],
                fg=theme["button_fg"],
                activebackground="#0078d7",
                activeforeground="white",
                bd=0,
                relief="flat",
                cursor="hand2"
            )

# ------------------------------------------------------ #
# Home Screen
# ------------------------------------------------------ #
class HomeScreen(ThemedFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        Label(self, text="📸 Photo Gallery Application", font=("Arial", 24, "bold")).pack(pady=40)
        Label(self, text="Welcome! Manage your photos easily.\nChoose an option below:", font=("Arial", 12)).pack(pady=10)

        Button(self, text="View Gallery", width=20, height=2,
               command=lambda: controller.show_frame("GalleryScreen")).pack(pady=10)
        Button(self, text="Open Photo Viewer", width=20, height=2,
               command=lambda: controller.show_frame("PhotoViewerScreen")).pack(pady=10)
        Button(self, text="Settings", width=20, height=2,
               command=lambda: controller.show_frame("SettingsScreen")).pack(pady=10)
        Button(self, text="Exit", width=20, height=2,
               command=controller.root.quit).pack(pady=30)


# ------------------------------------------------------ #
# Gallery Screen
# ------------------------------------------------------ #
class GalleryScreen(ThemedFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        Label(self, text="🖼️ Photo Gallery", font=("Arial", 20, "bold")).pack(pady=20)
        Label(self, text="(Gallery grid will be displayed here)", font=("Arial", 12)).pack(pady=50)

        Button(self, text="Back to Home", width=20,
               command=lambda: controller.show_frame("HomeScreen")).pack(pady=10)
        Button(self, text="Open Selected Photo", width=20,
               command=lambda: controller.show_frame("PhotoViewerScreen")).pack(pady=10)


# ------------------------------------------------------ #
# Photo Viewer Screen
# ------------------------------------------------------ #
class PhotoViewerScreen(ThemedFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        Label(self, text="🖼️ Photo Viewer", font=("Arial", 20, "bold")).pack(pady=20)
        Label(self, text="(Selected photo will be displayed here)", font=("Arial", 12)).pack(pady=50)

        Button(self, text="Back to Gallery", width=20,
               command=lambda: controller.show_frame("GalleryScreen")).pack(pady=10)
        Button(self, text="Back to Home", width=20,
               command=lambda: controller.show_frame("HomeScreen")).pack(pady=10)


# ------------------------------------------------------ #
# Settings Screen (Theme Selection)
# ------------------------------------------------------ #
class SettingsScreen(ThemedFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        Label(self, text="⚙️ Settings", font=("Arial", 20, "bold")).pack(pady=30)
        Label(self, text="Choose Theme:", font=("Arial", 12)).pack(pady=10)

        Button(self, text="☀️ Light Mode", width=20, height=2,
               command=lambda: controller.set_theme("light")).pack(pady=10)

        Button(self, text="🌙 Dark Mode", width=20, height=2,
               command=lambda: controller.set_theme("dark")).pack(pady=10)

        Button(self, text="Back to Home", width=20, height=2,
               command=lambda: controller.show_frame("HomeScreen")).pack(pady=30)


# ------------------------------------------------------ #
# Run the App
# ------------------------------------------------------ #
root = Tk()
app = Gallerie(root)
root.mainloop()
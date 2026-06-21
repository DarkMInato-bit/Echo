import customtkinter as ctk

class MainFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Logo/Avatar
        avatar_image = self.controller.get_avatar_image((100, 100))
        if avatar_image:
            self.avatar_label = ctk.CTkLabel(self, image=avatar_image, text="")
            self.avatar_label.pack(pady=40)
        else:
            self.title_label = ctk.CTkLabel(self, text="ECHO", font=("Arial", 36, "bold"))
            self.title_label.pack(pady=40)

        # Welcome Text
        self.welcome_label = ctk.CTkLabel(self, text="Welcome to ECHO", font=("Arial", 20, "bold"))
        self.welcome_label.pack(pady=(0, 20))

        self.tagline_label = ctk.CTkLabel(
            self, 
            text="Your Voice, Analyzed & Archived.", 
            font=("Arial", 14),
            text_color="gray"
        )
        self.tagline_label.pack(pady=(0, 40))

        # Buttons
        self.login_btn = ctk.CTkButton(
            self, 
            text="Login", 
            command=lambda: self.controller.show_frame("LoginFrame"), 
            width=220,
            height=40,
            font=("Arial", 14, "bold")
        )
        self.login_btn.pack(pady=10)

        self.register_btn = ctk.CTkButton(
            self, 
            text="Register", 
            command=lambda: self.controller.show_frame("RegisterFrame"), 
            width=220,
            height=40,
            font=("Arial", 14, "bold")
        )
        self.register_btn.pack(pady=10)

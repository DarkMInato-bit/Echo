import customtkinter as ctk

class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Logo
        avatar_image = self.controller.get_avatar_image((100, 100))
        if avatar_image:
            self.avatar_label = ctk.CTkLabel(self, image=avatar_image, text="")
            self.avatar_label.pack(pady=30)

        self.title_label = ctk.CTkLabel(self, text="Login to ECHO", font=("Arial", 20, "bold"))
        self.title_label.pack(pady=(0, 20))

        # Input Fields
        self.username_entry = ctk.CTkEntry(
            self, 
            width=220, 
            placeholder_text="Username",
            height=35
        )
        self.username_entry.pack(pady=10)

        self.password_entry = ctk.CTkEntry(
            self, 
            width=220, 
            placeholder_text="Password", 
            show="*",
            height=35
        )
        self.password_entry.pack(pady=10)

        # Status Error/Success Label
        self.status_label = ctk.CTkLabel(self, text="", text_color="red", font=("Arial", 12))
        self.status_label.pack(pady=5)

        # Action Buttons
        self.login_btn = ctk.CTkButton(
            self, 
            text="Login", 
            command=self.perform_login, 
            width=220,
            height=40,
            font=("Arial", 14, "bold")
        )
        self.login_btn.pack(pady=10)

        self.back_btn = ctk.CTkButton(
            self, 
            text="Back", 
            command=self.go_back, 
            width=220,
            height=40,
            fg_color="transparent",
            border_width=2,
            text_color=("black", "white"),
            font=("Arial", 14, "bold")
        )
        self.back_btn.pack(pady=10)

    def perform_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            self.status_label.configure(text="All fields are required!", text_color="red")
            return

        self.status_label.configure(text="Logging in...", text_color="orange")
        self.update_idletasks()

        success, result = self.controller.db_module.login_user(username, password)
        if success:
            self.status_label.configure(text="")
            self.controller.set_logged_in_user(username, result)
            self.controller.show_frame("SpeechFrame")
        else:
            self.status_label.configure(text=f"Error: {result}", text_color="red")

    def go_back(self):
        self.status_label.configure(text="")
        self.username_entry.delete(0, 'end')
        self.password_entry.delete(0, 'end')
        self.controller.show_frame("MainFrame")

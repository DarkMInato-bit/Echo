import customtkinter as ctk

class RegisterFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Logo
        avatar_image = self.controller.get_avatar_image((100, 100))
        if avatar_image:
            self.avatar_label = ctk.CTkLabel(self, image=avatar_image, text="")
            self.avatar_label.pack(pady=20)

        self.title_label = ctk.CTkLabel(self, text="Create ECHO Account", font=("Arial", 20, "bold"))
        self.title_label.pack(pady=(0, 15))

        # Inputs
        self.username_entry = ctk.CTkEntry(self, width=220, placeholder_text="Username", height=35)
        self.username_entry.pack(pady=7)

        self.password_entry = ctk.CTkEntry(self, width=220, placeholder_text="Password", show="*", height=35)
        self.password_entry.pack(pady=7)

        self.confirm_password_entry = ctk.CTkEntry(self, width=220, placeholder_text="Confirm Password", show="*", height=35)
        self.confirm_password_entry.pack(pady=7)

        self.contact_entry = ctk.CTkEntry(self, width=220, placeholder_text="Contact #", height=35)
        self.contact_entry.pack(pady=7)

        # Status Error/Success Label
        self.status_label = ctk.CTkLabel(self, text="", font=("Arial", 12))
        self.status_label.pack(pady=5)

        # Buttons
        self.register_btn = ctk.CTkButton(
            self, 
            text="Register", 
            command=self.perform_registration, 
            width=220,
            height=40,
            font=("Arial", 14, "bold")
        )
        self.register_btn.pack(pady=10)

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

    def perform_registration(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        contact = self.contact_entry.get().strip()

        if not username or not password or not confirm_password or not contact:
            self.status_label.configure(text="All fields are required!", text_color="red")
            return

        if password != confirm_password:
            self.status_label.configure(text="Passwords do not match!", text_color="red")
            return

        self.status_label.configure(text="Registering...", text_color="orange")
        self.update_idletasks()

        success, message = self.controller.db_module.register_user(username, password, contact)
        if success:
            self.status_label.configure(text=message, text_color="green")
            # Clear inputs
            self.clear_fields()
            # Redirect to login
            self.after(1500, lambda: self.controller.show_frame("LoginFrame"))
        else:
            self.status_label.configure(text=message, text_color="red")

    def clear_fields(self):
        self.username_entry.delete(0, 'end')
        self.password_entry.delete(0, 'end')
        self.confirm_password_entry.delete(0, 'end')
        self.contact_entry.delete(0, 'end')

    def go_back(self):
        self.status_label.configure(text="")
        self.clear_fields()
        self.controller.show_frame("MainFrame")

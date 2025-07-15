import customtkinter as ctk

class ExampleLoginApp:
    def __init__(self):
        # Configure appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create app
        self.app = ctk.CTk()
        self.app.title("Example Login")
        self.app.geometry("400x500")
        self.app.resizable(False, False)
        
        # Create frame
        self.frame = ctk.CTkFrame(master=self.app)
        self.frame.pack(pady=20, padx=40, fill="both", expand=True)
        
        # Create widgets
        self.label = ctk.CTkLabel(master=self.frame, text="Login System", font=("Roboto", 24))
        self.label.pack(pady=12, padx=10)
        
        self.username_entry = ctk.CTkEntry(master=self.frame, placeholder_text="Username")
        self.username_entry.pack(pady=12, padx=10)
        
        self.password_entry = ctk.CTkEntry(master=self.frame, placeholder_text="Password", show="*")
        self.password_entry.pack(pady=12, padx=10)
        
        self.checkbox = ctk.CTkCheckBox(master=self.frame, text="Remember Me")
        self.checkbox.pack(pady=12, padx=10)
        
        self.login_button = ctk.CTkButton(master=self.frame, text="Login", command=self.login_event)
        self.login_button.pack(pady=12, padx=10)
        
        self.register_button = ctk.CTkButton(master=self.frame, text="Register", 
                                            fg_color="transparent", border_width=2)
        self.register_button.pack(pady=12, padx=10)
        
    def login_event(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        # For demonstration purposes only
        if username == "admin" and password == "password":
            print("Login successful!")
        else:
            print("Login failed.")

    def run(self):
        self.app.mainloop()

# Create and run the app
if __name__ == "__main__":
    login_app = ExampleLoginApp()
    login_app.run()

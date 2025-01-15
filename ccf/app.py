import customtkinter as tk

tk.set_appearance_mode("System")  # Modes: system (default), light, dark
tk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

app = tk.CTk()  # create CTk window like you do with the Tk window
app.geometry("1280x720")

def button_function():
    print("button pressed")

# Use CTkButton instead of tkinter Button
button = tk.CTkButton(master=app, text="CTkButton", command=button_function)
button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

app.mainloop()

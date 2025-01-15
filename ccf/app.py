import customtkinter as tk

 #init theme
tk.set_appearance_mode("System")
tk.set_default_color_theme("dark-blue")

# init window
app = tk.CTk()  
app.geometry("1280x720")

# ---------------------------
# CALLBACKS & STATE VARIABLES
# ---------------------------
# main event callback
def PARAMS_CHANGED():
    print('PARAMS_CHANGED')

# set up app state variables 
val_checkbox_absolute_corr = tk.BooleanVar(value=False)
val_checkbox_filter_data = tk.BooleanVar(value=False)
val_checkbox_IBI = tk.BooleanVar(value=True)
val_checkbox_EDA = tk.BooleanVar(value=False)

# set up callbacks
def on_absolute_corr_change():
    new_val = val_checkbox_absolute_corr.get()
    PARAMS_CHANGED()

def on_filter_data_change():
    new_val = val_checkbox_filter_data.get()
    PARAMS_CHANGED()

def on_is_ibi_change():
    new_val = val_checkbox_IBI.get()
    val_checkbox_EDA.set(not new_val)
    PARAMS_CHANGED()

def on_is_eda_change():
    new_val = val_checkbox_EDA.get()
    val_checkbox_IBI.set(not new_val)
    PARAMS_CHANGED()
    

# -------------------
# GUI PARAMETER GROUP
# -------------------
# parameter group
frame_parameter_group = tk.CTkFrame(app)
frame_parameter_group.pack(pady=10, padx=20)

# input data
label_input_data = tk.CTkLabel(frame_parameter_group, text="Input Data")
label_input_data.grid(row=0, column=0, columnspan=2, pady=10)
# TODO Row 1: file picker
checkbox_filter_data = tk.CTkCheckBox(frame_parameter_group, text='Remove out of range samples', variable=val_checkbox_filter_data, command=on_filter_data_change)
checkbox_filter_data.grid(row=2, column=0, sticky="w", padx=10)

# data type
label_data_type = tk.CTkLabel(frame_parameter_group, text="Data Type")
label_data_type.grid(row=3, column=0, columnspan=2, pady=10)
checkbox_is_ibi_data = tk.CTkCheckBox(frame_parameter_group, text='IBI', variable=val_checkbox_IBI, command=on_is_ibi_change)
checkbox_is_ibi_data.grid(row=4, column=0, sticky="w", padx=10)
checkbox_is_eda_data = tk.CTkCheckBox(frame_parameter_group, text='EDA', variable=val_checkbox_EDA, command=on_is_eda_change)
checkbox_is_eda_data.grid(row=4, column=1, sticky="w", padx=10)

# correlation settings
label_corr_settings = tk.CTkLabel(frame_parameter_group, text="Correlation Settings")
label_corr_settings.grid(row=5, column=0, columnspan=2, pady=10)
# TODO row 6 windowed?
# TODO row 7 window_size?
# TODO row 8 max_lag? - note should be window//2
# TODO row 9 window step size?
checkbox_absolute_corr = tk.CTkCheckBox(frame_parameter_group, text='use absolute correlation values', variable=val_checkbox_absolute_corr, command=on_absolute_corr_change)
checkbox_absolute_corr.grid(row=10, column=0, sticky="w", padx=10)

# export
# TODO row 11 export button

# run app
app.mainloop()

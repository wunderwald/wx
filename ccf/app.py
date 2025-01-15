import customtkinter as tk
from tkinter import filedialog

 #init theme
tk.set_appearance_mode("System")
tk.set_default_color_theme("dark-blue")

# init window
app = tk.CTk()  
app.geometry("1280x720")

# ----------------
# INPUT VALIDATION
# ----------------
def on_validate_numeric_input(input):
    if input == "" or input.isdigit():
        return True
    return False
validate_numeric_input = app.register(on_validate_numeric_input)

# ---------------------------
# CALLBACKS & STATE VARIABLES
# ---------------------------
# main event callback
def PARAMS_CHANGED():
    print('PARAMS_CHANGED')

# set up app state variables 
val_CORRELATION_SETTINGS_VALID = tk.BooleanVar(value=True)
val_WINDOW_SIZE_VALID = tk.BooleanVar(value=True)
val_STEP_SIZE_VALID = tk.BooleanVar(value=True)
val_MAX_LAG_VALID = tk.BooleanVar(value=True)
val_checkbox_absolute_corr = tk.BooleanVar(value=False)
val_checkbox_filter_data = tk.BooleanVar(value=False)
val_checkbox_IBI = tk.BooleanVar(value=True)
val_checkbox_EDA = tk.BooleanVar(value=False)
val_checkbox_windowed_xcorr = tk.BooleanVar(value=True)
val_window_size_input = tk.StringVar(value='10')
val_step_size_input = tk.StringVar(value='1')
val_max_lag_input = tk.StringVar(value='5')
val_window_size = tk.IntVar(value=10)
val_step_size = tk.IntVar(value=1)
val_max_lag = tk.IntVar(value=5)

# entry callbacks
def check_window_size():
    # window size must be at least 3
    # TODO input should turn red if value is invalid
    window_size_is_valid = val_window_size.get() >= 3
    val_WINDOW_SIZE_VALID.set(window_size_is_valid)
    return window_size_is_valid

def check_step_size():
    # step size must be at least 1
    # TODO input should turn red if value is invalid
    step_size_is_valid = val_step_size.get() >= 1
    val_STEP_SIZE_VALID.set(step_size_is_valid)
    return step_size_is_valid

def check_max_lag():
    # max lag can be at most half the window size and more than 0
    # TODO max lag input should turn red if value is invalid
    max_lag_is_valid = val_max_lag.get() > 0 and val_max_lag.get() <= val_window_size.get() // 2
    val_MAX_LAG_VALID.set(max_lag_is_valid)
    return max_lag_is_valid

def check_correlation_settings():
    window_size_is_valid = check_window_size()
    step_size_is_valid = check_step_size()
    max_lag_is_valid = check_max_lag()
    correlation_settings_valid = window_size_is_valid and step_size_is_valid and max_lag_is_valid
    val_CORRELATION_SETTINGS_VALID.set(correlation_settings_valid)
    return correlation_settings_valid

def on_window_size_input_change(name, index, mode):
    new_str_val = val_window_size_input.get()
    if new_str_val == '':
        val_window_size.set(0)
    else:
        new_val = int(new_str_val)
        val_window_size.set(new_val)
    check_correlation_settings()
    PARAMS_CHANGED()
val_window_size_input.trace_add("write", on_window_size_input_change)

def on_step_size_input_change(name, index, mode):
    new_str_val = val_step_size_input.get()
    if new_str_val == '':
        val_step_size.set(0)
    else:
        new_val = int(new_str_val)
        val_step_size.set(new_val)
    check_correlation_settings()
    PARAMS_CHANGED()
val_step_size_input.trace_add("write", on_step_size_input_change)

def on_max_lag_input_change(name, index, mode):
    new_str_val = val_max_lag_input.get()
    if new_str_val == '':
        val_max_lag.set(0)
    else:
        new_val = int(new_str_val)
        val_max_lag.set(new_val)
    check_correlation_settings()
    PARAMS_CHANGED()
val_max_lag_input.trace_add("write", on_max_lag_input_change)



# checkbox callbacks
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

def on_windowed_xcorr_change():
    new_val = val_checkbox_windowed_xcorr.get()
    print("TODO ! (de-) activate window settings")
    PARAMS_CHANGED()    

# button callbacks
def export_data():
    print("TODO: prepare data for export, open path picker, save file")

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
checkbox_filter_data.grid(row=2, column=0, sticky="w", padx=10, pady=5)

# data type
label_data_type = tk.CTkLabel(frame_parameter_group, text="Data Type")
label_data_type.grid(row=3, column=0, columnspan=2, pady=10)
checkbox_is_ibi_data = tk.CTkCheckBox(frame_parameter_group, text='IBI', variable=val_checkbox_IBI, command=on_is_ibi_change)
checkbox_is_ibi_data.grid(row=4, column=0, sticky="w", padx=10, pady=5)
checkbox_is_eda_data = tk.CTkCheckBox(frame_parameter_group, text='EDA', variable=val_checkbox_EDA, command=on_is_eda_change)
checkbox_is_eda_data.grid(row=4, column=1, sticky="w", padx=10, pady=5)

# correlation settings
label_corr_settings = tk.CTkLabel(frame_parameter_group, text="Correlation Settings")
label_corr_settings.grid(row=5, column=0, columnspan=2, pady=10)
checkbox_is_eda_data = tk.CTkCheckBox(frame_parameter_group, text='Windowed XCorr', variable=val_checkbox_windowed_xcorr, command=on_windowed_xcorr_change)
checkbox_is_eda_data.grid(row=6, column=0, sticky="w", padx=10, pady=5)
label_window_size = tk.CTkLabel(frame_parameter_group, text='Window Size')
label_window_size.grid(row=7, column=0, sticky="w", padx=10, pady=5)
entry_window_size = tk.CTkEntry(frame_parameter_group, validate="key", validatecommand=(validate_numeric_input, "%P"), textvariable=val_window_size_input)
entry_window_size.grid(row=7, column=1, sticky="w", padx=10, pady=5)
label_max_lag = tk.CTkLabel(frame_parameter_group, text='Max Lag')
label_max_lag.grid(row=8, column=0, sticky="w", padx=10, pady=5)
entry_max_lag = tk.CTkEntry(frame_parameter_group, validate="key", validatecommand=(validate_numeric_input, "%P"), textvariable=val_max_lag_input)
entry_max_lag.grid(row=8, column=1, sticky="w", padx=10, pady=5)
label_step_size = tk.CTkLabel(frame_parameter_group, text='Step Size')
label_step_size.grid(row=9, column=0, sticky="w", padx=10, pady=5)
entry_step_size = tk.CTkEntry(frame_parameter_group, validate="key", validatecommand=(validate_numeric_input, "%P"), textvariable=val_step_size_input)
entry_step_size.grid(row=9, column=1, sticky="w", padx=10, pady=5)
checkbox_absolute_corr = tk.CTkCheckBox(frame_parameter_group, text='Absolute Correlation Values', variable=val_checkbox_absolute_corr, command=on_absolute_corr_change)
checkbox_absolute_corr.grid(row=10, column=0, sticky="w", padx=10, pady=5)

# export
button_export = tk.CTkButton(frame_parameter_group, text='Export', command=export_data)
button_export.grid(row=11, column=0, sticky="w", padx=10, pady=5)

# run app
app.mainloop()

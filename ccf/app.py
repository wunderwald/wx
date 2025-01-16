import os
import customtkinter as tk
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from plot import plot_windowed_cross_correlation, plot_init
from cross_correlation import windowed_cross_correlation
from xlsx import write_xlsx

# ------------------
# APP INITIALIZATION
# ------------------

#init theme
tk.set_appearance_mode("System")
tk.set_default_color_theme("dark-blue")

# init window
app = tk.CTk()  
app.title("ccf")
app.geometry("1620x900")

# ----------------------
# DEFAULTS / INIT VALUES
# ----------------------

INIT_WINDOW_SIZE = 20
INIT_STEP_SIZE = 10
INIT_MAX_LAG = 10    # default: window_size//2

# ---------------------
# GLOBAL STATE & EVENTS
# ---------------------

# input validation trackers
val_CORRELATION_SETTINGS_VALID = tk.BooleanVar(value=True)
val_WINDOW_SIZE_VALID = tk.BooleanVar(value=True)
val_STEP_SIZE_VALID = tk.BooleanVar(value=True)
val_MAX_LAG_VALID = tk.BooleanVar(value=True)

# update count
val_UPDATE_COUNT = tk.IntVar(value=0)

# main event callback
def PARAMS_CHANGED():
    print('PARAMS_CHANGED')
    val_UPDATE_COUNT.set(val_UPDATE_COUNT.get() + 1)

# ----------------
# INPUT VALIDATION
# ----------------

def on_validate_numeric_input(input):
    if input == "" or input.isdigit():
        return True
    return False
validate_numeric_input = app.register(on_validate_numeric_input)

# entry validation
def check_window_size():
    # window size must be at least 3
    window_size_is_valid = val_window_size.get() >= 3
    val_WINDOW_SIZE_VALID.set(window_size_is_valid)
    return window_size_is_valid

def check_step_size():
    # step size must be at least 1 and at most window size
    window_size_is_valid = val_WINDOW_SIZE_VALID.get()
    window_size = val_window_size.get()
    step_size = val_step_size.get()
    step_size_is_valid = step_size >= 1 and (not window_size_is_valid or step_size <= window_size)
    val_STEP_SIZE_VALID.set(step_size_is_valid)
    return step_size_is_valid

def check_max_lag():
    # max lag can be at most half the window size and more than 0
    max_lag_is_valid = val_max_lag.get() > 0 and val_max_lag.get() <= val_window_size.get() // 2
    val_MAX_LAG_VALID.set(max_lag_is_valid)
    return max_lag_is_valid

def check_correlation_settings():
    window_size_is_valid = check_window_size()
    step_size_is_valid = check_step_size()
    max_lag_is_valid = check_max_lag()
    correlation_settings_valid = window_size_is_valid and step_size_is_valid and max_lag_is_valid
    val_CORRELATION_SETTINGS_VALID.set(correlation_settings_valid)
    PARAMS_CHANGED()
    return correlation_settings_valid

# ---------------------------
# CALLBACKS & STATE VARIABLES
# ---------------------------

# set up app state variables 
val_checkbox_absolute_corr = tk.BooleanVar(value=False)
val_checkbox_filter_data = tk.BooleanVar(value=False)
val_checkbox_IBI = tk.BooleanVar(value=True)
val_checkbox_EDA = tk.BooleanVar(value=False)
val_checkbox_windowed_xcorr = tk.BooleanVar(value=True)
val_window_size_input = tk.StringVar(value=INIT_WINDOW_SIZE)
val_step_size_input = tk.StringVar(value=INIT_STEP_SIZE)
val_max_lag_input = tk.StringVar(value=INIT_MAX_LAG)    
val_window_size = tk.IntVar(value=INIT_WINDOW_SIZE)
val_step_size = tk.IntVar(value=INIT_STEP_SIZE)
val_max_lag = tk.IntVar(value=INIT_MAX_LAG)
val_selected_file = tk.StringVar(value = '')

# set up data container
dat_plot_data = {
    'fig': plot_init()
}

# entry callbacks
def on_window_size_input_change(name, index, mode):
    new_str_val = val_window_size_input.get()
    if new_str_val == '':
        val_window_size.set(0)
    else:
        new_val = int(new_str_val)
        val_window_size.set(new_val)
    check_correlation_settings()
val_window_size_input.trace_add("write", on_window_size_input_change)

def on_step_size_input_change(name, index, mode):
    new_str_val = val_step_size_input.get()
    if new_str_val == '':
        val_step_size.set(0)
    else:
        new_val = int(new_str_val)
        val_step_size.set(new_val)
    check_correlation_settings()
val_step_size_input.trace_add("write", on_step_size_input_change)

def on_max_lag_input_change(name, index, mode):
    new_str_val = val_max_lag_input.get()
    if new_str_val == '':
        val_max_lag.set(0)
    else:
        new_val = int(new_str_val)
        val_max_lag.set(new_val)
    check_correlation_settings()
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
    PARAMS_CHANGED()    

# button callbacks
def export_data():
    # get filename using file picker
    file_path = filedialog.asksaveasfilename(
        title="Save As",
        defaultextension=".xlsx",  
        filetypes=(
            ("XLSX files", "*.xlsx"),
        )
    )
    if not file_path: return
    print(file_path)

def export_plot():
    # get fig data
    fig = dat_plot_data["fig"]
    if not fig: return
    
    # create initial output file name
    selected_file = val_selected_file.get()
    filename_init = f"plot_{os.path.basename(selected_file).replace('.xlsx', '')}" if selected_file else "plot_cff"

    # get filename using file picker
    file_path = filedialog.asksaveasfilename(
        title="Save As",
        defaultextension=".png",  
        initialfile=filename_init,
        filetypes=(
            ("PNG files", "*.png"),
        )
    )
    if not file_path: return
    
    # export plot
    fig.savefig(file_path, dpi=300, format='png')

# -----------
# FILE PICKER
# -----------

def open_file_picker():
    file_path = filedialog.askopenfilename(
        title="Select an Excel file",
        filetypes=(("Excel files", "*.xlsx"), ("All files", "*.*"))
    )
    if file_path: 
        val_selected_file.set(file_path)
        PARAMS_CHANGED()    


# -----------
# MAIN LAYOUT
# -----------
# main grid
group_main = tk.CTkFrame(app)
group_main.pack(pady=10, padx=20)
# plot group
group_plot = tk.CTkFrame(group_main)
group_plot.grid(row=0, column=0, pady=10, padx=20)
# parameter group
group_parameter_settings = tk.CTkFrame(group_main)
group_parameter_settings.grid(row=0, column=1, pady=10, padx=20)


# -------------------
# GUI PARAMETER GROUP
# -------------------
# input data
label_input_data = tk.CTkLabel(group_parameter_settings, text="Input Data", font=("Arial", 20, "bold"))
label_input_data.grid(row=0, column=0, columnspan=2, pady=20)
button_file_picker = tk.CTkButton(group_parameter_settings, text="Choose Excel File", command=open_file_picker)
button_file_picker.grid(row=1, column=0, sticky="w", padx=10, pady=5)
label_file_picker = tk.CTkLabel(group_parameter_settings, text="No file selected.")
label_file_picker.grid(row=1, column=1, sticky="w", padx=10, pady=5)
checkbox_filter_data = tk.CTkCheckBox(group_parameter_settings, text='Remove out of range samples', variable=val_checkbox_filter_data, command=on_filter_data_change)
checkbox_filter_data.grid(row=2, column=0, sticky="w", padx=10, pady=5)

# data type
label_data_type = tk.CTkLabel(group_parameter_settings, text="Data Type", font=("Arial", 20, "bold"))
label_data_type.grid(row=3, column=0, columnspan=2, pady=20)
checkbox_is_ibi_data = tk.CTkCheckBox(group_parameter_settings, text='IBI', variable=val_checkbox_IBI, command=on_is_ibi_change)
checkbox_is_ibi_data.grid(row=4, column=0, sticky="w", padx=10, pady=5)
checkbox_is_eda_data = tk.CTkCheckBox(group_parameter_settings, text='EDA', variable=val_checkbox_EDA, command=on_is_eda_change)
checkbox_is_eda_data.grid(row=4, column=1, sticky="w", padx=10, pady=5)

# correlation settings
label_corr_settings = tk.CTkLabel(group_parameter_settings, text="Correlation Settings", font=("Arial", 20, "bold"))
label_corr_settings.grid(row=5, column=0, columnspan=2, pady=20)
checkbox_is_eda_data = tk.CTkCheckBox(group_parameter_settings, text='Windowed XCorr', variable=val_checkbox_windowed_xcorr, command=on_windowed_xcorr_change)
checkbox_is_eda_data.grid(row=6, column=0, sticky="w", padx=10, pady=5)
label_window_size = tk.CTkLabel(group_parameter_settings, text='Window Size')
label_window_size.grid(row=7, column=0, sticky="w", padx=10, pady=5)
entry_window_size = tk.CTkEntry(group_parameter_settings, validate="key", validatecommand=(validate_numeric_input, "%P"), textvariable=val_window_size_input, border_color='#777777')
entry_window_size.grid(row=7, column=1, sticky="w", padx=10, pady=5)
label_max_lag = tk.CTkLabel(group_parameter_settings, text='Max Lag')
label_max_lag.grid(row=8, column=0, sticky="w", padx=10, pady=5)
entry_max_lag = tk.CTkEntry(group_parameter_settings, validate="key", validatecommand=(validate_numeric_input, "%P"), textvariable=val_max_lag_input, border_color='#777777')
entry_max_lag.grid(row=8, column=1, sticky="w", padx=10, pady=5)
label_step_size = tk.CTkLabel(group_parameter_settings, text='Step Size')
label_step_size.grid(row=9, column=0, sticky="w", padx=10, pady=5)
entry_step_size = tk.CTkEntry(group_parameter_settings, validate="key", validatecommand=(validate_numeric_input, "%P"), textvariable=val_step_size_input, border_color='#777777')
entry_step_size.grid(row=9, column=1, sticky="w", padx=10, pady=5)
checkbox_absolute_corr = tk.CTkCheckBox(group_parameter_settings, text='Absolute Correlation Values', variable=val_checkbox_absolute_corr, command=on_absolute_corr_change)
checkbox_absolute_corr.grid(row=10, column=0, sticky="w", padx=10, pady=5)

# export
label_corr_settings = tk.CTkLabel(group_parameter_settings, text="Export", font=("Arial", 20, "bold"))
label_corr_settings.grid(row=11, column=0, columnspan=2, pady=10)
button_export_data = tk.CTkButton(group_parameter_settings, text='Export XLSX', command=export_data)
button_export_data.grid(row=12, column=0, padx=10, pady=10)
button_export_plot = tk.CTkButton(group_parameter_settings, text='Export Plots', command=export_plot)
button_export_plot.grid(row=12, column=1, padx=10, pady=10)

 # TODO deactivate export buttons if there is no data

# ---------------------
# PARAMETER GUI UPDATES
# ---------------------
def update_color_window_size_entry(*args):
    entry_window_size.configure(border_color='#777777' if val_WINDOW_SIZE_VALID.get() else 'red')
val_WINDOW_SIZE_VALID.trace_add('write', update_color_window_size_entry)

def update_color_step_size_entry(*args):
    entry_step_size.configure(border_color='#777777' if val_STEP_SIZE_VALID.get() else 'red')
val_STEP_SIZE_VALID.trace_add('write', update_color_step_size_entry)

def update_color_max_lag_entry(*args):
    entry_max_lag.configure(border_color='#777777' if val_MAX_LAG_VALID.get() else 'red')
val_MAX_LAG_VALID.trace_add('write', update_color_max_lag_entry)

def update_active_state_export_button(*args):
    button_export_data.configure(state="normal" if val_CORRELATION_SETTINGS_VALID.get() else "disabled")
    button_export_plot.configure(state="normal" if val_CORRELATION_SETTINGS_VALID.get() else "disabled")
val_CORRELATION_SETTINGS_VALID.trace_add('write', update_active_state_export_button)

def update_active_state_correlation_parameters(*args):
    is_active = val_checkbox_windowed_xcorr.get()
    active_state = "normal" if is_active else "disabled"
    border_color = '#777777' if is_active else '#000000'
    entry_window_size.configure(state=active_state)
    entry_window_size.configure(border_color=border_color)
    entry_max_lag.configure(state=active_state)
    entry_max_lag.configure(border_color=border_color)
    entry_step_size.configure(state=active_state)
    entry_step_size.configure(border_color=border_color)
val_checkbox_windowed_xcorr.trace_add('write', update_active_state_correlation_parameters)

def update_file_picker_label(*args):
    file_path = val_selected_file.get()
    label_file_picker.configure(text='No file selected.' if file_path == '' else os.path.basename(file_path))
val_selected_file.trace_add('write', update_file_picker_label)

# --------
# PLOTTING
# --------
# create canvas
#dat_current_plot = plot_init()
canvas = FigureCanvasTkAgg(dat_plot_data["fig"], master=group_plot)

def update_canvas():
    if not dat_plot_data["fig"]: return
    canvas.figure = dat_plot_data["fig"]
    canvas.draw()
    canvas.get_tk_widget().pack(pady=10)

# test plot
def plot_test(*args):
    if not val_CORRELATION_SETTINGS_VALID.get():
        return
    
    # calculate wxcorr
    length = 800
    signal1 = np.sin(np.linspace(0, 5 * np.pi, length))
    # signal2 = np.cos(np.linspace(0, 4 * np.pi, length))
    signal2 = signal1 * 4*(np.random.random(length))

    window_size = val_window_size.get()
    step_size = val_step_size.get()
    max_lag = val_max_lag.get()
    absolute_values = val_checkbox_absolute_corr.get()

    windowed_corr_data = windowed_cross_correlation(signal1, signal2, window_size=window_size, step_size=step_size, max_lag=max_lag, absolute=absolute_values)
    
    # make plot figure
    fig = plot_windowed_cross_correlation(windowed_corr_data, max_lag, step_size, signal1, signal2)
    dat_plot_data["fig"] = fig

    # update canvas
    update_canvas()

plot_test()

# auto refresh
val_UPDATE_COUNT.trace_add('write', plot_test)

# ---
# RUN
# ---
app.mainloop()
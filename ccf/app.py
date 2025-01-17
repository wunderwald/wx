import os
import customtkinter as tk
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from plot import plot_windowed_cross_correlation, plot_standard_cross_correlation, plot_init
from cross_correlation import windowed_cross_correlation, standard_cross_correlation
from xlsx import write_xlsx

# ------------------
# APP INITIALIZATION
# ------------------

#init theme
tk.set_appearance_mode("Light") # options 'System', 'Light', 'Dark'
tk.set_default_color_theme("dark-blue")

# init window
app = tk.CTk()  
app.title("ccf")
app.geometry("1620x900")

# ----------------------
# DEFAULTS / INIT VALUES
# ----------------------

INIT_WINDOW_SIZE = 100
INIT_STEP_SIZE = 10
INIT_MAX_LAG = 50    # default: window_size//2
INIT_MAX_LAG_SXC = 100

# ---------------------
# GLOBAL STATE & EVENTS
# ---------------------

# input validation trackers
# TODO: init with false and reset to false when data changes [as soon as file input is implemented]
val_CORRELATION_SETTINGS_VALID = tk.BooleanVar(value=True)
val_CORRELATION_SETTINGS_VALID_SXC = tk.BooleanVar(value=True)
val_WINDOW_SIZE_VALID = tk.BooleanVar(value=True)
val_STEP_SIZE_VALID = tk.BooleanVar(value=True)
val_MAX_LAG_VALID = tk.BooleanVar(value=True)
val_MAX_LAG_VALID_SXC = tk.BooleanVar(value=True)

# update count: changes trigger rerendering
val_UPDATE_COUNT = tk.IntVar(value=0)

# main event callback: causes rerendering
def PARAMS_CHANGED():
    val_UPDATE_COUNT.set(val_UPDATE_COUNT.get() + 1)

# ----------------
# INPUT VALIDATION
# ----------------

def on_validate_numeric_input(input):
    if input == "" or input.isdigit():
        return True
    return False
validate_numeric_input = app.register(on_validate_numeric_input)

# entry validation (windowed_xcorr)
def check_window_size():
    # window size must be at least 1
    data_length = val_data_length.get()
    window_size_is_valid = val_window_size.get() >= 1 and val_window_size.get() <= data_length
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
    window_size_is_valid = val_WINDOW_SIZE_VALID.get()
    max_lag_is_valid = val_max_lag.get() > 0 and (not window_size_is_valid or (val_max_lag.get() <= val_window_size.get() // 2))
    val_MAX_LAG_VALID.set(max_lag_is_valid)
    return max_lag_is_valid

def check_wx_correlation_settings():
    window_size_is_valid = check_window_size()
    step_size_is_valid = check_step_size()
    max_lag_is_valid = check_max_lag()
    correlation_settings_valid = window_size_is_valid and step_size_is_valid and max_lag_is_valid
    val_CORRELATION_SETTINGS_VALID.set(correlation_settings_valid)
    PARAMS_CHANGED()
    return correlation_settings_valid

# entry validation (standard xcorr)
def check_max_lag_sxc():
    # max lag range [0, data_length - 1]
    data_length = val_data_length.get()
    max_lag = val_max_lag_sxc.get()
    max_lag_is_valid = max_lag >= 0 and  max_lag < data_length
    val_MAX_LAG_VALID_SXC.set(max_lag_is_valid)
    return max_lag_is_valid

def check_sx_correlation_settings():
    max_lag_is_valid = check_max_lag_sxc()
    correlation_settings_valid = max_lag_is_valid
    val_CORRELATION_SETTINGS_VALID_SXC.set(correlation_settings_valid)
    PARAMS_CHANGED()
    return correlation_settings_valid

# ------------------------------
# DATA STORAGE & STATE VARIABLES
# ------------------------------

# set up app state variables 
val_checkbox_absolute_corr = tk.BooleanVar(value=False)
val_checkbox_absolute_corr_sxc = tk.BooleanVar(value=False)
val_checkbox_filter_data = tk.BooleanVar(value=False)
val_checkbox_IBI = tk.BooleanVar(value=True)
val_checkbox_EDA = tk.BooleanVar(value=False)
val_checkbox_windowed_xcorr = tk.BooleanVar(value=True)
val_window_size_input = tk.StringVar(value=INIT_WINDOW_SIZE)
val_step_size_input = tk.StringVar(value=INIT_STEP_SIZE)
val_max_lag_input = tk.StringVar(value=INIT_MAX_LAG) 
val_max_lag_input_sxc = tk.StringVar(value=INIT_MAX_LAG_SXC)   
val_window_size = tk.IntVar(value=INIT_WINDOW_SIZE)
val_step_size = tk.IntVar(value=INIT_STEP_SIZE)
val_max_lag = tk.IntVar(value=INIT_MAX_LAG)
val_max_lag_sxc = tk.IntVar(value=INIT_MAX_LAG_SXC)
val_checkbox_average_windows = tk.BooleanVar(value=False)
val_checkbox_tscl_index = tk.BooleanVar(value=True)
val_checkbox_tscl_center = tk.BooleanVar(value=False)
val_selected_file = tk.StringVar(value='')
val_data_length = tk.IntVar(value=0)

# set up data containers
dat_plot_data = {
    'fig': plot_init()
}
dat_physiological_data = {
    'signal_a': [],
    'signal_b': []
}
dat_correlation_data = {
    'wxcorr': [],
    'sxcorr': []
}

# ---------
# CALLBACKS
# ---------

# entry callbacks windowed xcorr
def on_window_size_input_change(name, index, mode):
    new_str_val = val_window_size_input.get()
    if new_str_val == '':
        val_window_size.set(0)
    else:
        new_val = int(new_str_val)
        val_window_size.set(new_val)
    check_wx_correlation_settings()
val_window_size_input.trace_add("write", on_window_size_input_change)

def on_step_size_input_change(name, index, mode):
    new_str_val = val_step_size_input.get()
    if new_str_val == '':
        val_step_size.set(0)
    else:
        new_val = int(new_str_val)
        val_step_size.set(new_val)
    check_wx_correlation_settings()
val_step_size_input.trace_add("write", on_step_size_input_change)

def on_max_lag_input_change(name, index, mode):
    new_str_val = val_max_lag_input.get()
    if new_str_val == '':
        val_max_lag.set(0)
    else:
        new_val = int(new_str_val)
        val_max_lag.set(new_val)
    check_wx_correlation_settings()
val_max_lag_input.trace_add("write", on_max_lag_input_change)

# entry callbacks standard xcorr
def on_max_lag_input_change_sxc(name, index, mode):
    new_str_val = val_max_lag_input_sxc.get()
    if new_str_val == '':
        val_max_lag_sxc.set(0)
    else:
        new_val = int(new_str_val)
        val_max_lag_sxc.set(new_val)
    check_sx_correlation_settings()
val_max_lag_input_sxc.trace_add("write", on_max_lag_input_change_sxc)

# checkbox callbacks
def on_absolute_corr_change():
    new_val = val_checkbox_absolute_corr.get()
    PARAMS_CHANGED()

def on_absolute_corr_change_sxc():
    new_val = val_checkbox_absolute_corr_sxc.get()
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

def on_use_tscl_index_change():
    new_val = val_checkbox_tscl_index.get()
    val_checkbox_tscl_center.set(not new_val)
    PARAMS_CHANGED()

def on_use_tscl_center_change():
    new_val = val_checkbox_tscl_center.get()
    val_checkbox_tscl_index.set(not new_val)
    PARAMS_CHANGED()

def on_windowed_xcorr_change():
    new_val = val_checkbox_windowed_xcorr.get()
    PARAMS_CHANGED()    

def on_average_windows_change():
    new_val = val_checkbox_average_windows.get()
    PARAMS_CHANGED()

# ---------------
# EXPORT HANDLERS
# ---------------

def _export_wxcorr_data(file_path):
    metadata = {
        'xcorr type': "windowed cross-correlation",
        'Input file': f"{os.path.basename(val_selected_file.get())}.xlsx",
        'Phsyiological data type': 'EDA' if val_checkbox_EDA.get() else 'IBI', 
        'Filtered input data': val_checkbox_filter_data.get(),
        'Window size': val_window_size.get(),
        'Max lag': val_max_lag.get(),
        'Step size': val_step_size.get(),
        'Window overlap ratio': val_step_size.get() / val_window_size.get(),
        'Absolute correlation values': val_checkbox_absolute_corr.get(),
        'Per-window averages': val_checkbox_average_windows.get(),
        'Input signals resampled to 5hz': val_checkbox_IBI.get(),
    }
    vectors = {
        'signal_a': dat_physiological_data["signal_a"],
        'signal_b': dat_physiological_data["signal_b"],
        'window start index': [o['start_idx'] for o in dat_correlation_data["wxcorr"]],
        'max correlation (r_max)': [o['r_max'] for o in dat_correlation_data["wxcorr"]],
        'lag of max correlation (tau_max)': [o['tau_max'] for o in dat_correlation_data["wxcorr"]],
    }
    for window_index, window in enumerate(dat_correlation_data["wxcorr"]):
        vectors[f"w_{window_index}_correlations"] = window['correlations']
        vectors[f"w_{window_index}_meta"] = [ f"start_idx={window['start_idx']}", f"center_idx={window['center_idx']}", f"r_max={window['r_max']}", f"tau_max={window['tau_max']}" ]

    write_xlsx(vectors=vectors, single_values=metadata, output_path=file_path)

def _export_sxcorr_data(file_path):
    metadata = {
        'xcorr type': "(standard) cross-correlation",
        'Input file': f"{os.path.basename(val_selected_file.get())}.xlsx",
        'Phsyiological data type': 'EDA' if val_checkbox_EDA.get() else 'IBI', 
        'Filtered input data': val_checkbox_filter_data.get(),
        'Max lag': val_max_lag_sxc.get(),
        'Absolute correlation values': val_checkbox_absolute_corr_sxc.get(),
        'Input signals resampled to 5hz': val_checkbox_IBI.get(),
    }
    vectors = {
        'signal_a': dat_physiological_data["signal_a"],
        'signal_b': dat_physiological_data["signal_b"],
        'lag': dat_correlation_data["sxcorr"]['lags'],
        'correlation': dat_correlation_data["sxcorr"]['corr'],
    }
    write_xlsx(vectors=vectors, single_values=metadata, output_path=file_path)

# export XLSX data
def export_data():
    # create initial output file name
    selected_file = val_selected_file.get()
    filename_init = f"xc_data_{os.path.basename(selected_file).replace('.xlsx', '')}" if selected_file else "xc_data"
    # get filename using file picker
    file_path = filedialog.asksaveasfilename(
        title="Save As",
        defaultextension=".xlsx",  
        initialfile=filename_init,
        filetypes=(
            ("XLSX files", "*.xlsx"),
        )
    )
    if not file_path: return
    # call specialised export function
    is_windowed_xcorr = val_checkbox_windowed_xcorr.get()
    if is_windowed_xcorr:
        _export_wxcorr_data(file_path)
    else:
        _export_sxcorr_data(file_path)

# export plots as PNG
def export_plot():
    # get fig data
    fig = dat_plot_data["fig"]
    if not fig: return
    
    # create initial output file name
    selected_file = val_selected_file.get()
    filename_init = f"xc_plot_{os.path.basename(selected_file).replace('.xlsx', '')}" if selected_file else "xc_plot"

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
        # TODO: load data 
        # TODO: update val_data_length
        # TODO: clear dat_correlation_data["wxcorr"] and dat_correlation_data["sxcorr"]
        PARAMS_CHANGED()    


# -----------
# MAIN LAYOUT
# -----------
# main grid
group_main = tk.CTkFrame(app)
group_main.pack(pady=10, padx=20)
# plot group
group_plot = tk.CTkFrame(group_main)
group_plot.grid(row=0, column=0, pady=0, padx=0)
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
checkbox_is_eda_data = tk.CTkCheckBox(group_parameter_settings, text='Windowed cross-correlation', variable=val_checkbox_windowed_xcorr, command=on_windowed_xcorr_change)
checkbox_is_eda_data.grid(row=6, column=0, sticky="w", padx=10, pady=5)

# windowerd xcorr specialised settings
subgroup_windowed_xcorr_parameters = tk.CTkFrame(group_parameter_settings)
subgroup_windowed_xcorr_parameters.grid(row=7, column=0, columnspan=2, padx=0, pady=0)
label_subgroup_windowed_xcorr_parameters=tk.CTkLabel(subgroup_windowed_xcorr_parameters, text='Windowed cross-correlation parameters')
label_subgroup_windowed_xcorr_parameters.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky='w')
label_window_size = tk.CTkLabel(subgroup_windowed_xcorr_parameters, text='Window Size')
label_window_size.grid(row=1, column=0, sticky="w", padx=10, pady=5)
entry_window_size = tk.CTkEntry(subgroup_windowed_xcorr_parameters, validate="key", validatecommand=(validate_numeric_input, "%P"), textvariable=val_window_size_input, border_color='#777777')
entry_window_size.grid(row=1, column=1, sticky="w", padx=10, pady=5)
error_label_window_size = tk.CTkLabel(subgroup_windowed_xcorr_parameters, text='Window Size must be in range [1, data_length]', text_color='red') # initially hidden
label_max_lag = tk.CTkLabel(subgroup_windowed_xcorr_parameters, text='Max Lag')
label_max_lag.grid(row=3, column=0, sticky="w", padx=10, pady=5)
entry_max_lag = tk.CTkEntry(subgroup_windowed_xcorr_parameters, validate="key", validatecommand=(validate_numeric_input, "%P"), textvariable=val_max_lag_input, border_color='#777777')
entry_max_lag.grid(row=3, column=1, sticky="w", padx=10, pady=5)
error_label_max_lag = tk.CTkLabel(subgroup_windowed_xcorr_parameters, text='Max Lag must be in range [1, window_size//2]', text_color='red') # initially hidden
label_step_size = tk.CTkLabel(subgroup_windowed_xcorr_parameters, text='Step Size')
label_step_size.grid(row=5, column=0, sticky="w", padx=10, pady=5)
entry_step_size = tk.CTkEntry(subgroup_windowed_xcorr_parameters, validate="key", validatecommand=(validate_numeric_input, "%P"), textvariable=val_step_size_input, border_color='#777777')
entry_step_size.grid(row=5, column=1, sticky="w", padx=10, pady=5)
error_label_step_size = tk.CTkLabel(subgroup_windowed_xcorr_parameters, text='Step Size must be in range [1, window_size]', text_color='red') # initially hidden
checkbox_absolute_corr = tk.CTkCheckBox(subgroup_windowed_xcorr_parameters, text='Absolute Correlation Values', variable=val_checkbox_absolute_corr, command=on_absolute_corr_change)
checkbox_absolute_corr.grid(row=9, column=0, sticky="w", padx=10, pady=5)
checkbox_average_windows = tk.CTkCheckBox(subgroup_windowed_xcorr_parameters, text='Average Values in Windows', variable=val_checkbox_average_windows, command=on_average_windows_change)
checkbox_average_windows.grid(row=10, column=0, sticky="w", padx=10, pady=5)

# standard xcorr specialised settings (initially hidden)
subgroup_standard_xcorr_parameters = tk.CTkFrame(group_parameter_settings)
label_subgroup_standard_xcorr_parameters=tk.CTkLabel(subgroup_standard_xcorr_parameters, text='Standard cross-correlation parameters')
label_subgroup_standard_xcorr_parameters.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky='w')
label_max_lag_sxc = tk.CTkLabel(subgroup_standard_xcorr_parameters, text='Max Lag')
label_max_lag_sxc.grid(row=1, column=0, sticky="w", padx=10, pady=5)
entry_max_lag_sxc = tk.CTkEntry(subgroup_standard_xcorr_parameters, validate="key", validatecommand=(validate_numeric_input, "%P"), textvariable=val_max_lag_input_sxc, border_color='#777777')
entry_max_lag_sxc.grid(row=1, column=1, sticky="w", padx=10, pady=5)
error_label_max_lag_sxc = tk.CTkLabel(subgroup_standard_xcorr_parameters, text='Max Lag must be in range [0, data_length - 1]', text_color='red') # initially hidden
checkbox_absolute_corr_sxc = tk.CTkCheckBox(subgroup_standard_xcorr_parameters, text='Absolute Correlation Values', variable=val_checkbox_absolute_corr_sxc, command=on_absolute_corr_change_sxc)
checkbox_absolute_corr_sxc.grid(row=3, column=0, sticky="w", padx=10, pady=5)

# visualisation settings
label_vis_settings = tk.CTkLabel(group_parameter_settings, text="Visualisation", font=("Arial", 20, "bold"))
label_vis_settings.grid(row=8, column=0, columnspan=2, pady=10)
subgroup_vis_settings = tk.CTkFrame(group_parameter_settings)
subgroup_vis_settings.grid(row=9, column=0, columnspan=2, padx=0, pady=0)
label_vis_time_scale  = tk.CTkLabel(subgroup_vis_settings, text="Time format in plots")
label_vis_time_scale.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky='w')
checkbox_use_tscl_index = tk.CTkCheckBox(subgroup_vis_settings, text='Window Start Indices', variable=val_checkbox_tscl_index, command=on_use_tscl_index_change)
checkbox_use_tscl_index.grid(row=3, column=0, sticky="w", padx=10, pady=5)
checkbox_use_tscl_center = tk.CTkCheckBox(subgroup_vis_settings, text='Window Center Time', variable=val_checkbox_tscl_center, command=on_use_tscl_center_change)
checkbox_use_tscl_center.grid(row=3, column=1, sticky="w", padx=10, pady=5)

# export
label_corr_settings = tk.CTkLabel(group_parameter_settings, text="Export", font=("Arial", 20, "bold"))
label_corr_settings.grid(row=10, column=0, columnspan=2, pady=10)
subgroup_export_buttons = tk.CTkFrame(group_parameter_settings)
subgroup_export_buttons.grid(row=11, column=0, columnspan=2, padx=0, pady=0)
button_export_data = tk.CTkButton(subgroup_export_buttons, text='Export XLSX', command=export_data)
button_export_data.grid(row=2, column=0, padx=10, pady=10)
button_export_plot = tk.CTkButton(subgroup_export_buttons, text='Export Plots', command=export_plot)
button_export_plot.grid(row=2, column=1, padx=10, pady=10)

# ---------------------
# PARAMETER GUI UPDATES
# ---------------------

# windowed xcorr entries
def update_window_size_entry_on_validation(*args):
    win_size_is_valid = val_WINDOW_SIZE_VALID.get()
    if win_size_is_valid:
        entry_window_size.configure(border_color='#777777')
        error_label_window_size.grid_forget()
    else:  
        entry_window_size.configure(border_color='red')  
        error_label_window_size.grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=0)
val_WINDOW_SIZE_VALID.trace_add('write', update_window_size_entry_on_validation)

def update_max_lag_entry_on_validation(*args):
    max_lag_is_valid = val_MAX_LAG_VALID.get()
    if max_lag_is_valid:
        entry_max_lag.configure(border_color='#777777')
        error_label_max_lag.grid_forget()
    else:  
        entry_max_lag.configure(border_color='red')  
        error_label_max_lag.grid(row=4, column=0, columnspan=2, sticky="w", padx=10, pady=0)
val_MAX_LAG_VALID.trace_add('write', update_max_lag_entry_on_validation)

def update_step_size_entry_on_validation(*args):
    step_size_is_valid = val_STEP_SIZE_VALID.get()
    if step_size_is_valid:
        entry_step_size.configure(border_color='#777777')
        error_label_step_size.grid_forget()
    else:  
        entry_step_size.configure(border_color='red')  
        error_label_step_size.grid(row=6, column=0, columnspan=2, sticky="w", padx=10, pady=0)
val_STEP_SIZE_VALID.trace_add('write', update_step_size_entry_on_validation)

# standard xcorr entries
def update_max_lag_entry_on_validation_sxc(*args):
    max_lag_is_valid = val_MAX_LAG_VALID_SXC.get()
    if max_lag_is_valid:
        entry_max_lag_sxc.configure(border_color='#777777')
        error_label_max_lag_sxc.grid_forget()
    else:  
        entry_max_lag_sxc.configure(border_color='red')  
        error_label_max_lag_sxc.grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=0)
val_MAX_LAG_VALID_SXC.trace_add('write', update_max_lag_entry_on_validation_sxc)

# export buttons
def update_active_state_export_button(*args):
    button_export_data.configure(state="normal" if val_CORRELATION_SETTINGS_VALID.get() else "disabled")
    button_export_plot.configure(state="normal" if val_CORRELATION_SETTINGS_VALID.get() else "disabled")
val_CORRELATION_SETTINGS_VALID.trace_add('write', update_active_state_export_button)

# toggle parameter xroups (wxc/sxc)
def update_xcorr_parameter_groups(*args):
    wxc_is_active = val_checkbox_windowed_xcorr.get()
    if wxc_is_active:
        subgroup_windowed_xcorr_parameters.grid(row=7, column=0, columnspan=2, padx=0, pady=0)
        subgroup_standard_xcorr_parameters.grid_forget()
    else:
        subgroup_windowed_xcorr_parameters.grid_forget()
        subgroup_standard_xcorr_parameters.grid(row=7, column=0, columnspan=2, padx=0, pady=0, sticky='w')
val_checkbox_windowed_xcorr.trace_add('write', update_xcorr_parameter_groups)

# toggle vis group (only needed for wxc)
def update_vis_settings_group(*args):
    wxc_is_active = val_checkbox_windowed_xcorr.get()
    if wxc_is_active:
        label_vis_settings.grid(row=8, column=0, columnspan=2, pady=10)
        subgroup_vis_settings.grid(row=9, column=0, columnspan=2, padx=0, pady=0)    
    else:
        label_vis_settings.grid_forget()
        subgroup_vis_settings.grid_forget()
val_checkbox_windowed_xcorr.trace_add('write', update_vis_settings_group)

# file picker
def update_file_picker_label(*args):
    file_path = val_selected_file.get()
    label_file_picker.configure(text='No file selected.' if file_path == '' else os.path.basename(file_path))
val_selected_file.trace_add('write', update_file_picker_label)

# -----------
# CORRELATION
# -----------

# update windowed xcorr data
def _update_wxcorr_data():
    if not val_CORRELATION_SETTINGS_VALID.get():
        return
    # read data from data containers and state variables
    signal_a = dat_physiological_data["signal_a"]
    signal_b = dat_physiological_data["signal_b"]
    window_size = val_window_size.get()
    step_size = val_step_size.get()
    max_lag = val_max_lag.get()
    absolute_values = val_checkbox_absolute_corr.get()
    average_windows = val_checkbox_average_windows.get()

    # update correlation data
    dat_correlation_data['wxcorr'] = windowed_cross_correlation(signal_a, signal_b, window_size=window_size, step_size=step_size, max_lag=max_lag, absolute=absolute_values, average_windows=average_windows)

# uodate standard xcorr data
def _update_sxcorr_data():
    if not val_CORRELATION_SETTINGS_VALID_SXC.get():
        return

    # read data from data containers and state variabled
    signal_a = dat_physiological_data["signal_a"]
    signal_b = dat_physiological_data["signal_b"]
    max_lag = val_max_lag_sxc.get()
    absolute_values = val_checkbox_absolute_corr_sxc.get()
    dat_correlation_data['sxcorr'] = standard_cross_correlation(signal_a, signal_b, max_lag=max_lag, absolute=absolute_values)

# update correlation data
def update_corr():
    is_windowed_xcorr = val_checkbox_windowed_xcorr.get()
    if is_windowed_xcorr:
        _update_wxcorr_data()
    else:
        _update_sxcorr_data()
    

# --------
# PLOTTING
# --------

canvas = FigureCanvasTkAgg(dat_plot_data["fig"], master=group_plot)
def update_canvas():
    if not dat_plot_data["fig"]: return
    canvas.figure = dat_plot_data["fig"]
    canvas.draw()
    canvas.get_tk_widget().pack()

# update windowed xcorr plots
def _update_wxcorr_plots():
    if not val_CORRELATION_SETTINGS_VALID.get() or not dat_correlation_data['wxcorr']:
        return
    
    # read data from data containers and state variables
    signal_a = dat_physiological_data["signal_a"]
    signal_b = dat_physiological_data["signal_b"]
    window_size = val_window_size.get()
    step_size = val_step_size.get()
    max_lag = val_max_lag.get()
    windowed_xcorr_data = dat_correlation_data["wxcorr"]
    
    # create and store plot figure
    fig = plot_windowed_cross_correlation(windowed_xcorr_data, window_size, max_lag, step_size, signal_a, signal_b, use_win_center_tscl=val_checkbox_tscl_center.get())
    dat_plot_data["fig"] = fig

# update standard xcorr plots
def _update_sxcorr_plots():
    if not val_CORRELATION_SETTINGS_VALID_SXC.get() or not dat_correlation_data['sxcorr']:
        return

    # read data from data containers and state variabled
    signal_a = dat_physiological_data["signal_a"]
    signal_b = dat_physiological_data["signal_b"]
    xcorr_data = dat_correlation_data["sxcorr"]

    # create and store plot figure
    fig = plot_standard_cross_correlation(xcorr_data, signal_a, signal_b)
    dat_plot_data["fig"] = fig

def update_plot(*args):
    is_windowed_xcorr = val_checkbox_windowed_xcorr.get()
    if is_windowed_xcorr:
        _update_wxcorr_plots()
    else:
        _update_sxcorr_plots()

# -----------
# UPDATE LOOP
# -----------

def UPDATE(*args):
    update_corr()
    update_plot()
    update_canvas()
val_UPDATE_COUNT.trace_add('write', UPDATE)
UPDATE()

# ---------------
# TESTING HELPERS
# ---------------

def set_test_data():
    length = 1000
    dat_physiological_data["signal_a"] = np.sin(np.linspace(0, 5 * np.pi / 2, length))
    #dat_physiological_data["signal_b"] = np.cos(np.linspace(0, 4 * np.pi, length))
    dat_physiological_data["signal_b"] = dat_physiological_data["signal_a"] * 4*(np.random.random(length))
    val_data_length.set(length)

set_test_data()
UPDATE()

# ---
# RUN
# ---
app.mainloop()
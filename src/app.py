import customtkinter as tk

import state
import validation
import callbacks
import layout
import gui_updates
import corr_plot

# ------------------
# APP INITIALIZATION
# ------------------

tk.set_appearance_mode("Light")       # options: 'System', 'Light', 'Dark'
tk.set_default_color_theme("dark-blue")  # options: 'blue', 'green', 'dark-blue'

app = tk.CTk()
app.title("wx")

screen_width  = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()
screen_dpi    = app.winfo_fpixels('1i')

RETINA     = screen_dpi < 75
app_width  = min(2000, screen_width)
app_height = min(1200, screen_height)
app.geometry(f"{app_width}x{app_height}")
app.tk.call('tk', 'scaling', 1 if RETINA else 1.5)

# --------------------------------
# STATE — all tk.Vars & containers
# --------------------------------

state.init_state(screen_dpi, screen_width, screen_height, RETINA)

# --------------------------------
# VALIDATION & CALLBACKS
# --------------------------------

validate_numeric_input = validation.make_validator(app)
callbacks.setup_traces()

# --------------------------------
# BUILD UI
# --------------------------------

widget_dict = layout.build_layout(app, validate_numeric_input)

# --------------------------------
# REACTIVE GUI UPDATES
# --------------------------------

gui_updates.register_widgets(widget_dict)
gui_updates.setup_traces()

# --------------------------------
# CORRELATION & PLOTTING ENGINE
# --------------------------------

corr_plot.setup(widget_dict['group_plot'])
state.val_UPDATE_COUNT.trace_add('write', corr_plot.UPDATE)
corr_plot.UPDATE()

# --------------------------------
# CLEANUP & SHUTDOWN
# --------------------------------

def on_window_closing():
    for widget_id in list(app.after_info()):
        try:
            app.after_cancel(widget_id)
        except Exception:
            pass
    try:
        import matplotlib.pyplot as plt
        plt.close('all')
    except Exception:
        pass
    app.destroy()

app.protocol("WM_DELETE_WINDOW", on_window_closing)

# --------------------------------
# RUN
# --------------------------------

app.mainloop()

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

tk.set_appearance_mode("Light")
tk.set_default_color_theme("dark-blue")

app = tk.CTk()
app.title("wx")
app.withdraw()  # hide until fully built and sized

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

# Force Tk to resolve geometry and pack/grid layout so widget sizes are known,
# then size the figure to the actual canvas dimensions before showing the window.
app.update()
corr_plot.fit_canvas_to_container()

# --------------------------------
# CLEANUP & SHUTDOWN
# --------------------------------

def on_window_closing():
    for widget_id in app.tk.call('after', 'info'):
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

app.deiconify()  # show now — figure already sized correctly
app.mainloop()